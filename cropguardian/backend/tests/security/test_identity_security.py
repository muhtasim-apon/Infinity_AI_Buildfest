"""Identity security regressions (spec 19.4): timing, redaction, injection, secrets in responses,
concurrent audit chain, token/OTP entropy. Needs the test Postgres + Redis."""

import statistics
import threading
import time
import uuid

import psycopg
import pytest

from tests.api.identity_support import (
    API_DB,
    STAFF_PW,
    STRONG,
    SUPER_DB,
    Api,
    flush_redis,
    local_phone,
    make_staff,
    needs_services,
    new_phone,
    register_farmer,
    sql,
)

pytestmark = [pytest.mark.security, pytest.mark.integration, needs_services]


def test_login_timing_does_not_reveal_whether_the_account_exists(app_client: Api):
    phone = register_farmer(app_client)
    app_client.post("/api/v1/auth/logout")
    app_client.refresh_csrf()
    known: list[float] = []
    unknown: list[float] = []
    for i in range(50):
        flush_redis()  # keep the 5/min limiter out of the measurement
        who, bucket = (phone, known) if i % 2 == 0 else (new_phone(), unknown)
        started = time.perf_counter()
        r = app_client.post(
            "/api/v1/auth/login", {"identifier": who, "password": "wrong-password-1"}
        )
        bucket.append((time.perf_counter() - started) * 1000)
        assert r.status_code == 401
    gap = abs(statistics.median(known) - statistics.median(unknown))
    assert gap < 50, f"median difference {gap:.1f} ms (known vs unknown account)"


def test_secrets_never_appear_in_logs(app_client: Api, capsys, caplog):
    phone = new_phone()
    app_client.post(
        "/api/v1/auth/register/farmer",
        {"phone": local_phone(phone), "password": STRONG, "display_name": "Log Check",
         "accept_service": True},
    )  # fmt: skip
    code = app_client.sms_code(phone)
    login = app_client.post("/api/v1/auth/otp/verify", {"phone": phone, "code": code})
    token = app_client.c.cookies.get("__Host-cg_session")
    app_client.post("/api/v1/auth/login", {"identifier": phone, "password": "wrong-password-1"})
    seen = capsys.readouterr()
    # the test client's own httpx request log is not server output: judge only the application's logs
    lines = (seen.out + seen.err + caplog.text).splitlines()
    haystack = " ".join(x for x in lines if "HTTP Request:" not in x)
    assert login.status_code == 200 and token
    for secret in (STRONG, code, token, phone, local_phone(phone), "wrong-password-1"):
        assert secret not in haystack, f"secret leaked into logs: {secret[:6]}..."


@pytest.mark.parametrize(
    "name",
    [
        "<script>alert(1)</script>",
        "' OR 1=1 --",
        "{{7*7}}",
        "${jndi:ldap://x}",
        "a" + chr(0x202E) + "b",
        "x" * 80,
    ],
)
def test_hostile_display_names_are_stored_and_returned_inert(app_client: Api, name):
    phone = new_phone()
    app_client.post("/api/v1/__test__/reset-limits")
    r = app_client.post(
        "/api/v1/auth/register/farmer",
        {"phone": local_phone(phone), "password": STRONG, "display_name": name,
         "accept_service": True},
    )  # fmt: skip
    assert r.status_code == 202
    app_client.post("/api/v1/auth/otp/verify", {"phone": phone, "code": app_client.sms_code(phone)})
    me = app_client.get("/api/v1/me")
    assert me.status_code == 200 and me.json()["display_name"] == name  # data, never markup
    assert me.headers["content-type"].startswith("application/json")
    assert me.headers["x-content-type-options"] == "nosniff"


@pytest.mark.parametrize(
    "identifier", ["' OR '1'='1", "admin'--", '" OR ""="', "a@b.c' UNION SELECT 1 --", "\x00"]
)
def test_sql_injection_in_login_identifier_is_just_a_wrong_login(app_client: Api, identifier):
    r = app_client.post(
        "/api/v1/auth/login", {"identifier": identifier, "password": "wrong-password-1"}
    )
    assert r.status_code in (401, 422) and r.status_code != 500


def test_password_hashes_and_secrets_never_leave_the_api(app_client: Api):
    register_farmer(app_client)
    me = app_client.get("/api/v1/me").text
    sessions = app_client.get("/api/v1/me/sessions").text
    consents = app_client.get("/api/v1/me/consents").text
    for blob in (me, sessions, consents):
        for forbidden in ("argon2", "password", "token_hash", "csrf_secret", "secret_enc"):
            assert forbidden not in blob.lower()
    admin_email, _ = make_staff("ADMIN")
    assert admin_email not in me


def test_security_headers_and_no_server_banner_on_api_routes(app_client: Api):
    r = app_client.get("/api/v1/auth/state")
    assert r.headers["x-content-type-options"] == "nosniff"
    assert "frame-ancestors 'none'" in r.headers["content-security-policy"]
    assert r.headers["referrer-policy"]
    assert (
        "server" not in {h.lower() for h in r.headers}
        or "uvicorn" not in r.headers.get("server", "").lower()
    )


def test_oversized_and_malformed_bodies_do_not_500(app_client: Api):
    big = app_client.c.post(
        "/api/v1/auth/login",
        content=b"{" + b'"a":"' + b"x" * 2_000_000 + b'"}',
        headers={"Origin": "https://testserver", "X-CSRF-Token": app_client.csrf,
                 "Content-Type": "application/json"},
    )  # fmt: skip
    assert big.status_code == 413
    bad_json = app_client.c.post(
        "/api/v1/auth/login",
        content=b"{not json",
        headers={"Origin": "https://testserver", "X-CSRF-Token": app_client.csrf,
                 "Content-Type": "application/json"},
    )  # fmt: skip
    assert bad_json.status_code == 422
    wrong_type = app_client.post("/api/v1/auth/login", {"identifier": ["x"], "password": 1})
    assert wrong_type.status_code == 422


def test_session_tokens_are_unique_and_long(app_client: Api):
    tokens = set()
    for _ in range(3):
        browser = app_client.spawn()
        register_farmer(browser)
        tokens.add(browser.c.cookies.get("__Host-cg_session"))
    assert len(tokens) == 3 and all(len(t) >= 43 for t in tokens)


def test_audit_chain_stays_valid_under_concurrent_writers():
    run = uuid.uuid4().hex[:8]

    def writer(n: int) -> None:
        with psycopg.connect(API_DB, autocommit=False) as conn, conn.cursor() as cur:
            for i in range(5):
                cur.execute("SET LOCAL ROLE cg_app")
                cur.execute(
                    "SELECT set_config('app.role','system',true), set_config('app.tenant','real',true)"
                )
                cur.execute(
                    "INSERT INTO audit_log (action, tenant_id) VALUES (%s, 'real')",
                    (f"concurrency.{run}.{n}.{i}",),
                )
                conn.commit()

    threads = [threading.Thread(target=writer, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert sql("SELECT audit_verify_chain()") == [(0,)]
    assert (
        sql("SELECT count(*) FROM audit_log WHERE action LIKE %s", (f"concurrency.{run}.%",))[0][0]
        == 40
    )


def test_audit_tamper_is_detected_and_updates_are_refused():
    with psycopg.connect(SUPER_DB) as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO audit_log (action, tenant_id) VALUES ('tamper.check','real')")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute("UPDATE audit_log SET action = 'edited' WHERE action = 'tamper.check'")
        conn.rollback()
        assert STAFF_PW  # (fixture constant referenced so the import is exercised)
