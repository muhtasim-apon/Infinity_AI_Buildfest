"""Scan lifecycle: create → (browser uploads to signed URL) → analyze → read.

Contract: services/api/openapi-outline.md §Scans. Sequence: docs/architecture/sequence-diagrams.md §1.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Header

from app.schemas.scan import AnalyzeOut, ScanCreateIn, ScanCreateOut, ScanPage
from app.security.auth import CurrentUser, require_role

router = APIRouter(prefix="/v1/scans", tags=["scans"])


@router.post("", response_model=ScanCreateOut, status_code=201)
async def create_scan(
    body: ScanCreateIn,
    user: CurrentUser = Depends(require_role("farmer", "demo", "agronomist")),
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
) -> ScanCreateOut:
    """Insert ``scans`` row (pending_upload) and return a 5-minute signed upload URL.

    Idempotent on ``(user_id, sha256)``: an existing scan is returned with 200.
    Rate limited: ``rate_limit_scans_per_hour``.
    """
    raise NotImplementedError


@router.post("/{scan_id}/analyze", response_model=AnalyzeOut)
async def analyze_scan(scan_id: UUID, user: CurrentUser = Depends(require_role("farmer", "demo", "agronomist"))) -> AnalyzeOut:
    """Validate image → infer → decide (abstain?) → advise (RAG) → persist → outbreak check.

    Budget 25 s. Inference timeout → 503 + Retry-After (scan stays ``uploaded``).
    LLM failure → diagnosis returned with ``advisory.status = "fallback"``.
    Owner-only (IDOR guard, threat T9).
    """
    raise NotImplementedError


@router.get("", response_model=ScanPage)
async def list_scans(limit: int = 20, cursor: str | None = None,
                     user: CurrentUser = Depends(require_role("farmer", "demo", "agronomist"))) -> ScanPage:
    """Caller's history, newest first. ``limit`` 1..50."""
    raise NotImplementedError


@router.get("/{scan_id}", response_model=AnalyzeOut)
async def get_scan(scan_id: UUID, user: CurrentUser = Depends(require_role("farmer", "demo", "agronomist", "admin"))) -> AnalyzeOut:
    """Owner, regional agronomist or admin only."""
    raise NotImplementedError
