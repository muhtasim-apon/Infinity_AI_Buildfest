"""One-click audit report — sections in docs/security/audit-readiness.md.

Numbers not yet measured are rendered as "not yet measured", never as placeholders.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Depends

from app.security.auth import CurrentUser, require_role

router = APIRouter(prefix="/v1/audit", tags=["audit"])


@router.get("/report")
async def audit_report(format: Literal["json", "html"] = "json",
                       user: CurrentUser = Depends(require_role("admin", "demo"))) -> dict[str, object]:
    """Demo role sees the report built over synthetic data only. Budget 10 s."""
    raise NotImplementedError
