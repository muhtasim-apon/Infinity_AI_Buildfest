"""Roles, tenants and the database context derived from them (spec 2, 16.10)."""

from __future__ import annotations

from typing import Literal

from app.db.session import DbContext

Role = Literal["FARMER", "REVIEWER", "ADMIN", "DEMO_FARMER", "DEMO_REVIEWER", "DEMO_ADMIN"]
ROLES: tuple[Role, ...] = (
    "FARMER",
    "REVIEWER",
    "ADMIN",
    "DEMO_FARMER",
    "DEMO_REVIEWER",
    "DEMO_ADMIN",
)
DEMO_ROLES = frozenset({"DEMO_FARMER", "DEMO_REVIEWER", "DEMO_ADMIN"})
_BASE = {
    "FARMER": "farmer", "DEMO_FARMER": "farmer",
    "REVIEWER": "reviewer", "DEMO_REVIEWER": "reviewer",
    "ADMIN": "admin", "DEMO_ADMIN": "admin",
}  # fmt: skip


def tenant_for(role: str) -> str:
    return "demo" if role in DEMO_ROLES else "real"


def base_role(role: str) -> str:
    """farmer | reviewer | admin: what the policies and RLS compare against (never 'system')."""
    return _BASE[role]


def db_context_for(user_id: str, role: str, region_codes: tuple[str, ...] = ()) -> DbContext:
    """The only way request code obtains a DB context. 'system' cannot be produced here."""
    return DbContext(
        user_id=user_id,
        role=base_role(role),
        tenant=tenant_for(role),
        region_csv=",".join(region_codes),
    )
