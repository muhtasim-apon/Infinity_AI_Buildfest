"""Real-Postgres tests for migration 0002 (identity tables, RLS, users_guard trigger)."""

import os
import uuid

import psycopg
import pytest

OWNER = os.environ.get("TEST_SUPER_DATABASE_URL")
API = os.environ.get("TEST_API_DATABASE_URL")
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(not (OWNER and API), reason="database URLs not set"),
]

HASH = "$argon2id$v=19$m=65536,t=3,p=2$c29tZXNhbHQ$aGFzaA"
TOKEN = "a" * 64


def ctx(cur, uid="", role="", tenant=""):
    cur.execute("SET LOCAL ROLE cg_app")
    cur.execute(
        "SELECT set_config('app.user_id', %s, true), set_config('app.role', %s, true), "
        "set_config('app.tenant', %s, true)",
        (uid, role, tenant),
    )


@pytest.fixture
def api():
    with psycopg.connect(API, autocommit=False) as conn:
        yield conn
        conn.rollback()


def make_user(cur, *, tenant="real", role="FARMER", phone=None, email=None):
    uid = str(uuid.uuid4())
    if role in ("FARMER", "DEMO_FARMER"):
        phone = phone or f"+88017{uuid.uuid4().int % 10**8:08d}"
    else:
        email = email or f"{uid}@example.org"
    cur.execute(
        "INSERT INTO users (id, tenant_id, role, phone_e164, email, display_name, password_hash, status)"
        " VALUES (%s,%s,%s,%s,%s,'Test',%s,'ACTIVE')",
        (uid, tenant, role, phone, email, HASH),
    )
    return uid


def system(cur):
    ctx(cur, role="system", tenant="real")


def test_all_identity_tables_force_rls():
    with psycopg.connect(OWNER) as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT relname FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname='public' AND relkind='r' AND NOT (relrowsecurity AND relforcerowsecurity) "
            "AND relname <> 'alembic_version'"
        )
        assert cur.fetchall() == []


@pytest.mark.security
def test_no_context_cannot_read_or_insert_users(api):
    with api.cursor() as cur:
        system(cur)
        make_user(cur)
        ctx(cur)
        cur.execute("SELECT count(*) FROM users")
        assert cur.fetchone()[0] == 0
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            make_user(cur)


@pytest.mark.security
def test_user_sees_only_self_and_not_other_tenant(api):
    with api.cursor() as cur:
        system(cur)
        a = make_user(cur)
        make_user(cur)
        d = make_user(cur, tenant="demo", role="DEMO_FARMER")
        ctx(cur, uid=a, role="farmer", tenant="real")
        cur.execute("SELECT id::text FROM users")
        assert [r[0] for r in cur.fetchall()] == [a]
        ctx(cur, uid=d, role="farmer", tenant="demo")
        cur.execute("SELECT id::text FROM users")
        assert [r[0] for r in cur.fetchall()] == [d]


@pytest.mark.security
def test_admin_sees_own_tenant_only(api):
    with api.cursor() as cur:
        system(cur)
        admin = make_user(cur, role="ADMIN")
        make_user(cur)
        make_user(cur, tenant="demo", role="DEMO_FARMER")
        ctx(cur, uid=admin, role="admin", tenant="real")
        cur.execute("SELECT DISTINCT tenant_id FROM users")
        assert [r[0] for r in cur.fetchall()] == ["real"]


@pytest.mark.security
def test_mass_assignment_blocked_in_database(api):
    with api.cursor() as cur:
        system(cur)
        u = make_user(cur)
        ctx(cur, uid=u, role="farmer", tenant="real")
        cur.execute("UPDATE users SET display_name = 'New', locale = 'en' WHERE id = %s", (u,))
        assert cur.rowcount == 1
        changes = (
            ("role", "'ADMIN'"),
            ("status", "'SUSPENDED'"),
            ("failed_logins", "5"),
            ("email", "'x@example.org'"),
            ("tenant_id", "'demo'"),
        )
        for col, val in changes:
            cur.execute("SAVEPOINT s")
            with pytest.raises(
                (psycopg.errors.InsufficientPrivilege, psycopg.errors.CheckViolation)
            ):
                cur.execute(f"UPDATE users SET {col} = {val} WHERE id = %s", (u,))  # noqa: S608
            cur.execute("ROLLBACK TO SAVEPOINT s")


@pytest.mark.security
def test_credentials_tables_are_system_write_only(api):
    with api.cursor() as cur:
        system(cur)
        u = make_user(cur)
        cur.execute(
            "INSERT INTO sessions (tenant_id,user_id,token_hash,csrf_secret,expires_at,"
            "absolute_expires_at) VALUES ('real',%s,%s,%s,now()+interval '1 hour',"
            "now()+interval '1 hour')",
            (u, TOKEN, "c" * 40),
        )
        cur.execute(
            "INSERT INTO otp_codes (tenant_id,user_id,purpose,code_hmac,expires_at)"
            " VALUES ('real',%s,'login',%s,now()+interval '5 minutes')",
            (u, TOKEN),
        )
        ctx(cur, uid=u, role="farmer", tenant="real")
        cur.execute("SELECT count(*) FROM sessions")
        assert cur.fetchone()[0] == 1  # may list their own sessions
        cur.execute("SELECT count(*) FROM otp_codes")
        assert cur.fetchone()[0] == 1
        for sql in (
            "UPDATE sessions SET revoked_at = now()",
            "DELETE FROM sessions",
        ):
            cur.execute("SAVEPOINT s")
            cur.execute(sql)
            assert cur.rowcount == 0  # USING (is_system()) hides every row: nothing changed
            cur.execute("ROLLBACK TO SAVEPOINT s")
        with pytest.raises(psycopg.errors.InsufficientPrivilege):
            cur.execute(
                "INSERT INTO sessions (tenant_id,user_id,token_hash,csrf_secret,expires_at,"
                "absolute_expires_at) VALUES ('real',%s,%s,%s,now(),now())",
                (u, "b" * 64, "c" * 40),
            )


@pytest.mark.security
def test_other_users_rows_invisible_and_outbox_is_system_only(api):
    with api.cursor() as cur:
        system(cur)
        a = make_user(cur)
        b = make_user(cur)
        cur.execute(
            "INSERT INTO consents (tenant_id,user_id,purpose,granted,text_version) "
            "VALUES ('real',%s,'service',true,'consent-v1')",
            (a,),
        )
        cur.execute(
            "INSERT INTO email_outbox (tenant_id,to_email,kind,subject,body_text,body_html) "
            "VALUES ('real','a@example.org','verify','s','t','h')"
        )
        ctx(cur, uid=b, role="farmer", tenant="real")
        cur.execute("SELECT count(*) FROM consents")
        assert cur.fetchone()[0] == 0
        cur.execute("SELECT count(*) FROM email_outbox")
        assert cur.fetchone()[0] == 0
        ctx(cur, uid=b, role="admin", tenant="real")
        cur.execute("SELECT count(*) FROM email_outbox")
        assert cur.fetchone()[0] == 0  # not even admins read one-time links


BAD_ROWS = [
    "INSERT INTO users (role,tenant_id,phone_e164,display_name) "
    "VALUES ('FARMER','demo','+8801711111111','x')",
    "INSERT INTO users (role,tenant_id,display_name) VALUES ('FARMER','real','x')",
    "INSERT INTO users (role,tenant_id,display_name) VALUES ('ADMIN','real','x')",
    "INSERT INTO users (role,tenant_id,phone_e164,display_name) "
    "VALUES ('FARMER','real','12345','x')",
    "INSERT INTO users (role,tenant_id,phone_e164,display_name,password_hash) "
    "VALUES ('FARMER','real','+8801711111112','x','plaintext')",
]


@pytest.mark.parametrize("sql", BAD_ROWS)
def test_check_constraints_reject_bad_rows(sql):
    with psycopg.connect(OWNER) as conn, conn.cursor() as cur:
        with pytest.raises(psycopg.errors.CheckViolation):
            cur.execute(sql)
        conn.rollback()


def test_notification_links_must_be_in_app_paths():
    with psycopg.connect(OWNER) as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO users (role,tenant_id,phone_e164,display_name) "
            "VALUES ('FARMER','real','+8801733333333','x') RETURNING id"
        )
        uid = cur.fetchone()[0]
        for good in ("/alerts", "/", "/scans/1?x=1"):
            cur.execute(
                "INSERT INTO notifications (user_id,kind,link_path) VALUES (%s,'k',%s)", (uid, good)
            )
        for bad in ("//evil.example", "https://evil.example", "/\\evil", "javascript:alert(1)"):
            cur.execute("SAVEPOINT s")
            with pytest.raises(psycopg.errors.CheckViolation):
                cur.execute(
                    "INSERT INTO notifications (user_id,kind,link_path) VALUES (%s,'k',%s)",
                    (uid, bad),
                )
            cur.execute("ROLLBACK TO SAVEPOINT s")
        conn.rollback()
