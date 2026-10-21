"""Server-side sessions (spec 16.4): 256-bit opaque token, only its SHA-256 is stored.

Postgres is the record; Redis is a 60-second read cache in front of it, so a Redis outage degrades
to slower lookups (DB fallback) instead of logging everybody out. Revocation deletes the cache
entry,
so a revoked session stops working at once rather than after the cache expires.

Lifetimes: farmer 30 min idle (30 days when "keep me signed in"), staff 30 min idle / 12 h absolute,
admin 15 min idle / 12 h absolute, demo = the demo session length. The token is rotated after 15 min
of activity, on login and on step-up; the old token stays valid for 30 s so parallel requests and
flaky mobile networks do not log the user out.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.clock import utcnow
from app.core.ids import uuid7
from app.core.security import new_token, sha256_hex
from app.core.tenancy import DEMO_ROLES, tenant_for
from app.db.session import system_scope

COOKIE_NAME = "__Host-cg_session"
ROTATE_AFTER = timedelta(minutes=15)
GRACE = timedelta(seconds=30)
TOUCH_EVERY = timedelta(seconds=60)
CACHE_TTL = 60
STEP_UP_WINDOW = timedelta(minutes=10)
FARMER_KEEP = timedelta(days=30)
_ABSOLUTE_STAFF = timedelta(hours=12)


@dataclass(frozen=True)
class Timeouts:
    idle: timedelta
    absolute: timedelta


def timeouts_for(role: str, keep_signed_in: bool, demo_minutes: int = 30) -> Timeouts:
    if role in DEMO_ROLES:
        span = timedelta(minutes=demo_minutes)
        return Timeouts(span, span)
    if role == "FARMER":
        if keep_signed_in:
            return Timeouts(FARMER_KEEP, FARMER_KEEP)
        return Timeouts(timedelta(minutes=30), _ABSOLUTE_STAFF)
    if role == "ADMIN":
        return Timeouts(timedelta(minutes=15), _ABSOLUTE_STAFF)
    return Timeouts(timedelta(minutes=30), _ABSOLUTE_STAFF)  # REVIEWER


@dataclass(frozen=True)
class SessionData:
    id: str
    token_hash: str
    user_id: str
    tenant_id: str
    role: str
    status: str
    region_codes: tuple[str, ...]
    locale: str
    csrf_secret: str
    keep_signed_in: bool
    created_at: datetime
    last_seen_at: datetime
    expires_at: datetime
    absolute_expires_at: datetime
    totp_verified_at: datetime | None
    step_up_at: datetime | None

    def step_up_valid(self, now: datetime) -> bool:
        return self.step_up_at is not None and now - self.step_up_at <= STEP_UP_WINDOW

    def to_json(self) -> str:
        raw = asdict(self)
        for key, value in raw.items():
            if isinstance(value, datetime):
                raw[key] = value.isoformat()
        raw["region_codes"] = list(self.region_codes)
        return json.dumps(raw)

    @staticmethod
    def from_json(blob: str) -> SessionData:
        raw = json.loads(blob)
        for key in ("created_at", "last_seen_at", "expires_at", "absolute_expires_at",
                    "totp_verified_at", "step_up_at"):  # fmt: skip
            if raw[key] is not None:
                raw[key] = datetime.fromisoformat(raw[key])
        raw["region_codes"] = tuple(raw["region_codes"])
        return SessionData(**raw)


# Three fixed queries (never built from strings): by id, by token hash, and a user's live sessions.
_BY_ID = """
SELECT s.id::text, s.token_hash, s.user_id::text, s.tenant_id, u.role, u.status, u.region_codes,
       u.locale, s.csrf_secret, s.keep_signed_in, s.created_at, s.last_seen_at, s.expires_at,
       s.absolute_expires_at, s.totp_verified_at, s.step_up_at
FROM sessions s JOIN users u ON u.id = s.user_id
WHERE s.id = CAST(:v AS uuid) AND s.revoked_at IS NULL
"""
_BY_DIGEST = """
SELECT s.id::text, s.token_hash, s.user_id::text, s.tenant_id, u.role, u.status, u.region_codes,
       u.locale, s.csrf_secret, s.keep_signed_in, s.created_at, s.last_seen_at, s.expires_at,
       s.absolute_expires_at, s.totp_verified_at, s.step_up_at
FROM sessions s JOIN users u ON u.id = s.user_id
WHERE s.token_hash = :v AND s.revoked_at IS NULL
"""
_FOR_USER = """
SELECT s.id::text, s.token_hash, s.user_id::text, s.tenant_id, u.role, u.status, u.region_codes,
       u.locale, s.csrf_secret, s.keep_signed_in, s.created_at, s.last_seen_at, s.expires_at,
       s.absolute_expires_at, s.totp_verified_at, s.step_up_at
FROM sessions s JOIN users u ON u.id = s.user_id
WHERE s.user_id = CAST(:uid AS uuid) AND s.revoked_at IS NULL
  AND s.expires_at > :now AND s.absolute_expires_at > :now
  AND NOT EXISTS (SELECT 1 FROM sessions n WHERE n.rotated_from = s.id AND n.revoked_at IS NULL)
ORDER BY s.created_at DESC
"""


def _row_to_data(row: Any) -> SessionData:
    r = tuple(row)
    return SessionData(
        id=r[0], token_hash=r[1], user_id=r[2], tenant_id=r[3], role=r[4], status=r[5],
        region_codes=tuple(r[6] or ()), locale=r[7], csrf_secret=r[8], keep_signed_in=r[9],
        created_at=r[10], last_seen_at=r[11], expires_at=r[12], absolute_expires_at=r[13],
        totp_verified_at=r[14], step_up_at=r[15],
    )  # fmt: skip


class SessionStore:
    def __init__(
        self,
        engine: AsyncEngine,
        redis: Redis | None,
        *,
        clock: Callable[[], datetime] = utcnow,
        demo_minutes: int = 30,
    ) -> None:
        self._engine = engine
        self._redis = redis
        self._now = clock
        self._demo_minutes = demo_minutes

    # --- create -----------------------------------------------------------------------------
    async def create(
        self,
        *,
        user_id: str,
        role: str,
        keep_signed_in: bool = False,
        ip_hash: str | None = None,
        user_agent: str | None = None,
        totp_verified_at: datetime | None = None,
        step_up_at: datetime | None = None,
        csrf_secret: str | None = None,
        rotated_from: str | None = None,
        absolute_cap: datetime | None = None,
    ) -> tuple[str, SessionData]:
        """Insert a session; returns (raw token, data). The raw token exists only in this return."""
        now = self._now()
        limits = timeouts_for(role, keep_signed_in, self._demo_minutes)
        token = new_token(32)
        sid = str(uuid7(now))
        absolute = now + limits.absolute
        if absolute_cap is not None:  # rotation must never extend a session's life
            absolute = min(absolute, absolute_cap)
        expires = min(now + limits.idle, absolute)
        async with system_scope(self._engine) as db:
            await db.execute(
                text(
                    "INSERT INTO sessions (id, tenant_id, user_id, token_hash, csrf_secret, "
                    "keep_signed_in, created_at, last_seen_at, rotated_from, expires_at, "
                    "absolute_expires_at, ip_hash, user_agent, totp_verified_at, step_up_at) "
                    "VALUES (CAST(:id AS uuid), :tenant, CAST(:uid AS uuid), :th, :csrf, :keep, "
                    ":now, :now, CAST(:rot AS uuid), :exp, :abs, :ip, :ua, :totp, :step)"
                ),
                {
                    "id": sid, "tenant": tenant_for(role), "uid": user_id,
                    "th": sha256_hex(token), "csrf": csrf_secret or new_token(24),
                    "keep": keep_signed_in, "now": now, "rot": rotated_from, "exp": expires,
                    "abs": absolute, "ip": ip_hash, "ua": (user_agent or "")[:255] or None,
                    "totp": totp_verified_at, "step": step_up_at,
                },
            )  # fmt: skip
            # .one(): the row we just inserted must be readable, otherwise this raises
            data = _row_to_data((await db.execute(text(_BY_ID), {"v": sid})).one())
        await self._cache_put(data)
        return token, data

    # --- load -------------------------------------------------------------------------------
    async def load(self, token: str | None) -> SessionData | None:
        if not token or len(token) > 128:
            return None
        token_hash = sha256_hex(token)
        data = await self._cache_get(token_hash)
        if data is None:
            async with system_scope(self._engine) as db:
                data = await self._fetch(db, _BY_DIGEST, token_hash)
            if data is None:
                return None
        now = self._now()
        if self._expired(data, now):
            return None
        if data.status != "ACTIVE":
            return None
        return data

    def _expired(self, data: SessionData, now: datetime) -> bool:
        return now >= data.expires_at or now >= data.absolute_expires_at

    async def touch(self, data: SessionData) -> SessionData:
        """Slide the idle window (at most once a minute, to keep writes down)."""
        now = self._now()
        if now - data.last_seen_at < TOUCH_EVERY:
            return data
        limits = timeouts_for(data.role, data.keep_signed_in, self._demo_minutes)
        expires = min(now + limits.idle, data.absolute_expires_at)
        async with system_scope(self._engine) as db:
            await db.execute(
                text(
                    "UPDATE sessions SET last_seen_at = :now, expires_at = :exp "
                    "WHERE id = CAST(:id AS uuid) AND revoked_at IS NULL"
                ),
                {"now": now, "exp": expires, "id": data.id},
            )
        fresh = replace(data, last_seen_at=now, expires_at=expires)
        await self._cache_put(fresh)
        return fresh

    # --- rotate -----------------------------------------------------------------------------
    def should_rotate(self, data: SessionData) -> bool:
        return self._now() - data.created_at >= ROTATE_AFTER

    async def rotate(
        self, data: SessionData, *, totp_verified: bool | None = None, step_up: bool = False,
        ip_hash: str | None = None, user_agent: str | None = None,
    ) -> tuple[str, SessionData]:  # fmt: skip
        """Issue a fresh token; the old one dies in 30 s. Carries over 2FA / step-up state."""
        now = self._now()
        totp_at = data.totp_verified_at
        if totp_verified is not None:
            totp_at = now if totp_verified else None
        step_at = now if step_up else (data.step_up_at if data.step_up_valid(now) else None)
        token, fresh = await self.create(
            user_id=data.user_id,
            role=data.role,
            keep_signed_in=data.keep_signed_in,
            ip_hash=ip_hash,
            user_agent=user_agent,
            totp_verified_at=totp_at,
            step_up_at=step_at,
            csrf_secret=data.csrf_secret,
            rotated_from=data.id,
            absolute_cap=data.absolute_expires_at,
        )
        async with system_scope(self._engine) as db:
            await db.execute(
                text(
                    "UPDATE sessions SET expires_at = LEAST(expires_at, :grace) "
                    "WHERE id = CAST(:id AS uuid) AND revoked_at IS NULL"
                ),
                {"grace": now + GRACE, "id": data.id},
            )
        await self._cache_delete(data.token_hash)
        return token, fresh

    async def mark_step_up(self, data: SessionData) -> tuple[str, SessionData]:
        return await self.rotate(data, step_up=True)

    async def mark_totp_verified(self, data: SessionData) -> tuple[str, SessionData]:
        return await self.rotate(data, totp_verified=True)

    # --- list / revoke ----------------------------------------------------------------------
    async def list_for_user(self, user_id: str) -> list[SessionData]:
        async with system_scope(self._engine) as db:
            result = await db.execute(text(_FOR_USER), {"uid": user_id, "now": self._now()})
            return [_row_to_data(r) for r in result.fetchall()]

    async def revoke(self, session_id: str, user_id: str) -> bool:
        """Revoke one of `user_id`'s sessions. Returns False when it is not theirs (-> 404)."""
        async with system_scope(self._engine) as db:
            result = await db.execute(
                text(
                    "UPDATE sessions SET revoked_at = :now WHERE id = CAST(:id AS uuid) "
                    "AND user_id = CAST(:uid AS uuid) AND revoked_at IS NULL RETURNING token_hash"
                ),
                {"now": self._now(), "id": session_id, "uid": user_id},
            )
            row = result.first()
        if row is None:
            return False
        await self._cache_delete(row[0])
        return True

    async def revoke_all(self, user_id: str, *, except_id: str | None = None) -> int:
        async with system_scope(self._engine) as db:
            result = await db.execute(
                text(
                    "UPDATE sessions SET revoked_at = :now WHERE user_id = CAST(:uid AS uuid) "
                    "AND revoked_at IS NULL AND (CAST(:keep AS text) IS NULL OR id::text <> :keep) "
                    "RETURNING token_hash"
                ),
                {"now": self._now(), "uid": user_id, "keep": except_id},
            )
            hashes = [r[0] for r in result.fetchall()]
        for h in hashes:
            await self._cache_delete(h)
        return len(hashes)

    async def purge_expired(self) -> int:
        async with system_scope(self._engine) as db:
            result = await db.execute(
                text(
                    "DELETE FROM sessions WHERE (absolute_expires_at < :cut OR revoked_at < :cut) "
                    "RETURNING 1"
                ),
                {"cut": self._now() - timedelta(days=1)},
            )
            return len(result.fetchall())

    # --- internals --------------------------------------------------------------------------
    async def _fetch(self, db: Any, query: str, value: str) -> SessionData | None:
        row = (await db.execute(text(query), {"v": value})).first()
        return _row_to_data(row) if row else None

    async def _cache_get(self, token_hash: str) -> SessionData | None:
        if self._redis is None:
            return None
        try:
            blob = await self._redis.get(f"cg:sess:{token_hash}")
        except (RedisError, OSError):
            return None
        if not blob:
            return None
        try:
            return SessionData.from_json(blob)
        except (ValueError, KeyError, TypeError):
            return None

    async def _cache_put(self, data: SessionData) -> None:
        if self._redis is None:
            return
        try:
            await self._redis.set(f"cg:sess:{data.token_hash}", data.to_json(), ex=CACHE_TTL)
        except (RedisError, OSError):
            return

    async def _cache_delete(self, token_hash: str) -> None:
        if self._redis is None:
            return
        try:
            await self._redis.delete(f"cg:sess:{token_hash}")
        except (RedisError, OSError):
            return
