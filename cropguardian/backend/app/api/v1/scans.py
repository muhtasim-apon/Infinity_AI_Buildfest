"""Scan, alert and knowledge-base endpoints (Gantt P2/P3/P4).

POST /api/v1/scans            multipart image + division code + Idempotency-Key header (farmer)
GET  /api/v1/scans            the farmer's own history (RLS: own rows only)
GET  /api/v1/scans/{id}       one result (404 for anyone else's)
GET  /api/v1/alerts           farmer: approved only; staff: drafts + decided (RLS)
POST /api/v1/alerts/{id}/decision   reviewer approve/reject (+ audit log; real staff need step-up)
GET  /api/v1/kb/sources       public Trust Centre data: sources, counts, exclusions, limits
"""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastapi import APIRouter, Depends, File, Form, Header, UploadFile
from pydantic import BaseModel, ConfigDict

from app.api import deps
from app.core.authz import Principal, Resource, authorize, principal_from_session
from app.core.clock import utcnow
from app.core.errors import AppError
from app.domain import decision, outbreak_rules
from app.services.scans import ScanService, load_kb

router = APIRouter(prefix="/api/v1", dependencies=deps.COMMON_DEPS, tags=["scans"])
public_router = APIRouter(prefix="/api/v1", dependencies=[Depends(deps.global_rate_limit)])


async def principal_dep(session: deps.ReqSession) -> Principal:
    return principal_from_session(session, utcnow())


Me = Annotated[Principal, Depends(principal_dep)]


async def farmer_dep(p: Me) -> Principal:
    """Authorize BEFORE the multipart body is parsed: deny-first, so a staff caller gets 403 and
    never reaches upload validation (and never makes the server read a 5 MB body)."""
    authorize(p, "scans:create", Resource(owner_id=p.user_id, tenant_id=p.tenant_id))
    return p


async def staff_dep(p: Me) -> Principal:
    authorize(p, "alerts:decide", Resource(tenant_id=p.tenant_id))
    return p


Farmer = Annotated[Principal, Depends(farmer_dep)]
Staff = Annotated[Principal, Depends(staff_dep)]


def scans_of(container: deps.Ctn) -> ScanService:
    if container.scans is None:
        raise AppError(503, "service_unavailable")
    return container.scans


class Decision(BaseModel):
    model_config = ConfigDict(extra="forbid")
    decision: Literal["approve", "reject"]


@router.post("/scans", status_code=201)
async def create_scan(
    p: Farmer,
    container: deps.Ctn,
    ctx: deps.Ctx,
    image: Annotated[UploadFile, File()],
    region_code: Annotated[str, Form(max_length=8)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", max_length=80)],
) -> dict[str, Any]:
    await container.limiter.enforce("scan_create", p.user_id)
    limit = container.settings.max_upload_mb * 1024 * 1024
    raw = await image.read(limit + 1)  # never read more than the limit + 1 byte
    return await scans_of(container).create(
        p,
        image=raw,
        region_code=region_code,
        idempotency_key=idempotency_key,
        request_id=ctx.request_id,
    )


@router.get("/scans")
async def list_scans(p: Me, container: deps.Ctn) -> dict[str, Any]:
    return {"scans": await scans_of(container).list_mine(p)}


@router.get("/scans/{scan_id}")
async def get_scan(scan_id: str, p: Me, container: deps.Ctn) -> dict[str, Any]:
    return await scans_of(container).get(p, scan_id)


@router.get("/alerts")
async def list_alerts(p: Me, container: deps.Ctn) -> dict[str, Any]:
    return {"alerts": await scans_of(container).list_alerts(p)}


@router.post("/alerts/{alert_id}/decision")
async def decide_alert(
    alert_id: str, body: Decision, p: Staff, container: deps.Ctn, ctx: deps.Ctx
) -> dict[str, Any]:
    await container.limiter.enforce("alert_approve", p.user_id)
    return await scans_of(container).decide_alert(
        p,
        alert_id,
        approve=body.decision == "approve",
        request_id=ctx.request_id,
        ip_hash=ctx.ip_hash,
    )


@public_router.get("/kb/sources")
async def kb_sources() -> dict[str, Any]:
    kb = load_kb()
    counts: dict[str, int] = {}
    for chunk in kb.chunks:
        counts[chunk.source_id] = counts.get(chunk.source_id, 0) + 1
    return {
        "kb_version": kb.version,
        "transcription": kb.transcription,
        "policy": kb.policy,
        "sources": [
            {"id": sid, **meta, "chunks": counts.get(sid, 0)} for sid, meta in kb.sources.items()
        ],
        "excluded": list(kb.excluded),
        "diseases": kb.diseases,
        "divisions": {k: {"bn": v[0], "en": v[1]} for k, v in outbreak_rules.DIVISIONS.items()},
        "limits": {
            "abstain_below": decision.ABSTAIN_BELOW,
            "confidence": "self-reported by the model, not calibrated; shown only as a band",
            "retrieval": "metadata filter + keyword overlap; no embeddings yet (planned)",
            "crops": ["rice"],
            "image_retention": "photos are not stored; only a SHA-256 of the re-encoded image",
            "outbreak_rule": {
                "min_cases": outbreak_rules.MIN_CASES,
                "window_days": outbreak_rules.WINDOW.days,
                "needs_reviewer_approval": True,
            },
        },
    }
