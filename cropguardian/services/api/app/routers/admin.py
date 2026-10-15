"""Admin: settings (τ, outbreak rules), model versions, KB documents, users/roles.

Every write requires a ``reason`` and is appended to the audit chain (threat T8).
"""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.schemas.admin import SettingsIn, SettingsOut
from app.security.auth import CurrentUser, require_role

router = APIRouter(prefix="/v1/admin", tags=["admin"])


@router.get("/settings", response_model=SettingsOut)
async def get_settings_(user: CurrentUser = Depends(require_role("admin"))) -> SettingsOut:
    raise NotImplementedError


@router.put("/settings", response_model=SettingsOut)
async def put_settings(body: SettingsIn, user: CurrentUser = Depends(require_role("admin"))) -> SettingsOut:
    raise NotImplementedError


@router.post("/models/{model_id}/activate")
async def activate_model(model_id: UUID, user: CurrentUser = Depends(require_role("admin"))) -> dict[str, str]:
    """Flip ``is_active`` in one transaction (partial unique index guarantees one active)."""
    raise NotImplementedError


@router.post("/kb/documents/{doc_id}/retire")
async def retire_document(doc_id: UUID, user: CurrentUser = Depends(require_role("admin"))) -> dict[str, str]:
    raise NotImplementedError
