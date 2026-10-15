"""Audit chain helpers (threat T8). Appends go through the SQL function ``audit_append``
(db/schema.sql), which serialises with an advisory lock so the chain stays linear under
concurrency (tests/concurrency/test_audit_chain_parallel.py).

``detail`` must never contain phone numbers or coordinates — enforced by ``scrub()``.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID


def scrub(detail: dict[str, Any]) -> dict[str, Any]:
    """Drop keys in {phone, phone_e164, lat, lon, email, display_name}; recurse into dicts."""
    raise NotImplementedError


async def append(actor_id: UUID | None, action: str, entity: str, entity_id: str | None, detail: dict[str, Any]) -> int:
    raise NotImplementedError


async def verify_chain() -> tuple[bool, int | None]:
    """Recompute hashes in id order. Return ``(ok, first_broken_id)``."""
    raise NotImplementedError
