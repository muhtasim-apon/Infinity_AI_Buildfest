"""One authorization module (spec 16.5). Every route and service goes through `authorize`.

Rules:
- Not signed in -> 401. Wrong role -> 403, except admin-only areas which answer 404 (their existence
  is not revealed). Somebody else's record (owner, tenant or region) -> 404, never 403, so ids
  cannot be probed.
- Staff accounts need a verified TOTP session; sensitive actions also need a fresh step-up.
- A new action must be registered here; an unknown action is refused (deny by default).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from app.core.errors import AppError
from app.core.sessions import SessionData
from app.core.tenancy import DEMO_ROLES, base_role

STAFF = frozenset({"reviewer", "admin"})


@dataclass(frozen=True)
class Principal:
    user_id: str
    role: str  # FARMER | REVIEWER | ADMIN | DEMO_*
    tenant_id: str
    region_codes: tuple[str, ...]
    session_id: str
    locale: str
    totp_verified: bool
    step_up: bool

    @property
    def base(self) -> str:
        return base_role(self.role)

    @property
    def is_demo(self) -> bool:
        return self.role in DEMO_ROLES

    @property
    def needs_totp(self) -> bool:
        """Real staff must complete 2FA; demo staff are exempt (no real data, no real power)."""
        return self.base in STAFF and not self.is_demo


def principal_from_session(data: SessionData, now: datetime) -> Principal:
    return Principal(
        user_id=data.user_id,
        role=data.role,
        tenant_id=data.tenant_id,
        region_codes=data.region_codes,
        session_id=data.id,
        locale=data.locale,
        totp_verified=data.totp_verified_at is not None,
        step_up=data.step_up_valid(now),
    )


@dataclass(frozen=True)
class Resource:
    owner_id: str | None = None
    tenant_id: str | None = None
    region_code: str | None = None


@dataclass(frozen=True)
class Policy:
    roles: frozenset[str]  # base roles: farmer | reviewer | admin
    owner_only: bool = False
    region_scoped: bool = False
    step_up: bool = False
    hide_as_404: bool = False  # role failure answers 404 (admin area)
    allow_demo: bool = True
    pre_totp: bool = False  # usable before the staff member has completed 2FA (setup / login)


POLICIES: dict[str, Policy] = {
    "me:read": Policy(frozenset({"farmer", "reviewer", "admin"})),
    "me:update": Policy(frozenset({"farmer", "reviewer", "admin"})),
    "me:sessions": Policy(frozenset({"farmer", "reviewer", "admin"})),
    "me:consents": Policy(frozenset({"farmer"})),
    "auth:logout": Policy(frozenset({"farmer", "reviewer", "admin"})),
    "auth:step_up": Policy(frozenset({"reviewer", "admin"}), allow_demo=False),
    "auth:totp_login": Policy(frozenset({"reviewer", "admin"}), pre_totp=True, allow_demo=False),
    "auth:totp_setup": Policy(frozenset({"reviewer", "admin"}), pre_totp=True, allow_demo=False),
    "auth:recovery_codes": Policy(frozenset({"reviewer", "admin"}), step_up=True, allow_demo=False),
    "scans:create": Policy(frozenset({"farmer"}), owner_only=True),
    "scans:read": Policy(frozenset({"farmer"}), owner_only=True),
    "alerts:read": Policy(frozenset({"farmer", "reviewer", "admin"})),
    # Approving an outbreak alert is the one action that reaches farmers: real staff need a fresh
    # step-up 2FA; the demo reviewer is exempt (demo tenant only, by RLS) - see authorize().
    "alerts:decide": Policy(frozenset({"reviewer", "admin"}), step_up=True),
    "admin:users:list": Policy(frozenset({"admin"}), hide_as_404=True),
    "admin:invites:create": Policy(
        frozenset({"admin"}), step_up=True, hide_as_404=True, allow_demo=False
    ),
}


def authorize(principal: Principal | None, action: str, resource: Resource | None = None) -> None:
    if principal is None:
        raise AppError(401, "authentication_required")
    policy = POLICIES.get(action)
    if policy is None:
        raise AppError(403, "forbidden")  # unregistered action: deny
    if principal.base not in policy.roles or (principal.is_demo and not policy.allow_demo):
        raise AppError(404, "not_found") if policy.hide_as_404 else AppError(403, "forbidden")
    if principal.needs_totp and not principal.totp_verified and not policy.pre_totp:
        raise AppError(403, "totp_required")
    if resource is not None:
        _check_resource(principal, policy, resource)
    if policy.step_up and not principal.step_up and not principal.is_demo:
        raise AppError(403, "step_up_required")


def _check_resource(principal: Principal, policy: Policy, resource: Resource) -> None:
    if resource.tenant_id is not None and resource.tenant_id != principal.tenant_id:
        raise AppError(404, "not_found")
    if policy.owner_only and principal.base != "admin" and resource.owner_id != principal.user_id:
        raise AppError(404, "not_found")
    if (
        policy.region_scoped
        and principal.base == "reviewer"
        and resource.region_code not in principal.region_codes
    ):
        raise AppError(404, "not_found")
