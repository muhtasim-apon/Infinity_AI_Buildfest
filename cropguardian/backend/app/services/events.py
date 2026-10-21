"""Audit trail writes (spec 7.6). The DB trigger chains and seals each row; this only inserts."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def record(
    db: AsyncSession,
    *,
    action: str,
    actor_id: str | None = None,
    actor_role: str | None = None,
    tenant_id: str = "real",
    object_type: str | None = None,
    object_id: str | None = None,
    request_id: str | None = None,
    ip_hash: str | None = None,
    before: dict[str, Any] | None = None,
    after: dict[str, Any] | None = None,
) -> None:
    """Never put secrets, phones, emails or free text into before/after: ids and states only."""
    await db.execute(
        text(
            "INSERT INTO audit_log (actor_id, actor_role, tenant_id, action, object_type, "
            "object_id, request_id, ip_hash, before, after) VALUES (:actor, :role, :tenant, "
            ":action, :otype, :oid, :rid, :ip, CAST(:before AS jsonb), CAST(:after AS jsonb))"
        ),
        {
            "actor": actor_id, "role": actor_role, "tenant": tenant_id, "action": action,
            "otype": object_type, "oid": object_id, "rid": request_id, "ip": ip_hash,
            "before": json.dumps(before) if before is not None else None,
            "after": json.dumps(after) if after is not None else None,
        },
    )  # fmt: skip
