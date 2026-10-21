"""Signed-in account endpoints, the demo entry point, and the minimal admin skeleton (Phase 1)."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, Request, Response

from app.api import deps
from app.api.v1.auth import _session_reply
from app.core import consent_texts
from app.core.authz import Principal, authorize, principal_from_session
from app.core.clock import utcnow
from app.core.errors import AppError
from app.schemas import auth as schema
from app.services import demo as demo_service

router = APIRouter(prefix="/api/v1", dependencies=deps.COMMON_DEPS, tags=["account"])


async def principal_dep(session: deps.ReqSession) -> Principal:
    return principal_from_session(session, utcnow())


Me = Annotated[Principal, Depends(principal_dep)]


async def admin_dep(session: deps.OptSession) -> Principal:
    """Admin area: anonymous callers get 404 too, so its existence is not revealed (spec 16.5)."""
    if session is None:
        raise AppError(404, "not_found")
    return principal_from_session(session, utcnow())


AdminP = Annotated[Principal, Depends(admin_dep)]


# --- /me --------------------------------------------------------------------------------------
@router.get("/me")
async def get_me(p: Me, container: deps.Ctn) -> dict[str, Any]:
    authorize(p, "me:read")
    return await container.users.me(p)


@router.patch("/me")
async def patch_me(
    body: schema.ProfilePatch, p: Me, container: deps.Ctn, info: deps.Info
) -> dict[str, Any]:
    authorize(p, "me:update")
    if p.is_demo:
        raise AppError(403, "forbidden")
    return await container.users.update_me(
        p, info, display_name=body.display_name, locale=body.locale
    )


@router.get("/me/sessions")
async def my_sessions(p: Me, container: deps.Ctn) -> dict[str, Any]:
    authorize(p, "me:sessions")
    return {"sessions": await container.users.sessions_view(p)}


@router.delete("/me/sessions/{session_id}", status_code=204)
async def revoke_my_session(
    session_id: str, response: Response, p: Me, container: deps.Ctn
) -> None:
    authorize(p, "me:sessions")
    if p.is_demo and session_id != p.session_id:  # demo users are shared: only your own session
        raise AppError(404, "not_found")
    if not await container.sessions.revoke(session_id, p.user_id):
        raise AppError(404, "not_found")  # not yours (or already gone): indistinguishable
    if session_id == p.session_id:
        deps.clear_session_cookies(response)


@router.get("/me/consents")
async def my_consents(p: Me, container: deps.Ctn) -> dict[str, Any]:
    authorize(p, "me:consents")
    return {"consents": await container.users.consents(p)}


@router.put("/me/consents")
async def put_consent(
    body: schema.ConsentPut, p: Me, container: deps.Ctn, info: deps.Info
) -> dict[str, Any]:
    authorize(p, "me:consents")
    return {"consents": await container.users.set_consent(
        p, info, purpose=body.purpose, granted=body.granted
    )}  # fmt: skip


# --- public consent wording (shown before sign-up) --------------------------------------------
@router.get("/consents/texts")
async def consent_wording() -> dict[str, Any]:
    """The versioned consent texts the registration form must show (spec 16.17)."""
    return {
        "version": consent_texts.CURRENT_VERSION,
        "consents": [
            {
                "purpose": c.purpose,
                "required": c.required,
                "default_granted": c.default_granted,
                "title": dict(c.title),
                "body": dict(c.body),
            }
            for c in consent_texts.current_texts()
        ],
    }


# --- demo -------------------------------------------------------------------------------------
@router.post("/demo/session", status_code=201)
async def demo_session(
    body: schema.DemoIn, request: Request, response: Response, container: deps.Ctn,
    ctx: deps.Ctx, session: deps.OptSession,
) -> dict[str, Any]:  # fmt: skip
    if not container.settings.demo_enabled:
        raise AppError(404, "not_found")
    await container.limiter.enforce("demo_session", ctx.ip)
    await container.captcha.verify(body.captcha)
    token, data = await demo_service.start_demo_session(
        container.engine, container.sessions, ctx, body.role
    )
    if session is not None:
        await container.sessions.revoke(session.id, session.user_id)
    return await _session_reply(container, response, token, data, "home")


# --- admin skeleton (the console itself is Phase 10) ------------------------------------------
@router.get("/admin/users")
async def admin_users(
    p: AdminP, container: deps.Ctn, limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0, le=100_000)] = 0,
) -> dict[str, Any]:  # fmt: skip
    authorize(p, "admin:users:list")
    return {"users": await container.users.admin_list_users(p, limit=limit, offset=offset)}


@router.post("/admin/invites", status_code=201)
async def admin_invite(
    body: schema.InviteIn, p: AdminP, container: deps.Ctn, ctx: deps.Ctx
) -> dict[str, Any]:
    authorize(p, "admin:invites:create")
    admin = await container.auth.get_user(p.user_id)
    if admin is None:
        raise AppError(401, "authentication_required")
    invite_id, expires = await container.auth.create_invite(
        ctx, admin, email=body.email, role=body.role, regions=body.region_codes
    )
    return {"id": invite_id, "expires_at": expires.isoformat()}  # the token is only ever emailed
