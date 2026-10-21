"""Signed-in user data. Every query here runs under the caller's own RLS context
(`db_context_for`), so even a bug in this file cannot read another user's rows (spec 16.10)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core import consent_texts
from app.core.authz import Principal
from app.core.clock import utcnow
from app.core.errors import AppError
from app.core.tenancy import db_context_for
from app.db.session import session_scope
from app.domain.phone import mask_phone
from app.services import events

OPTIONAL_CONSENTS = ("training_use", "push_alerts")


@dataclass(frozen=True)
class RequestInfo:
    request_id: str
    ip_hash: str


class UsersService:
    def __init__(self, engine: AsyncEngine) -> None:
        self.engine = engine

    def _scope(self, p: Principal) -> Any:
        return session_scope(self.engine, db_context_for(p.user_id, p.role, p.region_codes))

    async def me(self, p: Principal) -> dict[str, Any]:
        async with self._scope(p) as db:
            row = (
                await db.execute(
                    text(
                        "SELECT id::text, role, display_name, locale, phone_e164, email, status, "
                        "region_codes, email_verified_at, created_at FROM users "
                        "WHERE id = CAST(:i AS uuid)"
                    ),
                    {"i": p.user_id},
                )
            ).first()
        if row is None:
            raise AppError(404, "not_found")
        return {
            "id": row[0], "role": row[1], "display_name": row[2], "locale": row[3],
            "phone": row[4], "email": row[5], "status": row[6], "region_codes": list(row[7] or ()),
            "email_verified": row[8] is not None, "is_demo": p.is_demo,
            "tenant": p.tenant_id,
        }  # fmt: skip

    async def update_me(
        self, p: Principal, info: RequestInfo, *, display_name: str | None, locale: str | None
    ) -> dict[str, Any]:
        async with self._scope(p) as db:
            result = await db.execute(
                text(
                    "UPDATE users SET display_name = COALESCE(:n, display_name), "
                    "locale = COALESCE(:l, locale) WHERE id = CAST(:i AS uuid) RETURNING 1"
                ),
                {"n": display_name, "l": locale, "i": p.user_id},
            )
            if result.first() is None:
                raise AppError(404, "not_found")
            await events.record(
                db, action="user.profile_updated", actor_id=p.user_id, actor_role=p.role,
                tenant_id=p.tenant_id, object_type="user", object_id=p.user_id,
                request_id=info.request_id, ip_hash=info.ip_hash,
            )  # fmt: skip
        return await self.me(p)

    async def consents(self, p: Principal) -> list[dict[str, Any]]:
        async with self._scope(p) as db:
            rows = (
                await db.execute(
                    text(
                        "SELECT purpose, granted, text_version, granted_at, withdrawn_at "
                        "FROM consents WHERE user_id = CAST(:i AS uuid) "
                        "ORDER BY created_at DESC"
                    ),
                    {"i": p.user_id},
                )
            ).all()
        latest: dict[str, tuple[Any, ...]] = {}
        for r in rows:
            latest.setdefault(r[0], tuple(r))
        out = []
        for item in consent_texts.current_texts():
            state = latest.get(item.purpose)
            out.append(
                {
                    "purpose": item.purpose,
                    "required": item.required,
                    "version": consent_texts.CURRENT_VERSION,
                    "title": dict(item.title),
                    "body": dict(item.body),
                    "granted": bool(state[1]) if state else False,
                    "granted_version": state[2] if state else None,
                }
            )
        return out

    async def set_consent(
        self, p: Principal, info: RequestInfo, *, purpose: str, granted: bool
    ) -> list[dict[str, Any]]:
        if purpose not in OPTIONAL_CONSENTS:
            raise AppError(409, "consent_required", "Required consent cannot be withdrawn here.")
        now: datetime = utcnow()
        async with self._scope(p) as db:
            await db.execute(
                text(
                    "INSERT INTO consents (tenant_id, user_id, purpose, granted, text_version, "
                    "granted_at, withdrawn_at) VALUES (:t, CAST(:u AS uuid), :p, :g, :v, :ga, :wa) "
                    "ON CONFLICT (user_id, purpose, text_version) DO UPDATE SET "
                    "granted = EXCLUDED.granted, granted_at = EXCLUDED.granted_at, "
                    "withdrawn_at = EXCLUDED.withdrawn_at"
                ),
                {"t": p.tenant_id, "u": p.user_id, "p": purpose, "g": granted,
                 "v": consent_texts.CURRENT_VERSION, "ga": now if granted else None,
                 "wa": None if granted else now},
            )  # fmt: skip
            await events.record(
                db, action="consent.granted" if granted else "consent.withdrawn",
                actor_id=p.user_id, actor_role=p.role, tenant_id=p.tenant_id,
                object_type="consent", object_id=purpose, request_id=info.request_id,
                ip_hash=info.ip_hash, after={"version": consent_texts.CURRENT_VERSION},
            )  # fmt: skip
        return await self.consents(p)

    async def admin_list_users(
        self, p: Principal, *, limit: int, offset: int
    ) -> list[dict[str, Any]]:
        async with self._scope(p) as db:
            rows = (
                await db.execute(
                    text(
                        "SELECT id::text, role, display_name, status, phone_e164, email, "
                        "created_at FROM users ORDER BY created_at DESC, id LIMIT :l OFFSET :o"
                    ),
                    {"l": limit, "o": offset},
                )
            ).all()
        return [
            {
                "id": r[0], "role": r[1], "display_name": r[2], "status": r[3],
                # admins see masked contact details only (spec 16.5)
                "phone": mask_phone(r[4]) if r[4] else None,
                "email": _mask_email(r[5]) if r[5] else None,
                "created_at": r[6].isoformat(),
            }
            for r in rows
        ]  # fmt: skip

    async def sessions_view(self, p: Principal) -> list[dict[str, Any]]:
        async with self._scope(p) as db:
            rows = (
                await db.execute(
                    text(
                        "SELECT s.id::text, s.created_at, s.last_seen_at, s.user_agent FROM "
                        "sessions s WHERE s.user_id = CAST(:u AS uuid) AND s.revoked_at IS NULL "
                        "AND (:tenant <> 'demo' OR s.id = CAST(:sid AS uuid)) "
                        "AND s.expires_at > now() AND NOT EXISTS (SELECT 1 FROM sessions n "
                        "WHERE n.rotated_from = s.id AND n.revoked_at IS NULL) "
                        "ORDER BY s.last_seen_at DESC"
                    ),
                    {"u": p.user_id, "tenant": p.tenant_id, "sid": p.session_id},
                )
            ).all()
        return [
            {
                "id": r[0], "created_at": r[1].isoformat(), "last_seen_at": r[2].isoformat(),
                "device": (r[3] or "")[:80], "current": r[0] == p.session_id,
            }
            for r in rows
        ]  # fmt: skip


def _mask_email(email: str) -> str:
    local, _, domain = email.partition("@")
    return f"{local[:1]}***@{domain}"
