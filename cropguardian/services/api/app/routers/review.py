"""Agronomist review loop (ADR 0005). Every verdict → ``expert_reviews`` (+ ``feedback_labels``
when consented) + ``audit_log``. Concurrent reviews of one scan are both stored; conflicting
labels resolve to ``unclear`` (tests/concurrency)."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.schemas.review import ReviewIn, ReviewQueue
from app.security.auth import CurrentUser, require_role

router = APIRouter(prefix="/v1/review", tags=["review"])


@router.get("/queue", response_model=ReviewQueue)
async def review_queue(user: CurrentUser = Depends(require_role("agronomist", "admin"))) -> ReviewQueue:
    """``needs_review`` scans in the caller's upazila, oldest first."""
    raise NotImplementedError


@router.post("/{scan_id}", status_code=201)
async def submit_review(scan_id: UUID, body: ReviewIn,
                        user: CurrentUser = Depends(require_role("agronomist", "admin"))) -> dict[str, str]:
    raise NotImplementedError
