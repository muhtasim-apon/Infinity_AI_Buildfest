"""Inbound n8n webhooks (ADR 0008). HMAC-verified (threat T2) before any work.

Events: heartbeat · retention · export_labels · reset_demo · verify_audit_chain · alert_sent.
Workflow specs: automation/n8n/workflows/.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Request

router = APIRouter(prefix="/v1/hooks/n8n", tags=["hooks"])

Event = Literal["heartbeat", "retention", "export_labels", "reset_demo", "verify_audit_chain", "alert_sent"]


@router.post("/{event}")
async def n8n_event(event: Event, request: Request) -> dict[str, str]:
    """1. ``security.hmac.verify(request)`` → 401 on failure. 2. Dispatch. Budget 3 s;
    long jobs return 202 and run as a background task."""
    raise NotImplementedError
