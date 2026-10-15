"""Database access — async pool against Supabase Postgres (pooled connection string).

Rules: parameterised queries only (OWASP A03); each module writes only its own tables
(ADR 0002); pool size small (Supabase free connection limits, challenges B3).
"""

from __future__ import annotations

from typing import Any

from app.config import Settings


async def create_pool(settings: Settings) -> Any:
    """Create an asyncpg pool with ``min_size=1, max_size=settings.db_pool_size``,
    statement timeout 5 s, and register the pgvector codec.

    Failure: raise on connect error; ``/readyz`` reports ``db: "down"``.
    """
    raise NotImplementedError


async def ping(pool: Any) -> bool:
    """``select 1`` with a 2 s timeout. Used by ``/readyz`` and the n8n heartbeat (B1)."""
    raise NotImplementedError
