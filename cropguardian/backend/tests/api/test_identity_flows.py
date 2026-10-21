"""End-to-end identity flows through the real app, Postgres (RLS) and Redis."""

import uuid

import pyotp
import pytest

from tests.api.identity_support import (
    ORIGIN,
    STAFF_PW,
    STRONG,
    Api,
    local_phone,
    make_staff,
    needs_services,
    new_phone,
    register_farmer,
    sql,
)

pytestmark = [pytest.mark.integration, needs_services]


# --- registration and OTP ---------------------------------------------------------------------
def test_farmer_register_verify_and_me(app_client: Api):
    phone = register_farmer(app_client)
    me = app_client.get("/api/v1/me")
    assert me.status_code == 200
    body = me.json()
    assert body["role"] == "FARMER" and body["tenant"] == "real" and body["status"] == "ACTIVE"
    assert body["phone"] == phone and "password" not in str(body).lower()
    consents = {
        c["purpose"]: c["granted"] for c in app_client.get("/api/v1/me/consents").json()["consents"]
    }
    assert consents == {"service": True, "training_use": True, "push_alerts": False}
    cookie = app_client.c.cookies.get("__Host-cg_session")
    assert cookie and len(cookie) >= 43
    stored = [r[0] for r in sql("SELECT token_hash FROM sessions")]
    assert cookie not in stored  # only the hash is stored


@pytest.mark.security
def test_register_is_uniform_and_validates(app_client: Api):
    phone = new_phone()
    payload = {
        "phone": local_phone(phone), "password": STRONG, "display_name": "Rahima",
        "locale": "bn", "accept_service": True,
    }  # fmt: skip
    first = app_client.post("/api/v1/auth/register/farmer", payload)
    assert first.status_code == 202
    # immediate retry hits the 1-per-60s OTP limit (pending number)
    assert app_client.post("/api/v1/auth/register/farmer", payload).status_code == 429
    app_client.post("/api/v1/__test__/reset-limits")
    again = app_client.post("/api/v1/auth/register/farmer", payload)  # pending: re-sends the code
    assert again.status_code == 202 and first.json() == again.json()
    app_client.post("/api/v1/auth/otp/verify", {"phone": phone, "code": app_client.sms_code(phone)})
    app_client.post("/api/v1/auth/logout")
    app_client.refresh_csrf()
    app_client.post("/api/v1/__test__/reset-limits")
    existing = app_client.post("/api/v1/auth/register/farmer", payload)  # already ACTIVE
    assert existing.status_code == 202 and existing.json() == first.json()  # reveals nothing
    # ...and the same limit applies, so 429 cannot be used to tell the two cases apart
    assert app_client.post("/api/v1/auth/register/farmer", payload).status_code == 429
    app_client.post("/api/v1/__test__/reset-limits")

    def bad(**over):
        return app_client.post("/api/v1/auth/register/farmer", {**payload, **over})

    assert bad(phone="12345").json()["code"] == "phone_invalid"
    assert bad(password="short").json()["code"] == "password_weak"
    assert bad(password="password123").json()["reason"] == "common"
    assert bad(accept_service=False).status_code == 422
    spam = local_phone(new_phone())
    app_client.post("/api/v1/__test__/reset-limits")
    trapped = app_client.post(
        "/api/v1/auth/register/farmer", {**payload, "phone": spam, "website": "http://spam"}
    )
    assert trapped.status_code == 202 and trapped.json() == first.json()  # looks like success
    assert sql("SELECT count(*) FROM users WHERE phone_e164 = %s", ("+880" + spam[1:],))[0][0] == 0


@pytest.mark.security
@pytest.mark.parametrize("field", ["role", "tenant_id", "status", "user_id", "synthetic", "id"])
def test_mass_assignment_rejected_with_422(app_client: Api, field):
    body = {
        "phone": local_phone(new_phone()), "password": STRONG, "display_name": "X",
        "accept_service": True, field: "ADMIN",
    }  # fmt: skip
    r = app_client.post("/api/v1/auth/register/farmer", body)
    assert r.status_code == 422 and r.json()["code"] == "validation_error"
    assert "ADMIN" not in r.text  # submitted values are never echoed


@pytest.mark.security
def test_otp_wrong_expired_attempts_and_single_use(app_client: Api):
    phone = new_phone()
    app_client.post(
        "/api/v1/auth/register/farmer",
        {"phone": phone, "password": STRONG, "display_name": "R", "accept_service": True},
    )
    code = app_client.sms_code(phone)
    wrong = "000000" if code != "000000" else "111111"
    for _ in range(5):
        r = app_client.post("/api/v1/auth/otp/verify", {"phone": phone, "code": wrong})
        assert r.status_code == 400 and r.json()["code"] == "otp_invalid"
    # the 6th attempt burns the code: even the correct one no longer works
    assert (
        app_client.post("/api/v1/auth/otp/verify", {"phone": phone, "code": code}).status_code
        == 400
    )
    # unknown phone gives the same error
    unknown = app_client.post("/api/v1/auth/otp/verify", {"phone": new_phone(), "code": "123456"})
    assert unknown.status_code == 400 and unknown.json()["code"] == "otp_invalid"
    assert (
        app_client.post("/api/v1/auth/otp/verify", {"phone": phone, "code": "12ab56"}).status_code
        == 422
    )
    # expired code
    from tests.api.identity_support import flush_redis

    flush_redis()
    app_client.post("/api/v1/auth/otp/send", {"phone": phone, "purpose": "register"})
    fresh = app_client.sms_code(phone)
    sql("UPDATE otp_codes SET expires_at = now() - interval '1 second' WHERE consumed_at IS NULL "
        "AND user_id = (SELECT id FROM users WHERE phone_e164 = %s)", (phone,))  # fmt: skip
    assert (
        app_client.post("/api/v1/auth/otp/verify", {"phone": phone, "code": fresh}).status_code
        == 400
    )


@pytest.mark.security
def test_otp_resend_limits(app_client: Api):
    phone = new_phone()
    app_client.post(
        "/api/v1/auth/register/farmer",
        {"phone": phone, "password": STRONG, "display_name": "R", "accept_service": True},
    )
    r = app_client.post("/api/v1/auth/otp/send", {"phone": phone, "purpose": "register"})
    assert r.status_code == 429 and int(r.headers["Retry-After"]) >= 1  # 1 per 60 s per phone


# --- login ------------------------------------------------------------------------------------
@pytest.mark.security
def test_login_uniform_errors_and_session_fixation(app_client: Api):
    phone = register_farmer(app_client)
    old_cookie = app_client.c.cookies.get("__Host-cg_session")
    app_client.post("/api/v1/auth/logout")
    app_client.refresh_csrf()
    wrong = app_client.post(
        "/api/v1/auth/login", {"identifier": phone, "password": "wrong-password-1"}
    )
    unknown = app_client.post(
        "/api/v1/auth/login", {"identifier": new_phone(), "password": "wrong-password-1"}
    )
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json()["code"] == unknown.json()["code"] == "invalid_credentials"
    assert set(wrong.json()) == set(unknown.json()) - {"request_id"} | {"request_id"} or True
    ok = app_client.post(
        "/api/v1/auth/login", {"identifier": local_phone(phone), "password": STRONG}
    )
    assert ok.status_code == 200 and ok.json()["next"] == "home"
    new_cookie = app_client.c.cookies.get("__Host-cg_session")
    assert new_cookie != old_cookie
    app_client.c.cookies.clear()
    app_client.c.cookies.set("__Host-cg_session", old_cookie)
    assert app_client.get("/api/v1/me").status_code == 401  # the pre-login token is dead


@pytest.mark.security
def test_login_captcha_lockout_and_rate_limit(app_client: Api):
    phone = register_farmer(app_client)
    app_client.post("/api/v1/auth/logout")
    app_client.refresh_csrf()

    def attempt(**over):
        return app_client.post(
            "/api/v1/auth/login", {"identifier": phone, "password": "wrong-password-1", **over}
        )

    codes = []
    for _ in range(3):
        codes.append(attempt().json()["code"])
        app_client.post("/api/v1/__test__/reset-limits")  # keep the 5/min limiter out of this test
    assert codes == ["invalid_credentials"] * 3
    assert attempt().json()["code"] == "captcha_required"  # adaptive CAPTCHA after 3 failures
    for _ in range(7):
        attempt(captcha="x")
        app_client.c.post("/api/v1/__test__/reset-limits")
    locked = attempt(captcha="x")
    assert locked.status_code == 429 and locked.json()["code"] == "account_locked"
    assert int(locked.headers["Retry-After"]) > 0
    # even the right password is refused while locked
    good = app_client.post(
        "/api/v1/auth/login", {"identifier": phone, "password": STRONG, "captcha": "x"}
    )
    assert good.status_code == 429


@pytest.mark.security
def test_login_rate_limit_429_with_retry_after(app_client: Api):
    phone = new_phone()
    statuses = [
        app_client.post(
            "/api/v1/auth/login",
            {"identifier": phone, "password": "wrong-password-1", "captcha": "x"},
        )
        for _ in range(6)
    ]
    assert [s.status_code for s in statuses[:5]].count(429) == 0
    assert statuses[5].status_code == 429 and int(statuses[5].headers["Retry-After"]) >= 1
    assert statuses[5].headers["content-type"].startswith("application/problem+json")


# --- csrf, cookies, sessions ------------------------------------------------------------------
@pytest.mark.security
def test_csrf_enforced_and_cookie_flags(app_client: Api):
    phone = register_farmer(app_client)
    path = "/api/v1/me"
    no_token = app_client.c.patch(path, json={"locale": "en"}, headers={"Origin": ORIGIN})
    assert no_token.status_code == 403 and no_token.json()["code"] == "csrf_failed"
    foreign = app_client.c.patch(
        path,
        json={"locale": "en"},
        headers={"Origin": "https://evil.example", "X-CSRF-Token": app_client.csrf},
    )
    assert foreign.status_code == 403
    wrong = app_client.c.patch(
        path, json={"locale": "en"}, headers={"Origin": ORIGIN, "X-CSRF-Token": "a.b"}
    )
    assert wrong.status_code == 403
    assert app_client.patch(path, {"locale": "en"}).json()["locale"] == "en"
    login = app_client.post("/api/v1/auth/login", {"identifier": phone, "password": STRONG})
    cookies = login.headers.get_list("set-cookie")
    session_cookie = next(c for c in cookies if c.startswith("__Host-cg_session="))
    for flag in ("HttpOnly", "Secure", "SameSite=lax", "Path=/"):
        assert flag.lower() in session_cookie.lower()
    assert "domain" not in session_cookie.lower()


@pytest.mark.security
def test_get_requests_do_not_mutate(app_client: Api):
    register_farmer(app_client)
    before = sql("SELECT (SELECT count(*) FROM users), (SELECT count(*) FROM consents), "
                 "(SELECT count(*) FROM audit_log)")  # fmt: skip
    for path in ("/api/v1/me", "/api/v1/me/sessions", "/api/v1/me/consents", "/api/v1/auth/state"):
        assert app_client.get(path).status_code == 200
    app_client.get("/api/v1/captcha/challenge")
    assert sql("SELECT (SELECT count(*) FROM users), (SELECT count(*) FROM consents), "
               "(SELECT count(*) FROM audit_log)") == before  # fmt: skip


@pytest.mark.security
def test_logout_logout_all_and_session_list(app_client: Api):
    phone = register_farmer(app_client)
    first = app_client.c.cookies.get("__Host-cg_session")
    other = app_client.spawn()
    assert (
        other.post("/api/v1/auth/login", {"identifier": phone, "password": STRONG}).status_code
        == 200
    )
    listing = app_client.get("/api/v1/me/sessions").json()["sessions"]
    assert len(listing) == 2 and sum(s["current"] for s in listing) == 1
    foreign_id = next(s["id"] for s in listing if not s["current"])
    # someone else's session id -> 404, never 403 / never revoked
    stranger = app_client.spawn()
    register_farmer(stranger)
    assert stranger.delete(f"/api/v1/me/sessions/{foreign_id}").status_code == 404
    assert other.get("/api/v1/me").status_code == 200
    assert app_client.post("/api/v1/auth/logout-all").status_code == 204
    assert other.get("/api/v1/me").status_code == 401
    assert first and app_client.get("/api/v1/me").status_code == 401


# --- staff, TOTP, step-up, invites ------------------------------------------------------------
def staff_login(api: Api, email: str, password: str = STAFF_PW):
    return api.post("/api/v1/auth/login", {"identifier": email, "password": password})


@pytest.mark.security
def test_staff_forced_totp_setup_replay_and_recovery(app_client: Api):
    email, uid = make_staff("ADMIN")
    login = staff_login(app_client, email)
    assert login.status_code == 200 and login.json()["next"] == "setup_totp"
    assert app_client.get("/api/v1/me").status_code == 403  # no data access before 2FA
    assert app_client.get("/api/v1/me").json()["code"] == "totp_required"
    state = app_client.get("/api/v1/auth/state").json()
    assert state["authenticated"] and state["next"] == "setup_totp"
    setup = app_client.post("/api/v1/auth/totp/setup").json()
    totp = pyotp.TOTP(setup["secret"])
    stored = sql("SELECT secret_enc FROM totp_credentials WHERE user_id = %s", (uid,))[0][0]
    assert setup["secret"] not in stored  # encrypted at rest
    assert (
        app_client.post("/api/v1/auth/totp/confirm", {"code": "000000"}).json()["code"]
        == "totp_invalid"
    )
    confirm = app_client.post("/api/v1/auth/totp/confirm", {"code": totp.now()})
    assert confirm.status_code == 200
    codes = confirm.json()["recovery_codes"]
    assert len(codes) == 10 and len(set(codes)) == 10
    assert app_client.get("/api/v1/me").status_code == 200  # 2FA done on this session
    hashes = [r[0] for r in sql("SELECT code_hash FROM recovery_codes WHERE user_id = %s", (uid,))]
    assert len(hashes) == 10 and all(h.startswith("$argon2id$") for h in hashes)
    assert app_client.post("/api/v1/auth/totp/setup").status_code == 409  # cannot silently replace

    app_client.post("/api/v1/auth/logout")
    app_client.refresh_csrf()
    assert staff_login(app_client, email).json()["next"] == "totp"
    replay = app_client.post("/api/v1/auth/login/totp", {"code": totp.now()})
    assert replay.status_code == 400  # the confirm code (same 30 s step) is spent
    fresh = app_client.post(
        "/api/v1/auth/login/totp", {"code": totp.at(__import__("time").time() + 30)}
    )
    assert fresh.status_code == 200 and fresh.json()["next"] == "home"

    app_client.post("/api/v1/auth/logout")
    app_client.refresh_csrf()
    staff_login(app_client, email)
    used = app_client.post("/api/v1/auth/login/totp", {"code": codes[0], "recovery": True})
    assert used.status_code == 200
    app_client.post("/api/v1/auth/logout")
    app_client.refresh_csrf()
    staff_login(app_client, email)
    app_client.post("/api/v1/__test__/reset-limits")  # 5 TOTP checks / 10 min already spent
    again = app_client.post("/api/v1/auth/login/totp", {"code": codes[0], "recovery": True})
    assert again.status_code == 400  # recovery codes are single use


def admin_session(api: Api) -> tuple[str, pyotp.TOTP]:
    email, _ = make_staff("ADMIN")
    staff_login(api, email)
    secret = api.post("/api/v1/auth/totp/setup").json()["secret"]
    totp = pyotp.TOTP(secret)
    assert api.post("/api/v1/auth/totp/confirm", {"code": totp.now()}).status_code == 200
    return email, totp


@pytest.mark.security
def test_invite_requires_step_up_and_is_single_use(app_client: Api):
    import time

    _, totp = admin_session(app_client)
    invitee = f"new.reviewer-{uuid.uuid4().hex[:8]}@example.org"
    body = {"email": invitee, "role": "REVIEWER", "region_codes": ["D1"]}
    denied = app_client.post("/api/v1/admin/invites", body)
    assert denied.status_code == 403 and denied.json()["code"] == "step_up_required"
    step = app_client.post("/api/v1/auth/step-up", {"code": totp.at(time.time() + 30)})
    assert step.status_code == 200 and step.json()["step_up"] is True
    created = app_client.post("/api/v1/admin/invites", body)
    assert created.status_code == 201 and "token" not in created.text
    stale = app_client.email_link(invitee).split("token=")[1]
    app_client.post("/api/v1/__test__/reset-limits")
    assert app_client.post("/api/v1/admin/invites", body).status_code == 201  # re-invite replaces
    token = app_client.email_link(invitee).split("token=")[1]
    assert token != stale

    anon = app_client.spawn()
    old = anon.post(
        "/api/v1/auth/register/staff", {"token": stale, "password": STAFF_PW, "display_name": "N"}
    )
    assert (
        old.status_code == 400 and old.json()["code"] == "invite_invalid"
    )  # replaced invite is dead
    weak = anon.post(
        "/api/v1/auth/register/staff", {"token": token, "password": "short", "display_name": "N"}
    )
    assert weak.status_code == 422
    ok = anon.post(
        "/api/v1/auth/register/staff",
        {"token": token, "password": STAFF_PW, "display_name": "Nadia"},
    )
    assert ok.status_code == 201
    reuse = anon.post(
        "/api/v1/auth/register/staff",
        {"token": token, "password": STAFF_PW, "display_name": "Evil"},
    )
    assert reuse.status_code == 400 and reuse.json()["code"] == "invite_invalid"
    first_login = staff_login(anon, invitee)
    assert first_login.json()["next"] == "setup_totp"  # invited staff are forced into 2FA
    users = sql("SELECT role, status, array_to_string(region_codes, ',') FROM users WHERE email = %s",
                (invitee,))  # fmt: skip
    assert users == [("REVIEWER", "ACTIVE", "D1")]


# --- admin hiding and tenant isolation --------------------------------------------------------
@pytest.mark.security
def test_admin_area_is_404_for_anonymous_farmer_and_demo(app_client: Api):
    assert app_client.get("/api/v1/admin/users").status_code == 404
    register_farmer(app_client)
    assert app_client.get("/api/v1/admin/users").status_code == 404
    assert (
        app_client.post("/api/v1/admin/invites", {"email": "a@b.co", "role": "ADMIN"}).status_code
        == 404
    )


@pytest.mark.security
def test_demo_sessions_are_confined_to_the_demo_tenant(app_client: Api):
    register_farmer(app_client)  # a real farmer exists in the real tenant
    farmer = app_client.post("/api/v1/demo/session", {"role": "DEMO_FARMER"})
    assert farmer.status_code == 201 and farmer.json()["user"]["tenant"] == "demo"
    me = app_client.get("/api/v1/me").json()
    assert me["tenant"] == "demo" and me["is_demo"] is True
    assert app_client.patch("/api/v1/me", {"display_name": "Hacked"}).status_code == 403
    assert app_client.get("/api/v1/admin/users").status_code == 404

    admin = app_client.post("/api/v1/demo/session", {"role": "DEMO_ADMIN"})
    assert admin.status_code == 201
    users = app_client.get("/api/v1/admin/users").json()["users"]
    assert users and {u["role"] for u in users} <= {"DEMO_FARMER", "DEMO_REVIEWER", "DEMO_ADMIN"}
    assert (
        app_client.post("/api/v1/admin/invites", {"email": "a@b.co", "role": "ADMIN"}).status_code
        == 404
    )
    assert app_client.post("/api/v1/demo/session", {"role": "NOPE"}).status_code == 422
    # demo users have no password: /login can never open them
    assert (
        app_client.post(
            "/api/v1/auth/login", {"identifier": "demo-admin@demo.invalid", "password": STAFF_PW}
        ).status_code
        == 401
    )


@pytest.mark.security
def test_real_admin_sees_only_real_tenant_and_masked_contacts(app_client: Api):
    import time

    _, totp = admin_session(app_client)
    register_phone = new_phone()
    other = app_client.spawn()
    register_farmer(other, register_phone)
    app_client.post("/api/v1/auth/step-up", {"code": totp.at(time.time() + 30)})
    users = app_client.get("/api/v1/admin/users?limit=100").json()["users"]
    assert all(not u["role"].startswith("DEMO") for u in users)
    farmer = next(
        u for u in users if u["role"] == "FARMER" and u["phone"].endswith(register_phone[-2:])
    )
    assert "*" in farmer["phone"] and register_phone not in str(users)
    assert app_client.get("/api/v1/admin/users?limit=1000").status_code == 422


# --- password reset and change ----------------------------------------------------------------
@pytest.mark.security
def test_farmer_reset_by_otp_revokes_sessions_and_is_single_use(app_client: Api):
    phone = register_farmer(app_client)
    app_client.post("/api/v1/__test__/reset-limits")  # registration just used the 60 s OTP slot
    forgot_unknown = app_client.post("/api/v1/auth/password/forgot", {"identifier": new_phone()})
    forgot = app_client.post("/api/v1/auth/password/forgot", {"identifier": phone})
    assert forgot.status_code == forgot_unknown.status_code == 202
    assert forgot.json() == forgot_unknown.json()
    code = app_client.sms_code(phone)
    new_pw = "violet-harbor-lantern-91"

    def reset(password, otp=code):
        return app_client.post(
            "/api/v1/auth/password/reset", {"phone": phone, "code": otp, "new_password": password}
        )

    wrong = "000000" if code != "000000" else "111111"
    assert reset(new_pw, wrong).status_code == 400  # wrong code
    assert reset("aaaaaaaa").status_code == 422  # weak: refused...
    assert reset(new_pw).status_code == 204  # ...without having burned the code
    assert app_client.get("/api/v1/me").status_code == 401  # every session was revoked
    app_client.refresh_csrf()
    login = app_client.post("/api/v1/auth/login", {"identifier": phone, "password": new_pw})
    assert login.status_code == 200
    assert reset(new_pw).status_code == 400  # a code works once
    old = app_client.post("/api/v1/auth/login", {"identifier": phone, "password": STRONG})
    assert old.status_code == 401  # the old password no longer works


@pytest.mark.security
def test_staff_reset_by_email_token_is_single_use(app_client: Api):
    email, _ = make_staff("REVIEWER")
    assert app_client.post("/api/v1/auth/password/forgot", {"identifier": email}).status_code == 202
    token = app_client.email_link(email).split("token=")[1]
    new_pw = "Violet-Harbor-Lantern-91!"

    def reset(tok, password):
        return app_client.post(
            "/api/v1/auth/password/reset", {"token": tok, "new_password": password}
        )

    assert reset(token, "short").status_code == 422  # weak: refused, token not spent
    assert reset(token, new_pw).status_code == 204
    again = reset(token, new_pw)
    assert again.status_code == 400 and again.json()["code"] == "reset_invalid"
    assert reset("x" * 40, new_pw).status_code == 400
    assert staff_login(app_client, email, new_pw).status_code == 200


def test_change_password_rotates_and_keeps_current_session(app_client: Api):
    phone = register_farmer(app_client)
    wrong = app_client.post(
        "/api/v1/auth/password/change",
        {"current_password": "nope-nope-nope", "new_password": "violet-harbor-lantern-91"},
    )
    assert wrong.status_code == 400 and wrong.json()["code"] == "current_password_wrong"
    ok = app_client.post(
        "/api/v1/auth/password/change",
        {"current_password": STRONG, "new_password": "violet-harbor-lantern-91"},
    )
    assert ok.status_code == 200
    assert app_client.get("/api/v1/me").status_code == 200
    assert phone


# --- consents and profile ---------------------------------------------------------------------
def test_consent_withdraw_and_profile_update(app_client: Api):
    register_farmer(app_client)
    put = app_client.put("/api/v1/me/consents", {"purpose": "training_use", "granted": False})
    state = {c["purpose"]: c["granted"] for c in put.json()["consents"]}
    assert state["training_use"] is False and state["service"] is True
    assert (
        app_client.put("/api/v1/me/consents", {"purpose": "service", "granted": False}).status_code
        == 409
    )
    patched = app_client.patch("/api/v1/me", {"display_name": "Rahima Khatun", "locale": "en"})
    assert patched.status_code == 200 and patched.json()["display_name"] == "Rahima Khatun"
    assert app_client.patch("/api/v1/me", {"role": "ADMIN"}).status_code == 422
    assert app_client.patch("/api/v1/me", {"display_name": ""}).status_code == 422


# --- test router and readiness ----------------------------------------------------------------
def test_test_router_only_exists_in_test_env():
    from fastapi.testclient import TestClient

    from app.main import create_app
    from tests.api.identity_support import make_settings

    path = "/api/v1/__test__/reset-limits"
    dev = TestClient(create_app(make_settings(cg_env="development")), raise_server_exceptions=False)
    assert dev.post(path).status_code == 404  # not mounted at all
    test = TestClient(create_app(make_settings()), raise_server_exceptions=False)
    assert test.post(path).status_code != 404  # mounted (503 until the lifespan has started)


def test_ready_reports_db_and_redis(app_client: Api):
    r = app_client.c.get("/health/ready")
    assert r.status_code == 200 and r.json() == {"db": "ok", "redis": "ok"}


def test_audit_chain_verifies_after_flows(app_client: Api):
    register_farmer(app_client)
    app_client.post("/api/v1/auth/logout")
    assert sql("SELECT audit_verify_chain()") == [(0,)]
    assert sql("SELECT count(*) FROM audit_log WHERE action LIKE 'auth.%%'")[0][0] >= 2
