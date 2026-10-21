"""Async engine + session dependency with `SET LOCAL ROLE` and transaction-local context.

Why SET LOCAL: with Supabase's transaction pooler a connection is shared between requests, so
role and `app.*` settings must be transaction-scoped or they would leak between users.
"""

from __future__ import annotations

import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from sqlalchemy import MetaData, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import Settings

# Deterministic constraint names keep Alembic autogenerate diffs stable.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
metadata = MetaData(naming_convention=NAMING_CONVENTION)

ALLOWED_ROLES = frozenset({"cg_app", "cg_worker", "cg_readonly"})
_TENANTS = frozenset({"real", "demo"})
_SAFE_CSV = re.compile(r"^[A-Za-z0-9_,.-]*$")


@dataclass(frozen=True)
class DbContext:
    """Per-request identity pushed into Postgres. Missing user/tenant => RLS matches nothing."""

    user_id: str = ""
    role: str = ""
    tenant: str = ""
    region_csv: str = ""

    def validate(self) -> None:
        if self.tenant and self.tenant not in _TENANTS:
            raise ValueError("invalid tenant")
        if not _SAFE_CSV.match(self.region_csv) or not _SAFE_CSV.match(self.user_id):
            raise ValueError("invalid characters in db context")


def normalise_async_url(url: str) -> str:
    """Accept postgres:// or postgresql:// URLs from dashboards; force the asyncpg driver."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+asyncpg://" + url[len(prefix) :]
    return url


def make_engine(settings: Settings) -> AsyncEngine:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL not configured")
    return create_async_engine(
        normalise_async_url(settings.database_url),
        pool_size=settings.db_pool_size,
        max_overflow=0,
        pool_pre_ping=True,
        connect_args={
            # transaction pooler (pgbouncer/supavisor) cannot use prepared statements
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
            "timeout": 5,
            "server_settings": {
                "statement_timeout": "5000",
                "lock_timeout": "3000",
                "idle_in_transaction_session_timeout": "10000",
            },
        },
    )


@asynccontextmanager
async def session_scope(
    engine: AsyncEngine, ctx: DbContext, role: str = "cg_app"
) -> AsyncIterator[AsyncSession]:
    if (
        role not in ALLOWED_ROLES
    ):  # role names are interpolated into SET LOCAL ROLE: allow-list only
        raise ValueError("role not allowed")
    ctx.validate()
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session, session.begin():
        await session.execute(text(f"SET LOCAL ROLE {role}"))
        await session.execute(
            text(
                "SELECT set_config('app.user_id', :uid, true), "
                "set_config('app.role', :role, true), "
                "set_config('app.tenant', :tenant, true), set_config('app.region', :region, true)"
            ),
            {"uid": ctx.user_id, "role": ctx.role, "tenant": ctx.tenant, "region": ctx.region_csv},
        )
        yield session
