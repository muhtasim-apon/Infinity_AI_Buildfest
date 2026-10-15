"""JWT verification and role guards (threats T1, T7; OWASP A01, A07).

Supabase issues the JWT. We verify signature (``SUPABASE_JWT_SECRET`` / JWKS), ``exp``,
``aud="authenticated"``; then load ``profiles.role`` (the DB is the source of truth for role,
not a client-editable claim).
"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from fastapi import Request

Role = str  # "farmer" | "agronomist" | "admin" | "demo"


@dataclass(frozen=True)
class CurrentUser:
    id: UUID
    role: Role
    upazila: str | None
    locale: str


async def current_user(request: Request) -> CurrentUser:
    """Parse ``Authorization: Bearer``; 401 problem+json on missing/invalid/expired token."""
    raise NotImplementedError


def require_role(*allowed: Role) -> Callable[[Request], Coroutine[Any, Any, CurrentUser]]:
    """Dependency factory: 403 unless ``user.role`` is in ``allowed``. Deny by default."""

    async def dependency(request: Request) -> CurrentUser:
        raise NotImplementedError

    return dependency
