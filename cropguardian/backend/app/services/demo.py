"""Demo tenant (spec 16.4, 2.2): three fixed demo users in `tenant_id='demo'`, entered by one click.

Demo users have no password and no phone/email contact, so they can never sign in through /login.
A demo session is short, bound to the demo tenant by RLS, and cannot invite, export or change
settings (see `authz.POLICIES`). Data created in the demo tenant is wiped nightly (Phase 8 job).
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.errors import AppError
from app.core.sessions import SessionData, SessionStore
from app.db.session import system_scope
from app.services.auth import RequestCtx

DEMO_USERS = {
    "DEMO_FARMER": ("00000000-0000-7000-8000-00000000d001", "ডেমো কৃষক", None),
    "DEMO_REVIEWER": (
        "00000000-0000-7000-8000-00000000d002", "ডেমো পর্যালোচক", "demo-reviewer@demo.invalid"
    ),
    "DEMO_ADMIN": (
        "00000000-0000-7000-8000-00000000d003", "ডেমো প্রশাসক", "demo-admin@demo.invalid"
    ),
}  # fmt: skip


async def seed_demo_users(engine: AsyncEngine) -> int:
    """Idempotent. Returns the number of demo users that now exist."""
    async with system_scope(engine) as db:
        for role, (uid, name, email) in DEMO_USERS.items():
            await db.execute(
                text(
                    "INSERT INTO users (id, tenant_id, role, email, display_name, locale, status, "
                    "region_codes, email_verified_at) VALUES (CAST(:id AS uuid), 'demo', :r, :e, "
                    ":n, 'bn', 'ACTIVE', ARRAY['DEMO'], "
                    "CASE WHEN CAST(:e AS text) IS NULL THEN NULL ELSE now() END) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": uid, "r": role, "e": email, "n": name},
            )
        count = (
            await db.execute(text("SELECT count(*) FROM users WHERE tenant_id = 'demo'"))
        ).scalar_one()
    return int(count)


async def start_demo_session(
    engine: AsyncEngine, sessions: SessionStore, ctx: RequestCtx, role: str
) -> tuple[str, SessionData]:
    if role not in DEMO_USERS:
        raise AppError(422, "role_invalid")
    async with system_scope(engine) as db:
        row = (
            await db.execute(
                text(
                    "SELECT id::text FROM users WHERE id = CAST(:i AS uuid) AND role = :r "
                    "AND tenant_id = 'demo' AND status = 'ACTIVE'"
                ),
                {"i": DEMO_USERS[role][0], "r": role},
            )
        ).first()
    if row is None:
        raise AppError(503, "demo_unavailable", "Demo data is not ready yet.")
    return await sessions.create(
        user_id=row[0], role=role, ip_hash=ctx.ip_hash, user_agent=ctx.user_agent
    )
