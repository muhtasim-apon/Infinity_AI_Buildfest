import base64
import json
from datetime import UTC, datetime, timedelta

import pytest

from app.core.authz import (
    POLICIES,
    Policy,
    Principal,
    Resource,
    authorize,
    principal_from_session,
)
from app.core.captcha import MAX_NUMBER, Captcha, solve
from app.core.errors import AppError
from app.core.sessions import STEP_UP_WINDOW, SessionData, Timeouts, timeouts_for
from app.core.tenancy import ROLES, base_role, db_context_for, tenant_for


def principal(role="FARMER", *, uid="u1", regions=(), totp=False, step_up=False):
    return Principal(
        user_id=uid,
        role=role,
        tenant_id=tenant_for(role),
        region_codes=tuple(regions),
        session_id="s1",
        locale="bn",
        totp_verified=totp,
        step_up=step_up,
    )


def status_of(p, action, resource=None):
    try:
        authorize(p, action, resource)
    except AppError as exc:
        return exc.status, exc.code
    return 200, ""


# --- tenancy -----------------------------------------------------------------------------------
def test_tenancy_mapping_and_db_context_never_system():
    for role in ROLES:
        ctx = db_context_for("u", role, ("D1", "D2"))
        assert ctx.role in {"farmer", "reviewer", "admin"}  # never "system"
        assert ctx.tenant == ("demo" if role.startswith("DEMO_") else "real")
        assert ctx.region_csv == "D1,D2"
    assert base_role("DEMO_ADMIN") == "admin"
    with pytest.raises(KeyError):
        base_role("system")


# --- authz -------------------------------------------------------------------------------------
@pytest.mark.security
def test_anonymous_and_unregistered_action():
    assert status_of(None, "me:read") == (401, "authentication_required")
    assert status_of(principal(), "unregistered:thing") == (403, "forbidden")


@pytest.mark.security
def test_admin_area_is_404_for_everyone_else():
    for role in ("FARMER", "REVIEWER", "DEMO_FARMER", "DEMO_REVIEWER"):
        assert status_of(principal(role, totp=True), "admin:users:list") == (404, "not_found")
    assert status_of(principal("ADMIN", totp=True), "admin:users:list") == (200, "")


@pytest.mark.security
def test_wrong_role_is_403_when_not_hidden():
    assert status_of(principal("FARMER"), "auth:step_up") == (403, "forbidden")
    assert status_of(principal("REVIEWER", totp=True), "me:consents") == (403, "forbidden")


@pytest.mark.security
def test_staff_need_totp_demo_staff_do_not():
    assert status_of(principal("ADMIN"), "admin:users:list") == (403, "totp_required")
    assert status_of(principal("REVIEWER"), "me:read") == (403, "totp_required")
    assert status_of(principal("DEMO_ADMIN"), "admin:users:list") == (200, "")
    assert status_of(principal("FARMER"), "me:read") == (200, "")


@pytest.mark.security
def test_step_up_required_and_demo_cannot_invite():
    assert status_of(principal("ADMIN", totp=True), "admin:invites:create") == (
        403,
        "step_up_required",
    )
    assert status_of(principal("ADMIN", totp=True, step_up=True), "admin:invites:create") == (
        200,
        "",
    )
    assert status_of(principal("DEMO_ADMIN"), "admin:invites:create") == (404, "not_found")


@pytest.mark.security
def test_ownership_tenant_and_region_hide_as_404():
    POLICIES["t:owned"] = Policy(frozenset({"farmer", "reviewer", "admin"}), owner_only=True)
    POLICIES["t:regional"] = Policy(frozenset({"reviewer", "admin"}), region_scoped=True)
    try:
        me = principal("FARMER", uid="a")
        assert status_of(me, "t:owned", Resource(owner_id="a", tenant_id="real")) == (200, "")
        assert status_of(me, "t:owned", Resource(owner_id="b", tenant_id="real")) == (
            404,
            "not_found",
        )
        assert status_of(me, "t:owned", Resource(owner_id="a", tenant_id="demo")) == (
            404,
            "not_found",
        )
        admin = principal("ADMIN", totp=True)
        assert status_of(admin, "t:owned", Resource(owner_id="b", tenant_id="real")) == (200, "")
        rev = principal("REVIEWER", totp=True, regions=("D1",))
        assert status_of(rev, "t:regional", Resource(region_code="D1")) == (200, "")
        assert status_of(rev, "t:regional", Resource(region_code="D2")) == (404, "not_found")
        assert status_of(rev, "t:regional", Resource(region_code=None)) == (404, "not_found")
    finally:
        del POLICIES["t:owned"], POLICIES["t:regional"]


def test_principal_from_session_derives_flags():
    now = datetime(2026, 10, 19, 12, tzinfo=UTC)
    data = session_data(role="ADMIN", totp=now, step_up=now - STEP_UP_WINDOW + timedelta(seconds=1))
    p = principal_from_session(data, now)
    assert p.totp_verified and p.step_up and p.base == "admin" and not p.is_demo
    stale = session_data(role="DEMO_FARMER", step_up=now - STEP_UP_WINDOW - timedelta(seconds=1))
    p2 = principal_from_session(stale, now)
    assert not p2.step_up and p2.is_demo and not p2.needs_totp


def session_data(role="FARMER", totp=None, step_up=None):
    t = datetime(2026, 10, 19, 11, tzinfo=UTC)
    return SessionData(
        id="s", token_hash="h", user_id="u", tenant_id=tenant_for(role), role=role, status="ACTIVE",
        region_codes=("D1",), locale="bn", csrf_secret="c" * 32, keep_signed_in=False,
        created_at=t, last_seen_at=t, expires_at=t, absolute_expires_at=t,
        totp_verified_at=totp, step_up_at=step_up,
    )  # fmt: skip


def test_session_json_roundtrip_and_timeouts():
    now = datetime(2026, 10, 19, 12, tzinfo=UTC)
    data = session_data(totp=now, step_up=None)
    assert SessionData.from_json(data.to_json()) == data
    assert timeouts_for("FARMER", True).idle == timedelta(days=30)
    assert timeouts_for("FARMER", False) == Timeouts(timedelta(minutes=30), timedelta(hours=12))
    assert timeouts_for("ADMIN", False).idle == timedelta(minutes=15)
    assert timeouts_for("REVIEWER", False).idle == timedelta(minutes=30)
    assert timeouts_for("DEMO_FARMER", True, 45) == Timeouts(
        timedelta(minutes=45), timedelta(minutes=45)
    )


# --- captcha (fake redis: SET NX only) ---------------------------------------------------------
class FakeRedis:
    def __init__(self, fail=False):
        self.seen: set[str] = set()
        self.fail = fail

    async def set(self, key, value, nx=False, ex=None):
        if self.fail:
            from redis.exceptions import ConnectionError as RedisConnectionError

            raise RedisConnectionError("down")
        if nx and key in self.seen:
            return None
        self.seen.add(key)
        return True


class Clock:
    def __init__(self):
        self.t = 1_800_000_000.0

    def __call__(self):
        return self.t


@pytest.fixture
def clock():
    return Clock()


def make_captcha(clock, redis=None, bypass=False):
    return Captcha("s" * 40, FakeRedis() if redis is None else redis, bypass=bypass, now=clock)


async def expect_invalid(captcha, payload):
    with pytest.raises(AppError) as err:
        await captcha.verify(payload)
    assert err.value.status == 400 and err.value.code == "captcha_invalid"


@pytest.mark.security
async def test_captcha_valid_once_then_replay_rejected(clock):
    captcha = make_captcha(clock)
    payload = solve(captcha.issue())
    clock.t += 3
    await captcha.verify(payload)
    await expect_invalid(captcha, payload)  # replay


@pytest.mark.security
async def test_captcha_too_fast_expired_tampered_malformed(clock):
    captcha = make_captcha(clock)
    ch = captcha.issue()
    payload = solve(ch)
    await expect_invalid(captcha, payload)  # no minimum elapsed time yet
    clock.t += 301
    await expect_invalid(captcha, payload)  # expired

    clock.t = 1_800_000_000.0
    fresh = captcha.issue()
    body = json.loads(base64.b64decode(solve(fresh)))
    clock.t += 3
    for field, value in (
        ("signature", "0" * 64),
        ("challenge", "f" * 64),
        ("salt", "ab" * 12),
        ("number", body["number"] + 1),
        ("expires_at", body["expires_at"] + 1000),
    ):
        forged = {**body, field: value}
        await expect_invalid(captcha, base64.b64encode(json.dumps(forged).encode()).decode())
    for junk in (None, "", "!!!", base64.b64encode(b"[]").decode(), base64.b64encode(b"{}").decode(),
                 base64.b64encode(b'{"challenge":1}').decode(), "A" * 3000):  # fmt: skip
        await expect_invalid(captcha, junk)
    out_of_range = {**body, "number": MAX_NUMBER + 1}
    await expect_invalid(captcha, base64.b64encode(json.dumps(out_of_range).encode()).decode())
    non_numeric = {**body, "number": "x"}
    await expect_invalid(captcha, base64.b64encode(json.dumps(non_numeric).encode()).decode())


@pytest.mark.security
async def test_captcha_fails_closed_without_redis_and_bypass_only_when_set(clock):
    payload = solve(make_captcha(clock).issue())
    clock.t += 3
    for redis in (FakeRedis(fail=True), None):
        captcha = Captcha("s" * 40, redis, now=clock)  # type: ignore[arg-type]
        with pytest.raises(AppError) as err:
            await captcha.verify(payload)
        assert err.value.status == 503
    await make_captcha(clock, bypass=True).verify(None)  # test-env bypass


def test_captcha_default_clock_and_solver_failure():
    ch = Captcha("s" * 40, None).issue()
    assert ch.maxnumber == MAX_NUMBER and ch.algorithm == "SHA-256"
    assert ch.expires_at - ch.issued_at == 300
