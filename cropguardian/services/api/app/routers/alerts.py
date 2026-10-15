"""Outbreak alerts. Drafts are created by ``services/outbreak.py``; only an agronomist can
approve, which triggers the n8n fan-out webhook (no PII in payload)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.schemas.alert import AlertApproveIn, AlertList
from app.security.auth import CurrentUser, require_role

router = APIRouter(prefix="/v1/alerts", tags=["alerts"])


@router.get("", response_model=AlertList)
async def alerts_near(lat: float, lon: float,
                      user: CurrentUser = Depends(require_role("farmer", "demo", "agronomist", "admin"))) -> AlertList:
    """Approved/sent alerts whose radius covers the coarse point."""
    raise NotImplementedError


@router.get("/drafts", response_model=AlertList)
async def drafts(user: CurrentUser = Depends(require_role("agronomist", "admin"))) -> AlertList:
    raise NotImplementedError


@router.post("/{alert_id}/approve")
async def approve(alert_id: UUID, body: AlertApproveIn,
                  user: CurrentUser = Depends(require_role("agronomist", "admin"))) -> dict[str, str]:
    """Atomically ``draft → approved`` (only one approval wins), audit, then POST to n8n."""
    raise NotImplementedError


@router.post("/{alert_id}/dismiss")
async def dismiss(alert_id: UUID, user: CurrentUser = Depends(require_role("agronomist", "admin"))) -> dict[str, str]:
    raise NotImplementedError
