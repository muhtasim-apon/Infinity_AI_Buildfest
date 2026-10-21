"""Rate limiter and session store against real Redis + Postgres (TEST_REDIS_URL, TEST_API_DATABASE_URL)."""

import os
import uuid
from datetime import UTC, datetime, timedelta

import pytest
from redis.asyncio import Redis
from sqlalchemy import text

from app.core.config import Settings
from app.core.errors import AppError
from app.core.ratelimit import RULES, RateLimiter
from app.core.sessions import GRACE, ROTATE_AFTER, SessionStore
from app.db.session import make_engine, system_scope

REDIS_URL = os.environ.get("TEST_REDIS_URL")
API = os.environ.get("TEST_API_DATABASE_URL")
pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        not (REDIS_URL and API), reason="TEST_REDIS_URL / TEST_API_DATABASE_URL unset"
    ),
]
HASH = "$argon2id$v=19$m=65536,t=3,p=2$c29tZXNhbHQ$aGFzaA"


class Clock:
    def __init__(self):
        self.now = datetime(2026, 10, 19, 12, 0, tzinfo=UTC)

    def __call__(self):
        return self.now

    def advance(self, **kw):
        self.now += timedelta(**kw)


@pytest.fixture
async def redis():
    client = Redis.from_url(REDIS_URL, decode_responses=True)
    await client.flushdb()
    yield client
    await client.flushdb()
    await client.aclose()


@pytest.fixture
async def engine():
    eng = make_engine(Settings(database_url=API, _env_file=None))  # type: ignore[call-arg]
    yield eng
    await eng.dispose()


async def make_user(engine, role="FARMER", status="ACTIVE"):
    uid = str(uuid.uuid4())
    farmer = role in ("FARMER", "DEMO_FARMER")
    async with system_scope(engine) as db:
        await db.execute(
            text(
                "INSERT INTO users (id, tenant_id, role, phone_e164, email, display_name, "
                "password_hash, status, region_codes) VALUES (CAST(:id AS uuid), :t, :r, :p, :e, "
                "'Test', :h, :s, ARRAY['D1'])"
            ),
            {
                "id": uid,
                "t": "demo" if role.startswith("DEMO") else "real",
                "r": role,
                "p": f"+88017{uuid.uuid4().int % 10**8:08d}" if farmer else None,
                "e": None if farmer else f"{uid}@example.org",
                "h": HASH,
                "s": status,
            },
        )
    return uid


# --- rate limiter -------------------------------------------------------------------------------
@pytest.mark.security
async def test_login_limit_blocks_6th_attempt_with_retry_after(redis):
    clock_ms = [1_000_000]
    limiter = RateLimiter(redis, now_ms=lambda: clock_ms[0])
    for _ in range(5):
        assert (await limiter.hit("login", "1.2.3.4|alice")).allowed
        clock_ms[0] += 100
    blocked = await limiter.hit("login", "1.2.3.4|alice")
    assert not blocked.allowed and 1 <= blocked.retry_after <= 60
    assert (await limiter.hit("login", "1.2.3.4|bob")).allowed  # different key
    clock_ms[0] += 61_000  # window slides
    assert (await limiter.hit("login", "1.2.3.4|alice")).allowed


@pytest.mark.security
async def test_hourly_window_and_every_rule_is_defined(redis):
    clock_ms = [5_000_000]
    limiter = RateLimiter(redis, now_ms=lambda: clock_ms[0])
    allowed = 0
    for _ in range(40):
        clock_ms[0] += 61_000  # stays under 5/min but hits 20/hour
        if (await limiter.hit("login", "ip|x")).allowed:
            allowed += 1
    assert allowed == 20
    assert all(rule.windows and rule.name == name for name, rule in RULES.items())


async def test_enforce_raises_429_with_retry_after_and_keys_hold_no_pii(redis):
    limiter = RateLimiter(redis)
    await limiter.enforce("otp_send", "+8801712345678")
    with pytest.raises(AppError) as err:
        await limiter.enforce("otp_send", "+8801712345678")
    assert err.value.status == 429 and err.value.extra["retry_after"] >= 1
    keys = [k async for k in redis.scan_iter("cg:rl:*")]
    assert keys and not any("8801712345678" in k for k in keys)


@pytest.mark.security
async def test_fail_closed_vs_fail_open_when_redis_is_down():
    dead = Redis.from_url("redis://127.0.0.1:1/0", socket_connect_timeout=0.2, socket_timeout=0.2)
    limiter = RateLimiter(dead)
    with pytest.raises(AppError) as err:
        await limiter.hit("login", "x")
    assert err.value.status == 503
    assert (await limiter.hit("public_read", "x")).allowed  # reads fail open
    with pytest.raises(AppError):
        await RateLimiter(None).hit("otp_send", "x")
    assert (await RateLimiter(None).hit("api_user", "x")).allowed
    await dead.aclose()


# --- sessions -----------------------------------------------------------------------------------
async def test_session_create_load_touch_and_cache(engine, redis):
    clock = Clock()
    store = SessionStore(engine, redis, clock=clock)
    uid = await make_user(engine)
    token, data = await store.create(user_id=uid, role="FARMER", user_agent="UA/1.0")
    assert len(token) >= 43 and token not in data.token_hash
    loaded = await store.load(token)
    assert loaded and loaded.user_id == uid and loaded.status == "ACTIVE"
    await redis.flushdb()  # Redis down/cold -> DB fallback still works
    assert (await store.load(token)).id == data.id
    assert await store.touch(loaded) == loaded  # within a minute: no write
    clock.advance(minutes=5)
    touched = await store.touch(loaded)
    assert touched.expires_at > loaded.expires_at
    async with system_scope(engine) as db:
        stored = (await db.execute(text("SELECT token_hash FROM sessions"))).scalars().all()
    assert token not in stored  # only the hash is stored


@pytest.mark.security
async def test_expiry_idle_absolute_unknown_and_inactive_user(engine, redis):
    clock = Clock()
    store = SessionStore(engine, redis, clock=clock)
    uid = await make_user(engine)
    token, _ = await store.create(user_id=uid, role="FARMER")
    assert await store.load(None) is None
    assert await store.load("x" * 200) is None
    assert await store.load("not-a-real-token") is None
    clock.advance(minutes=31)
    assert await store.load(token) is None  # idle timeout
    suspended = await make_user(engine, status="SUSPENDED")
    token2, _ = await store.create(user_id=suspended, role="FARMER")
    assert await store.load(token2) is None


@pytest.mark.security
async def test_rotation_grace_period_and_absolute_cap(engine, redis):
    clock = Clock()
    store = SessionStore(engine, redis, clock=clock)
    uid = await make_user(engine, role="ADMIN")
    token, first = await store.create(user_id=uid, role="ADMIN", totp_verified_at=clock.now)
    assert not store.should_rotate(first)
    clock.advance(minutes=14)
    first = await store.touch(first)
    clock.advance(minutes=1)
    assert store.should_rotate(first)
    new_token, second = await store.rotate(first)
    assert new_token != token and second.csrf_secret == first.csrf_secret
    assert second.totp_verified_at == first.totp_verified_at
    assert second.absolute_expires_at <= first.absolute_expires_at  # never extended
    assert await store.load(token) is not None  # old token still valid inside the grace window
    clock.advance(seconds=int(GRACE.total_seconds()) + 1)
    assert await store.load(token) is None
    assert await store.load(new_token) is not None
    _, stepped = await store.mark_step_up(second)
    assert stepped.step_up_valid(clock.now)
    _, with_totp = await store.mark_totp_verified(stepped)
    assert with_totp.totp_verified_at is not None
    assert timedelta(minutes=15) == ROTATE_AFTER


@pytest.mark.security
async def test_revoke_one_all_and_ownership(engine, redis):
    store = SessionStore(engine, redis)
    a, b = await make_user(engine), await make_user(engine)
    ta1, da1 = await store.create(user_id=a, role="FARMER")
    ta2, da2 = await store.create(user_id=a, role="FARMER")
    tb, db_ = await store.create(user_id=b, role="FARMER")
    assert not await store.revoke(db_.id, a)  # someone else's session -> not revoked
    assert await store.load(tb) is not None
    assert await store.revoke(da1.id, a)
    assert not await store.revoke(da1.id, a)  # already revoked
    assert await store.load(ta1) is None
    assert len(await store.list_for_user(a)) == 1
    assert await store.revoke_all(a, except_id=da2.id) == 0
    assert await store.revoke_all(a) == 1
    assert await store.load(ta2) is None
    assert await store.list_for_user(a) == []
    assert await store.load(tb) is not None


async def test_purge_expired_and_demo_timeouts(engine, redis):
    clock = Clock()
    store = SessionStore(engine, redis, clock=clock, demo_minutes=20)
    uid = await make_user(engine, role="DEMO_FARMER")
    token, data = await store.create(user_id=uid, role="DEMO_FARMER")
    assert data.tenant_id == "demo"
    assert data.absolute_expires_at - clock.now == timedelta(minutes=20)
    clock.advance(minutes=21)
    assert await store.load(token) is None
    clock.advance(days=2)
    assert await store.purge_expired() >= 1
    no_cache = SessionStore(engine, None, clock=clock)
    assert await no_cache.load(token) is None  # works without Redis too


@pytest.mark.security
async def test_session_cache_failures_degrade_to_database(engine, redis):
    uid = await make_user(engine)
    dead = Redis.from_url("redis://127.0.0.1:1/0", socket_connect_timeout=0.2, socket_timeout=0.2)
    store = SessionStore(engine, dead)  # every Redis call fails -> DB is the only source
    token, data = await store.create(user_id=uid, role="FARMER")
    assert (await store.load(token)).id == data.id
    await store.touch(await store.load(token))
    await store.revoke_all(uid)
    assert await store.load(token) is None
    await dead.aclose()

    healthy = SessionStore(engine, redis)
    token2, data2 = await healthy.create(user_id=uid, role="FARMER")
    await redis.set(f"cg:sess:{data2.token_hash}", "{not json")  # corrupt cache entry is ignored
    assert (await healthy.load(token2)).id == data2.id
    await redis.set(f"cg:sess:{data2.token_hash}", '{"id": "x"}')  # wrong shape too
    assert (await healthy.load(token2)).id == data2.id
    no_redis = SessionStore(engine, None)
    token3, data3 = await no_redis.create(user_id=uid, role="FARMER")
    assert (await no_redis.load(token3)).id == data3.id
    assert await no_redis.revoke(data3.id, uid)
