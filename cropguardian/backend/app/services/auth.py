"""Authentication flows (spec 16.4): register, OTP, login, TOTP, step-up, password reset/change.

Pre-login lookups run in the server-internal SYSTEM context (no user exists yet to scope by).
Everything that answers "does this account exist?" returns the same shape and the same errors, and
unknown accounts are verified against a dummy hash so timing does not reveal them either.
"""

from __future__ import annotations

import asyncio
import secrets
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

import pyotp
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core import consent_texts, security
from app.core.captcha import Captcha
from app.core.clock import utcnow
from app.core.config import Settings
from app.core.errors import AppError
from app.core.ids import uuid7
from app.core.ratelimit import RateLimiter
from app.core.sessions import SessionData, SessionStore
from app.core.tenancy import tenant_for
from app.db.session import system_scope
from app.domain.phone import PhoneError, normalise_phone
from app.services import events
from app.services.notify import Notifier

OTP_TTL = timedelta(minutes=5)
OTP_MAX_ATTEMPTS = 5
VERIFY_TTL = timedelta(hours=24)
RESET_TTL = timedelta(minutes=30)
INVITE_TTL = timedelta(hours=72)
LOCK_AFTER = 10
LOCK_FOR = timedelta(minutes=15)
CAPTCHA_AFTER = 3
DELAY_AFTER = 5
FAIL_WINDOW = 3600
RECOVERY_CODE_COUNT = 10
STAFF = ("REVIEWER", "ADMIN")


@dataclass(frozen=True)
class RequestCtx:
    ip: str
    ip_hash: str
    user_agent: str
    request_id: str


@dataclass(frozen=True)
class LoginResult:
    token: str
    session: SessionData
    next: str  # home | totp | setup_totp


@dataclass(frozen=True)
class UserRow:
    id: str
    tenant_id: str
    role: str
    phone: str | None
    email: str | None
    display_name: str
    locale: str
    password_hash: str | None
    status: str
    region_codes: tuple[str, ...]
    email_verified_at: datetime | None


# Fixed lookups (never assembled from strings): by phone, by email (case-insensitive), by id.
_USER_QUERIES = {
    "phone_e164": """SELECT id::text, tenant_id, role, phone_e164, email, display_name, locale,
        password_hash, status, region_codes, email_verified_at FROM users WHERE phone_e164 = :v""",
    "email": """SELECT id::text, tenant_id, role, phone_e164, email, display_name, locale,
        password_hash, status, region_codes, email_verified_at FROM users
        WHERE lower(email) = lower(:v)""",
    "id": """SELECT id::text, tenant_id, role, phone_e164, email, display_name, locale,
        password_hash, status, region_codes, email_verified_at FROM users
        WHERE id = CAST(:v AS uuid)""",
}


def _user(row: Any) -> UserRow | None:
    if row is None:
        return None
    r = tuple(row)
    return UserRow(r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], tuple(r[9] or ()), r[10])


def _invalid_credentials() -> AppError:
    return AppError(401, "invalid_credentials")


def _otp_invalid() -> AppError:
    return AppError(400, "otp_invalid")


class AuthService:
    def __init__(
        self,
        *,
        settings: Settings,
        engine: AsyncEngine,
        redis: Redis | None,
        sessions: SessionStore,
        limiter: RateLimiter,
        captcha: Captcha,
        notifier: Notifier,
        clock: Callable[[], datetime] = utcnow,
        sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
    ) -> None:
        self.s = settings
        self.engine = engine
        self.redis = redis
        self.sessions = sessions
        self.limiter = limiter
        self.captcha = captcha
        self.notifier = notifier
        self.now = clock
        self.sleep = sleep

    # --- lookups ----------------------------------------------------------------------------
    async def _by(self, db: AsyncSession, column: str, value: str) -> UserRow | None:
        query = _USER_QUERIES.get(column)
        if query is None:
            raise ValueError("unsupported lookup column")
        result = await db.execute(text(query), {"v": value})
        return _user(result.first())

    async def get_user(self, user_id: str) -> UserRow | None:
        async with system_scope(self.engine) as db:
            return await self._by(db, "id", user_id)

    def _identify(self, identifier: str) -> tuple[str, str]:
        """(column, normalised value). Unparseable identifiers map to a value matching nobody."""
        cleaned = identifier.strip()
        if "@" in cleaned:
            return "email", cleaned.lower()[:254]
        try:
            return "phone_e164", normalise_phone(cleaned)
        except PhoneError:
            return "phone_e164", "+0"

    # --- registration (farmers) -------------------------------------------------------------
    async def register_farmer(
        self,
        ctx: RequestCtx,
        *,
        phone: str,
        password: str,
        display_name: str,
        locale: str,
        optional_consents: dict[str, bool],
        captcha: str | None,
        honeypot: str,
    ) -> None:
        await self.limiter.enforce("register", ctx.ip)
        if honeypot:
            return  # a bot filled the hidden field: answer exactly like success, create nothing
        await self.captcha.verify(captcha)
        try:
            e164 = normalise_phone(phone)
        except PhoneError as exc:
            raise AppError(422, "phone_invalid") from exc
        verdict = security.check_password(password, "farmer", [display_name, e164])
        if not verdict.ok:
            raise AppError(422, "password_weak", extra={"reason": verdict.code})
        pw_hash = security.hash_password(password)  # always paid, even for existing numbers
        user_id: str | None = None
        async with system_scope(self.engine) as db:
            existing = await self._by(db, "phone_e164", e164)
            if existing is None:
                user_id = str(uuid7(self.now()))
                await db.execute(
                    text(
                        "INSERT INTO users (id, tenant_id, role, phone_e164, display_name, locale, "
                        "password_hash, status) VALUES (CAST(:id AS uuid), 'real', 'FARMER', :p, "
                        ":n, :l, :h, 'PENDING')"
                    ),
                    {
                        "id": user_id,
                        "p": e164,
                        "n": display_name.strip(),
                        "l": locale,
                        "h": pw_hash,
                    },
                )
                await self._record_consents(db, user_id, "real", optional_consents)
                await events.record(
                    db, action="auth.register", actor_id=user_id, actor_role="FARMER",
                    object_type="user", object_id=user_id, request_id=ctx.request_id,
                    ip_hash=ctx.ip_hash,
                )  # fmt: skip
            elif existing.status == "PENDING":
                user_id = existing.id  # same person retrying: only re-send the code
        if user_id is not None:
            await self._issue_otp(ctx, user_id, e164, "register", locale)
        else:  # existing active account: spend the same limits (response must not differ)
            await self.limiter.enforce("otp_send", f"phone:{e164}")
            await self.limiter.enforce("otp_send_ip", ctx.ip)

    async def _record_consents(
        self, db: AsyncSession, user_id: str, tenant: str, optional: dict[str, bool]
    ) -> None:
        now = self.now()
        granted = {"service": True, **{k: bool(v) for k, v in optional.items()}}
        for purpose in consent_texts.PURPOSES:
            is_granted = granted.get(purpose, False)
            await db.execute(
                text(
                    "INSERT INTO consents (tenant_id, user_id, purpose, granted, text_version, "
                    "granted_at) VALUES (:t, CAST(:u AS uuid), :p, :g, :v, :at) "
                    "ON CONFLICT (user_id, purpose, text_version) DO NOTHING"
                ),
                {"t": tenant, "u": user_id, "p": purpose, "g": is_granted,
                 "v": consent_texts.CURRENT_VERSION, "at": now if is_granted else None},
            )  # fmt: skip

    # --- OTP --------------------------------------------------------------------------------
    def _otp_mac(self, user_id: str, purpose: str, code: str) -> str:
        return security.hmac_hex(self.s.secret_key, "otp", user_id, purpose, code)

    async def _issue_otp(
        self, ctx: RequestCtx, user_id: str, phone: str, purpose: str, locale: str
    ) -> None:
        await self.limiter.enforce("otp_send", f"phone:{phone}")
        await self.limiter.enforce("otp_send_ip", ctx.ip)
        code = security.new_otp()
        now = self.now()
        async with system_scope(self.engine) as db:
            await db.execute(
                text(
                    "UPDATE otp_codes SET consumed_at = :now WHERE user_id = CAST(:u AS uuid) "
                    "AND purpose = :p AND consumed_at IS NULL"
                ),
                {"now": now, "u": user_id, "p": purpose},
            )
            await db.execute(
                text(
                    "INSERT INTO otp_codes (tenant_id, user_id, purpose, code_hmac, expires_at) "
                    "VALUES ('real', CAST(:u AS uuid), :p, :mac, :exp)"
                ),
                {"u": user_id, "p": purpose, "mac": self._otp_mac(user_id, purpose, code),
                 "exp": now + OTP_TTL},
            )  # fmt: skip
        await self.notifier.send_sms_otp(phone, code, locale)

    async def send_otp(self, ctx: RequestCtx, *, phone: str, purpose: str) -> None:
        """Uniform: the caller learns nothing about whether the number has an account."""
        try:
            e164 = normalise_phone(phone)
        except PhoneError as exc:
            raise AppError(422, "phone_invalid") from exc
        async with system_scope(self.engine) as db:
            user = await self._by(db, "phone_e164", e164)
        wanted = "PENDING" if purpose == "register" else "ACTIVE"
        if user is None or user.role != "FARMER" or user.status != wanted:
            await self.limiter.enforce("otp_send", f"phone:{e164}")  # same cost either way
            await self.limiter.enforce("otp_send_ip", ctx.ip)
            return
        await self._issue_otp(ctx, user.id, e164, purpose, user.locale)

    async def _consume_otp(
        self, user_id: str, purpose: str, code: str, *, burn: bool = True
    ) -> bool:
        """Check a code (counting the attempt). `burn=False` checks without spending it."""
        now = self.now()
        async with system_scope(self.engine) as db:
            row = (
                await db.execute(
                    text(
                        "SELECT id::text, code_hmac, expires_at FROM otp_codes WHERE "
                        "user_id = CAST(:u AS uuid) AND purpose = :p AND consumed_at IS NULL "
                        "ORDER BY created_at DESC LIMIT 1"
                    ),
                    {"u": user_id, "p": purpose},
                )
            ).first()
            if row is None or row[2] <= now:
                return False
            attempts = (
                await db.execute(
                    text(
                        "UPDATE otp_codes SET attempts = attempts + 1 WHERE id = CAST(:i AS uuid) "
                        "RETURNING attempts"
                    ),
                    {"i": row[0]},
                )
            ).scalar_one()
            if attempts > OTP_MAX_ATTEMPTS:
                await db.execute(
                    text("UPDATE otp_codes SET consumed_at = :now WHERE id = CAST(:i AS uuid)"),
                    {"now": now, "i": row[0]},
                )
                return False
            if not code.isascii() or not security.safe_equal(
                row[1], self._otp_mac(user_id, purpose, code)
            ):
                return False
            if burn:
                await db.execute(
                    text("UPDATE otp_codes SET consumed_at = :now WHERE id = CAST(:i AS uuid)"),
                    {"now": now, "i": row[0]},
                )
            return True

    async def verify_registration(
        self, ctx: RequestCtx, *, phone: str, code: str, keep_signed_in: bool
    ) -> LoginResult:
        try:
            e164 = normalise_phone(phone)
        except PhoneError as exc:
            raise _otp_invalid() from exc
        await self.limiter.enforce("otp_verify", f"phone:{e164}")
        await self.limiter.enforce("otp_verify", f"ip:{ctx.ip}")
        async with system_scope(self.engine) as db:
            user = await self._by(db, "phone_e164", e164)
        if user is None or user.status != "PENDING" or user.role != "FARMER":
            await self.sleep(0)  # keep the shape; no account-state leak
            raise _otp_invalid()
        if not await self._consume_otp(user.id, "register", code):
            raise _otp_invalid()
        async with system_scope(self.engine) as db:
            await db.execute(
                text(
                    "UPDATE users SET status = 'ACTIVE', phone_verified_at = :now "
                    "WHERE id = CAST(:i AS uuid)"
                ),
                {"now": self.now(), "i": user.id},
            )
            await events.record(
                db, action="auth.phone_verified", actor_id=user.id, actor_role="FARMER",
                object_type="user", object_id=user.id, request_id=ctx.request_id,
                ip_hash=ctx.ip_hash,
            )  # fmt: skip
        token, data = await self.sessions.create(
            user_id=user.id, role="FARMER", keep_signed_in=keep_signed_in,
            ip_hash=ctx.ip_hash, user_agent=ctx.user_agent,
        )  # fmt: skip
        return LoginResult(token, data, "home")

    # --- login ------------------------------------------------------------------------------
    def _fail_key(self, ident: str) -> str:
        return f"cg:lf:{security.sha256_hex(ident)[:32]}"

    async def _failures(self, ident: str) -> tuple[int, int]:
        """(failure count, seconds locked). Redis unreachable -> 503 (login fails closed)."""
        if self.redis is None:
            raise AppError(503, "auth_unavailable", "Try again shortly.")
        try:
            count = int(await self.redis.get(self._fail_key(ident)) or 0)
            ttl = await self.redis.ttl(f"{self._fail_key(ident)}:lock")
        except (RedisError, OSError) as exc:
            raise AppError(503, "auth_unavailable", "Try again shortly.") from exc
        return count, max(int(ttl), 0)

    async def _register_failure(self, ident: str) -> int:
        if self.redis is None:
            raise AppError(503, "auth_unavailable", "Try again shortly.")
        key = self._fail_key(ident)
        try:
            count = int(await self.redis.incr(key))
            await self.redis.expire(key, FAIL_WINDOW)
            if count >= LOCK_AFTER:
                await self.redis.set(f"{key}:lock", "1", ex=int(LOCK_FOR.total_seconds()))
        except (RedisError, OSError) as exc:
            raise AppError(503, "auth_unavailable", "Try again shortly.") from exc
        return count

    async def _clear_failures(self, ident: str) -> None:
        if self.redis is not None:
            try:
                await self.redis.delete(self._fail_key(ident), f"{self._fail_key(ident)}:lock")
            except (RedisError, OSError):
                return

    async def login(
        self,
        ctx: RequestCtx,
        *,
        identifier: str,
        password: str,
        keep_signed_in: bool,
        captcha: str | None,
    ) -> LoginResult:
        column, value = self._identify(identifier)
        ident = f"{column}:{value}"
        await self.limiter.enforce("login", f"{ctx.ip}|{ident}")
        failures, locked_for = await self._failures(ident)
        if locked_for:
            raise AppError(429, "account_locked", extra={"retry_after": locked_for})
        if failures >= CAPTCHA_AFTER:
            if not captcha:
                raise AppError(400, "captcha_required")
            await self.captcha.verify(captcha)
        async with system_scope(self.engine) as db:
            user = await self._by(db, column, value)
        ok = security.verify_password(user.password_hash if user else None, password)
        if user is not None and ok and user.status == "PENDING":
            raise AppError(403, "verification_required")
        if not ok or user is None or user.status != "ACTIVE":
            count = await self._register_failure(ident)
            if user is not None:
                await self._record_failure(user.id, ctx)
            if count > DELAY_AFTER:
                await self.sleep(min(2 ** (count - DELAY_AFTER), 8))
            raise _invalid_credentials()
        await self._clear_failures(ident)
        return await self._start_session(ctx, user, password, keep_signed_in)

    async def _record_failure(self, user_id: str, ctx: RequestCtx) -> None:
        async with system_scope(self.engine) as db:
            await db.execute(
                text(
                    "UPDATE users SET failed_logins = failed_logins + 1, last_failed_at = :now "
                    "WHERE id = CAST(:i AS uuid)"
                ),
                {"now": self.now(), "i": user_id},
            )
            await events.record(
                db, action="auth.login_failed", actor_id=user_id, object_type="user",
                object_id=user_id, request_id=ctx.request_id, ip_hash=ctx.ip_hash,
            )  # fmt: skip

    async def _start_session(
        self, ctx: RequestCtx, user: UserRow, password: str, keep_signed_in: bool
    ) -> LoginResult:
        async with system_scope(self.engine) as db:
            known_device = (
                await db.execute(
                    text(
                        "SELECT 1 FROM sessions WHERE user_id = CAST(:u AS uuid) "
                        "AND user_agent IS NOT DISTINCT FROM :ua LIMIT 1"
                    ),
                    {"u": user.id, "ua": ctx.user_agent[:255] or None},
                )
            ).first() is not None
            await db.execute(
                text(
                    "UPDATE users SET failed_logins = 0, locked_until = NULL "
                    "WHERE id = CAST(:i AS uuid)"
                ),
                {"i": user.id},
            )
            if security.needs_rehash(user.password_hash or ""):
                await db.execute(
                    text("UPDATE users SET password_hash = :h WHERE id = CAST(:i AS uuid)"),
                    {"h": security.hash_password(password), "i": user.id},
                )
            await events.record(
                db, action="auth.login", actor_id=user.id, actor_role=user.role,
                tenant_id=user.tenant_id, object_type="user", object_id=user.id,
                request_id=ctx.request_id, ip_hash=ctx.ip_hash,
            )  # fmt: skip
        token, data = await self.sessions.create(
            user_id=user.id, role=user.role,
            keep_signed_in=keep_signed_in and user.role == "FARMER",
            ip_hash=ctx.ip_hash, user_agent=ctx.user_agent,
        )  # fmt: skip
        if not known_device:
            await self._new_device_notice(user, ctx)
        if user.role in STAFF:
            confirmed = await self._totp_confirmed(user.id)
            return LoginResult(token, data, "totp" if confirmed else "setup_totp")
        return LoginResult(token, data, "home")

    async def _new_device_notice(self, user: UserRow, ctx: RequestCtx) -> None:
        async with system_scope(self.engine) as db:
            await db.execute(
                text(
                    "INSERT INTO notifications (tenant_id, user_id, kind, security, link_path) "
                    "VALUES (:t, CAST(:u AS uuid), 'new_device', true, '/account/sessions')"
                ),
                {"t": user.tenant_id, "u": user.id},
            )
        if user.email and user.email_verified_at:
            await self.notifier.send_email(
                user_id=user.id, tenant_id=user.tenant_id, to_email=user.email,
                kind="new_device", dedupe_key=f"newdev:{user.id}:{ctx.request_id}",
                name=user.display_name, when=self.now().strftime("%d %b %Y, %H:%M UTC"),
                device=ctx.user_agent or "unknown",
            )  # fmt: skip

    # --- TOTP -------------------------------------------------------------------------------
    async def _totp_confirmed(self, user_id: str) -> bool:
        async with system_scope(self.engine) as db:
            row = (
                await db.execute(
                    text(
                        "SELECT 1 FROM totp_credentials WHERE user_id = CAST(:u AS uuid) "
                        "AND confirmed_at IS NOT NULL"
                    ),
                    {"u": user_id},
                )
            ).first()
        return row is not None

    async def begin_totp_setup(self, user: UserRow, *, replace: bool) -> tuple[str, str]:
        if not replace and await self._totp_confirmed(user.id):
            raise AppError(409, "totp_already_set")
        secret = pyotp.random_base32()
        sealed = security.encrypt(self.s.secret_key, "totp", secret)
        async with system_scope(self.engine) as db:
            await db.execute(
                text(
                    "INSERT INTO totp_credentials (user_id, tenant_id, secret_enc) "
                    "VALUES (CAST(:u AS uuid), :t, :s) ON CONFLICT (user_id) DO UPDATE SET "
                    "secret_enc = EXCLUDED.secret_enc, confirmed_at = NULL, last_used_step = NULL"
                ),
                {"u": user.id, "t": user.tenant_id, "s": sealed},
            )
        uri = pyotp.TOTP(secret).provisioning_uri(
            name=user.email or user.id, issuer_name="Kaktarua"
        )
        return secret, uri

    async def _check_totp(self, user_id: str, code: str, *, allow_unconfirmed: bool) -> bool:
        if not (code.isascii() and code.isdigit() and len(code) == 6):
            return False
        async with system_scope(self.engine) as db:
            row = (
                await db.execute(
                    text(
                        "SELECT secret_enc, confirmed_at, last_used_step FROM totp_credentials "
                        "WHERE user_id = CAST(:u AS uuid)"
                    ),
                    {"u": user_id},
                )
            ).first()
            if row is None or (row[1] is None and not allow_unconfirmed):
                return False
            secret = security.decrypt(self.s.secret_key, "totp", row[0])
            current = int(self.now().timestamp()) // 30
            totp = pyotp.TOTP(secret)
            for step in (current - 1, current, current + 1):
                if security.safe_equal(totp.at(step * 30), code):
                    if row[2] is not None and step <= row[2]:
                        return False  # replay of an already-used code
                    claimed = await db.execute(
                        text(
                            "UPDATE totp_credentials SET last_used_step = :s WHERE "
                            "user_id = CAST(:u AS uuid) AND (last_used_step IS NULL OR "
                            "last_used_step < :s) RETURNING 1"
                        ),
                        {"s": step, "u": user_id},
                    )
                    return claimed.first() is not None
        return False

    def _new_recovery_code(self) -> str:
        alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
        raw = "".join(secrets.choice(alphabet) for _ in range(10))
        return f"{raw[:5]}-{raw[5:]}"

    async def _issue_recovery_codes(self, user: UserRow) -> list[str]:
        codes = [self._new_recovery_code() for _ in range(RECOVERY_CODE_COUNT)]
        hashes = [security.hash_password(c) for c in codes]
        async with system_scope(self.engine) as db:
            await db.execute(
                text("DELETE FROM recovery_codes WHERE user_id = CAST(:u AS uuid)"),
                {"u": user.id},
            )
            for h in hashes:
                await db.execute(
                    text(
                        "INSERT INTO recovery_codes (tenant_id, user_id, code_hash) "
                        "VALUES (:t, CAST(:u AS uuid), :h)"
                    ),
                    {"t": user.tenant_id, "u": user.id, "h": h},
                )
        return codes

    async def confirm_totp(
        self, ctx: RequestCtx, session: SessionData, user: UserRow, code: str
    ) -> tuple[list[str], str, SessionData]:
        await self.limiter.enforce("totp_verify", user.id)
        if not await self._check_totp(user.id, code, allow_unconfirmed=True):
            raise AppError(400, "totp_invalid")
        async with system_scope(self.engine) as db:
            await db.execute(
                text(
                    "UPDATE totp_credentials SET confirmed_at = :now "
                    "WHERE user_id = CAST(:u AS uuid)"
                ),
                {"now": self.now(), "u": user.id},
            )
            await events.record(
                db, action="auth.totp_enabled", actor_id=user.id, actor_role=user.role,
                object_type="user", object_id=user.id, request_id=ctx.request_id,
                ip_hash=ctx.ip_hash,
            )  # fmt: skip
        codes = await self._issue_recovery_codes(user)
        token, fresh = await self.sessions.mark_totp_verified(session)
        return codes, token, fresh

    async def _use_recovery_code(self, user_id: str, code: str) -> bool:
        async with system_scope(self.engine) as db:
            rows = (
                await db.execute(
                    text(
                        "SELECT id::text, code_hash FROM recovery_codes "
                        "WHERE user_id = CAST(:u AS uuid) AND used_at IS NULL"
                    ),
                    {"u": user_id},
                )
            ).all()
            for rid, code_hash in rows:
                if security.verify_password(code_hash, code.strip().lower()):
                    claimed = await db.execute(
                        text(
                            "UPDATE recovery_codes SET used_at = :now WHERE id = CAST(:i AS uuid) "
                            "AND used_at IS NULL RETURNING 1"
                        ),
                        {"now": self.now(), "i": rid},
                    )
                    return claimed.first() is not None
        return False

    async def login_totp(
        self, ctx: RequestCtx, session: SessionData, user: UserRow, *, code: str, recovery: bool
    ) -> tuple[str, SessionData]:
        await self.limiter.enforce("totp_verify", user.id)
        ok = (
            await self._use_recovery_code(user.id, code)
            if recovery
            else await self._check_totp(user.id, code, allow_unconfirmed=False)
        )
        if not ok:
            raise AppError(400, "totp_invalid")
        async with system_scope(self.engine) as db:
            await events.record(
                db, action="auth.totp_login", actor_id=user.id, actor_role=user.role,
                object_type="user", object_id=user.id, request_id=ctx.request_id,
                ip_hash=ctx.ip_hash, after={"recovery_code": recovery},
            )  # fmt: skip
        return await self.sessions.mark_totp_verified(session)

    async def step_up(
        self, ctx: RequestCtx, session: SessionData, user: UserRow, *, code: str
    ) -> tuple[str, SessionData]:
        await self.limiter.enforce("step_up", user.id)
        if not await self._check_totp(user.id, code, allow_unconfirmed=False):
            raise AppError(400, "totp_invalid")
        async with system_scope(self.engine) as db:
            await events.record(
                db, action="auth.step_up", actor_id=user.id, actor_role=user.role,
                object_type="user", object_id=user.id, request_id=ctx.request_id,
                ip_hash=ctx.ip_hash,
            )  # fmt: skip
        return await self.sessions.mark_step_up(session)

    async def regenerate_recovery_codes(self, ctx: RequestCtx, user: UserRow) -> list[str]:
        codes = await self._issue_recovery_codes(user)
        async with system_scope(self.engine) as db:
            await events.record(
                db, action="auth.recovery_codes_regenerated", actor_id=user.id,
                actor_role=user.role, object_type="user", object_id=user.id,
                request_id=ctx.request_id, ip_hash=ctx.ip_hash,
            )  # fmt: skip
        return codes

    # --- email tokens, password reset -------------------------------------------------------
    async def _issue_email_token(self, user: UserRow, purpose: str, ttl: timedelta) -> str:
        token = security.new_token(32)
        async with system_scope(self.engine) as db:
            await db.execute(
                text(
                    "UPDATE email_tokens SET consumed_at = :now WHERE user_id = CAST(:u AS uuid) "
                    "AND purpose = :p AND consumed_at IS NULL"
                ),
                {"now": self.now(), "u": user.id, "p": purpose},
            )
            await db.execute(
                text(
                    "INSERT INTO email_tokens (tenant_id, user_id, purpose, token_hash, "
                    "expires_at) VALUES (:t, CAST(:u AS uuid), :p, :h, :e)"
                ),
                {"t": user.tenant_id, "u": user.id, "p": purpose,
                 "h": security.sha256_hex(token), "e": self.now() + ttl},
            )  # fmt: skip
        return token

    async def _peek_email_token(self, token: str, purpose: str) -> str | None:
        async with system_scope(self.engine) as db:
            row = (
                await db.execute(
                    text(
                        "SELECT user_id::text FROM email_tokens WHERE token_hash = :h "
                        "AND purpose = :p AND consumed_at IS NULL AND expires_at > :now"
                    ),
                    {"now": self.now(), "h": security.sha256_hex(token), "p": purpose},
                )
            ).first()
        return row[0] if row else None

    async def _consume_email_token(self, token: str, purpose: str) -> str | None:
        """Single use: returns the user id once, then never again."""
        async with system_scope(self.engine) as db:
            row = (
                await db.execute(
                    text(
                        "UPDATE email_tokens SET consumed_at = :now WHERE token_hash = :h "
                        "AND purpose = :p AND consumed_at IS NULL AND expires_at > :now "
                        "RETURNING user_id::text"
                    ),
                    {"now": self.now(), "h": security.sha256_hex(token), "p": purpose},
                )
            ).first()
        return row[0] if row else None

    def _link(self, path: str, token: str) -> str:
        return f"{self.s.origin_for_links}{path}?token={token}"

    async def request_email_verification(self, user: UserRow) -> None:
        if not user.email or user.email_verified_at:
            return
        await self.limiter.enforce("email_token", f"user:{user.id}")
        token = await self._issue_email_token(user, "verify", VERIFY_TTL)
        await self.notifier.send_email(
            user_id=user.id, tenant_id=user.tenant_id, to_email=user.email, kind="verify",
            dedupe_key=f"verify:{security.sha256_hex(token)[:24]}", name=user.display_name,
            link=self._link("/verify-email", token),
        )  # fmt: skip

    async def verify_email(self, ctx: RequestCtx, token: str) -> None:
        await self.limiter.enforce("email_token", f"ip:{ctx.ip}")
        user_id = await self._consume_email_token(token, "verify")
        if user_id is None:
            raise AppError(400, "token_invalid")
        async with system_scope(self.engine) as db:
            await db.execute(
                text("UPDATE users SET email_verified_at = :n WHERE id = CAST(:i AS uuid)"),
                {"n": self.now(), "i": user_id},
            )

    async def forgot_password(self, ctx: RequestCtx, *, identifier: str) -> None:
        """Always the same outcome for the caller (202), whatever the account state."""
        column, value = self._identify(identifier)
        await self.limiter.enforce("password_reset", f"{column}:{value}")
        await self.limiter.enforce("password_reset", f"ip:{ctx.ip}")
        async with system_scope(self.engine) as db:
            user = await self._by(db, column, value)
        if user is None or user.status != "ACTIVE" or user.role.startswith("DEMO"):
            return
        if column == "email" and user.email:
            token = await self._issue_email_token(user, "reset", RESET_TTL)
            await self.notifier.send_email(
                user_id=user.id, tenant_id=user.tenant_id, to_email=user.email, kind="reset",
                dedupe_key=f"reset:{security.sha256_hex(token)[:24]}", name=user.display_name,
                link=self._link("/reset-password", token),
            )  # fmt: skip
        elif column == "phone_e164" and user.phone:
            await self._issue_otp(ctx, user.id, user.phone, "reset", user.locale)

    async def reset_password(
        self, ctx: RequestCtx, *, new_password: str, token: str | None, phone: str | None,
        code: str | None,
    ) -> None:  # fmt: skip
        user: UserRow | None = None
        if token:
            await self.limiter.enforce("email_token", f"ip:{ctx.ip}")
            user_id = await self._peek_email_token(token, "reset")
            user = await self.get_user(user_id) if user_id else None
            if user is not None and user.status == "ACTIVE":
                self._require_strong(user, new_password)  # a weak password must not burn the token
                if await self._consume_email_token(token, "reset") is None:
                    user = None
        elif phone and code:
            try:
                e164 = normalise_phone(phone)
            except PhoneError as exc:
                raise AppError(400, "reset_invalid") from exc
            await self.limiter.enforce("otp_verify", f"phone:{e164}")
            await self.limiter.enforce("otp_verify", f"ip:{ctx.ip}")
            async with system_scope(self.engine) as db:
                candidate = await self._by(db, "phone_e164", e164)
            if (
                candidate
                and candidate.status == "ACTIVE"
                and await self._consume_otp(candidate.id, "reset", code, burn=False)
            ):
                self._require_strong(candidate, new_password)  # ...nor burn the code
                if await self._consume_otp(candidate.id, "reset", code):
                    user = candidate
        if user is None or user.status != "ACTIVE":
            raise AppError(400, "reset_invalid")
        await self._set_password(ctx, user, new_password, revoke_except=None)

    def _require_strong(self, user: UserRow, password: str) -> None:
        level: security.PolicyLevel = "staff" if user.role in STAFF else "farmer"
        inputs = [user.display_name, user.email or "", user.phone or ""]
        verdict = security.check_password(password, level, inputs)
        if not verdict.ok:
            raise AppError(422, "password_weak", extra={"reason": verdict.code})

    async def _set_password(
        self, ctx: RequestCtx, user: UserRow, new_password: str, *, revoke_except: str | None
    ) -> None:
        self._require_strong(user, new_password)
        new_hash = security.hash_password(new_password)
        async with system_scope(self.engine) as db:
            await db.execute(
                text(
                    "UPDATE users SET password_hash = :h, failed_logins = 0, locked_until = NULL "
                    "WHERE id = CAST(:i AS uuid)"
                ),
                {"h": new_hash, "i": user.id},
            )
            await events.record(
                db, action="auth.password_changed", actor_id=user.id, actor_role=user.role,
                tenant_id=user.tenant_id, object_type="user", object_id=user.id,
                request_id=ctx.request_id, ip_hash=ctx.ip_hash,
            )  # fmt: skip
        await self.sessions.revoke_all(user.id, except_id=revoke_except)
        for column, value in (("phone_e164", user.phone), ("email", user.email)):
            if value:
                await self._clear_failures(
                    f"{column}:{value.lower() if column == 'email' else value}"
                )

    async def change_password(
        self, ctx: RequestCtx, session: SessionData, user: UserRow, *, current: str, new: str
    ) -> tuple[str, SessionData]:
        await self.limiter.enforce("login", f"change|{user.id}")
        if not security.verify_password(user.password_hash, current):
            raise AppError(400, "current_password_wrong")
        await self._set_password(ctx, user, new, revoke_except=session.id)
        return await self.sessions.rotate(session, ip_hash=ctx.ip_hash, user_agent=ctx.user_agent)

    # --- staff invitation -------------------------------------------------------------------
    async def create_invite(
        self, ctx: RequestCtx, admin: UserRow, *, email: str, role: str, regions: list[str]
    ) -> tuple[str, datetime]:
        email = email.strip().lower()
        if role not in STAFF:
            raise AppError(422, "role_invalid")
        token = security.new_token(32)
        expires = self.now() + INVITE_TTL
        async with system_scope(self.engine) as db:
            taken = await self._by(db, "email", email)
            if taken is not None:
                raise AppError(409, "conflict")
            await db.execute(  # a newer invite replaces older ones for the same address
                text(
                    "UPDATE invites SET consumed_at = :now WHERE email = :e AND consumed_at IS NULL"
                ),
                {"now": self.now(), "e": email},
            )
            invite_id = str(uuid7(self.now()))
            await db.execute(
                text(
                    "INSERT INTO invites (id, tenant_id, user_id, email, role, region_codes, "
                    "token_hash, expires_at) VALUES (CAST(:id AS uuid), 'real', CAST(:a AS uuid), "
                    ":e, :r, :rc, :h, :x)"
                ),
                {"id": invite_id, "a": admin.id, "e": email, "r": role, "rc": regions,
                 "h": security.sha256_hex(token), "x": expires},
            )  # fmt: skip
            await events.record(
                db, action="admin.invite_created", actor_id=admin.id, actor_role="ADMIN",
                object_type="invite", object_id=invite_id, request_id=ctx.request_id,
                ip_hash=ctx.ip_hash, after={"role": role},
            )  # fmt: skip
        await self.notifier.send_email(
            user_id=None, tenant_id="real", to_email=email, kind="invite",
            dedupe_key=f"invite:{invite_id}",
            role_bn="পর্যালোচক" if role == "REVIEWER" else "প্রশাসক",
            role_en="a reviewer" if role == "REVIEWER" else "an administrator",
            link=self._link("/accept-invite", token),
        )  # fmt: skip
        return invite_id, expires

    async def register_staff(
        self, ctx: RequestCtx, *, token: str, password: str, display_name: str, locale: str
    ) -> None:
        await self.limiter.enforce("register", ctx.ip)
        token_hash = security.sha256_hex(token)
        async with system_scope(self.engine) as db:
            invite = (
                await db.execute(
                    text(
                        "SELECT id::text, email, role, region_codes FROM invites WHERE "
                        "token_hash = :h AND consumed_at IS NULL AND expires_at > :now"
                    ),
                    {"h": token_hash, "now": self.now()},
                )
            ).first()
        if invite is None:
            raise AppError(400, "invite_invalid")
        verdict = security.check_password(password, "staff", [display_name, invite[1]])
        if not verdict.ok:
            raise AppError(422, "password_weak", extra={"reason": verdict.code})
        pw_hash = security.hash_password(password)
        user_id = str(uuid7(self.now()))
        async with system_scope(self.engine) as db:
            claimed = await db.execute(
                text(
                    "UPDATE invites SET consumed_at = :now WHERE id = CAST(:i AS uuid) "
                    "AND consumed_at IS NULL RETURNING 1"
                ),
                {"now": self.now(), "i": invite[0]},
            )
            if claimed.first() is None:
                raise AppError(400, "invite_invalid")  # lost a race: single use
            await db.execute(
                text(
                    "INSERT INTO users (id, tenant_id, role, email, display_name, locale, "
                    "password_hash, status, region_codes, email_verified_at) VALUES "
                    "(CAST(:id AS uuid), 'real', :r, :e, :n, :l, :h, 'ACTIVE', :rc, :now)"
                ),
                {"id": user_id, "r": invite[2], "e": invite[1], "n": display_name.strip(),
                 "l": locale, "h": pw_hash, "rc": list(invite[3] or ()), "now": self.now()},
            )  # fmt: skip
            await events.record(
                db, action="auth.register_staff", actor_id=user_id, actor_role=invite[2],
                object_type="user", object_id=user_id, request_id=ctx.request_id,
                ip_hash=ctx.ip_hash,
            )  # fmt: skip

    # --- misc -------------------------------------------------------------------------------
    async def logout(self, ctx: RequestCtx, session: SessionData) -> None:
        await self.sessions.revoke(session.id, session.user_id)
        async with system_scope(self.engine) as db:
            await events.record(
                db, action="auth.logout", actor_id=session.user_id, actor_role=session.role,
                tenant_id=session.tenant_id, object_type="session", object_id=session.id,
                request_id=ctx.request_id, ip_hash=ctx.ip_hash,
            )  # fmt: skip

    async def logout_all(self, ctx: RequestCtx, session: SessionData) -> int:
        if session.tenant_id == "demo":
            # demo users are shared by every visitor: "all sessions" would sign other people out
            count = 1 if await self.sessions.revoke(session.id, session.user_id) else 0
        else:
            count = await self.sessions.revoke_all(session.user_id)
        async with system_scope(self.engine) as db:
            await events.record(
                db, action="auth.logout_all", actor_id=session.user_id, actor_role=session.role,
                tenant_id=session.tenant_id, object_type="user", object_id=session.user_id,
                request_id=ctx.request_id, ip_hash=ctx.ip_hash, after={"revoked": count},
            )  # fmt: skip
        return count

    async def has_totp(self, user_id: str) -> bool:
        return await self._totp_confirmed(user_id)

    def tenant(self, role: str) -> str:
        return tenant_for(role)
