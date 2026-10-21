"""Authentication endpoints (spec 9, 16.4). Business rules live in `services.auth`; this layer only
validates input, enforces CSRF/authorization, and sets cookies."""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from fastapi import APIRouter, Request, Response

from app.api import deps
from app.core.authz import authorize, principal_from_session
from app.core.clock import utcnow
from app.core.errors import AppError
from app.core.sessions import SessionData
from app.schemas import auth as schema
from app.services.auth import LoginResult, UserRow

router = APIRouter(prefix="/api/v1", dependencies=deps.COMMON_DEPS, tags=["auth"])


def _user_view(user: UserRow) -> dict[str, Any]:
    return {
        "id": user.id, "role": user.role, "display_name": user.display_name,
        "locale": user.locale, "tenant": user.tenant_id,
    }  # fmt: skip


async def _session_reply(
    container: deps.Container, response: Response, token: str, data: SessionData,
    next_step: str, user: UserRow | None = None, **extra: Any,
) -> dict[str, Any]:  # fmt: skip
    deps.set_session_cookie(response, token, data)
    csrf_token = deps.issue_csrf(response, container, data.csrf_secret)
    body: dict[str, Any] = {"next": next_step, "csrf_token": csrf_token, **extra}
    if user is None:
        user = await container.auth.get_user(data.user_id)
    if user is not None:
        body["user"] = _user_view(user)
    return body


async def _login_reply(
    container: deps.Container, response: Response, result: LoginResult
) -> dict[str, Any]:
    return await _session_reply(container, response, result.token, result.session, result.next)


async def _drop_presented_session(container: deps.Container, session: SessionData | None) -> None:
    """Session-fixation defence: a login/verify always mints a new session and kills the old one."""
    if session is not None:
        await container.sessions.revoke(session.id, session.user_id)


async def _current_user(container: deps.Container, session: SessionData) -> UserRow:
    user = await container.auth.get_user(session.user_id)
    if user is None or user.status != "ACTIVE":
        raise AppError(401, "authentication_required")
    return user


# --- CAPTCHA and CSRF -------------------------------------------------------------------------
@router.get("/captcha/challenge")
async def captcha_challenge(request: Request, container: deps.Ctn) -> dict[str, Any]:
    await container.limiter.enforce("captcha", deps.client_ip(request, container.settings))
    return asdict(container.captcha.issue())


@router.get("/auth/csrf")
async def csrf_token(
    response: Response, container: deps.Ctn, session: deps.OptSession
) -> dict[str, str]:
    binding = session.csrf_secret if session else "anonymous"
    return {"csrf_token": deps.issue_csrf(response, container, binding)}


@router.get("/auth/state")
async def auth_state(
    response: Response, container: deps.Ctn, session: deps.OptSession
) -> dict[str, Any]:
    """Cheap boot probe for the SPA: who am I and which step comes next. Never 401s."""
    if session is None:
        return {
            "authenticated": False,
            "csrf_token": deps.issue_csrf(response, container, "anonymous"),
        }
    principal = principal_from_session(session, utcnow())
    next_step = "home"
    if principal.needs_totp and not principal.totp_verified:
        next_step = "totp" if await container.auth.has_totp(session.user_id) else "setup_totp"
    user = await container.auth.get_user(session.user_id)
    return {
        "authenticated": True,
        "next": next_step,
        "role": session.role,
        "tenant": session.tenant_id,
        "display_name": user.display_name if user else "",
        "locale": session.locale,
        "step_up": principal.step_up,
        "csrf_token": deps.issue_csrf(response, container, session.csrf_secret),
    }


# --- registration -----------------------------------------------------------------------------
@router.post("/auth/register/farmer", status_code=202)
async def register_farmer(
    body: schema.RegisterFarmerIn, container: deps.Ctn, ctx: deps.Ctx
) -> dict[str, str]:
    await container.auth.register_farmer(
        ctx, phone=body.phone, password=body.password, display_name=body.display_name,
        locale=body.locale,
        optional_consents={"training_use": body.training_use, "push_alerts": body.push_alerts},
        captcha=body.captcha, honeypot=body.website,
    )  # fmt: skip
    return {"status": "otp_sent"}  # identical whether or not the number was already registered


@router.post("/auth/register/staff", status_code=201)
async def register_staff(
    body: schema.StaffRegisterIn, container: deps.Ctn, ctx: deps.Ctx
) -> dict[str, str]:
    await container.auth.register_staff(
        ctx, token=body.token, password=body.password, display_name=body.display_name,
        locale=body.locale,
    )  # fmt: skip
    return {"status": "created"}


@router.post("/auth/otp/send", status_code=202)
async def otp_send(body: schema.OtpSendIn, container: deps.Ctn, ctx: deps.Ctx) -> dict[str, str]:
    await container.captcha.verify(body.captcha)
    await container.auth.send_otp(ctx, phone=body.phone, purpose=body.purpose)
    return {"status": "otp_sent"}


@router.post("/auth/otp/verify")
async def otp_verify(
    body: schema.OtpVerifyIn, response: Response, container: deps.Ctn, ctx: deps.Ctx,
    session: deps.OptSession,
) -> dict[str, Any]:  # fmt: skip
    result = await container.auth.verify_registration(
        ctx, phone=body.phone, code=body.code, keep_signed_in=body.keep_signed_in
    )
    await _drop_presented_session(container, session)  # only after success: a bad code is no logout
    return await _login_reply(container, response, result)


# --- login / logout ---------------------------------------------------------------------------
@router.post("/auth/login")
async def login(
    body: schema.LoginIn, response: Response, container: deps.Ctn, ctx: deps.Ctx,
    session: deps.OptSession,
) -> dict[str, Any]:  # fmt: skip
    result = await container.auth.login(
        ctx, identifier=body.identifier, password=body.password,
        keep_signed_in=body.keep_signed_in, captcha=body.captcha,
    )  # fmt: skip
    await _drop_presented_session(container, session)
    return await _login_reply(container, response, result)


@router.post("/auth/login/totp")
async def login_totp(
    body: schema.TotpIn, response: Response, container: deps.Ctn, ctx: deps.Ctx,
    session: deps.ReqSession,
) -> dict[str, Any]:  # fmt: skip
    authorize(principal_from_session(session, utcnow()), "auth:totp_login")
    user = await _current_user(container, session)
    token, fresh = await container.auth.login_totp(
        ctx, session, user, code=body.code, recovery=body.recovery
    )
    return await _session_reply(container, response, token, fresh, "home", user)


@router.post("/auth/step-up")
async def step_up(
    body: schema.CodeIn, response: Response, container: deps.Ctn, ctx: deps.Ctx,
    session: deps.ReqSession,
) -> dict[str, Any]:  # fmt: skip
    authorize(principal_from_session(session, utcnow()), "auth:step_up")
    user = await _current_user(container, session)
    token, fresh = await container.auth.step_up(ctx, session, user, code=body.code)
    return await _session_reply(container, response, token, fresh, "home", user, step_up=True)


@router.post("/auth/logout", status_code=204)
async def logout(
    response: Response, container: deps.Ctn, ctx: deps.Ctx, session: deps.ReqSession
) -> None:
    await container.auth.logout(ctx, session)
    deps.clear_session_cookies(response)


@router.post("/auth/logout-all", status_code=204)
async def logout_all(
    response: Response, container: deps.Ctn, ctx: deps.Ctx, session: deps.ReqSession
) -> None:
    await container.auth.logout_all(ctx, session)
    deps.clear_session_cookies(response)


# --- two-factor -------------------------------------------------------------------------------
@router.post("/auth/totp/setup")
async def totp_setup(container: deps.Ctn, session: deps.ReqSession) -> dict[str, str]:
    principal = principal_from_session(session, utcnow())
    authorize(principal, "auth:totp_setup")
    user = await _current_user(container, session)
    secret, uri = await container.auth.begin_totp_setup(user, replace=principal.step_up)
    return {"secret": secret, "otpauth_uri": uri}  # shown once; never retrievable again


@router.post("/auth/totp/confirm")
async def totp_confirm(
    body: schema.CodeIn, response: Response, container: deps.Ctn, ctx: deps.Ctx,
    session: deps.ReqSession,
) -> dict[str, Any]:  # fmt: skip
    authorize(principal_from_session(session, utcnow()), "auth:totp_setup")
    user = await _current_user(container, session)
    codes, token, fresh = await container.auth.confirm_totp(ctx, session, user, body.code)
    return await _session_reply(
        container, response, token, fresh, "home", user, recovery_codes=codes
    )


@router.post("/auth/recovery-codes")
async def recovery_codes(
    container: deps.Ctn, ctx: deps.Ctx, session: deps.ReqSession
) -> dict[str, list[str]]:
    authorize(principal_from_session(session, utcnow()), "auth:recovery_codes")
    user = await _current_user(container, session)
    return {"recovery_codes": await container.auth.regenerate_recovery_codes(ctx, user)}


# --- password and email -----------------------------------------------------------------------
@router.post("/auth/password/forgot", status_code=202)
async def password_forgot(
    body: schema.ForgotIn, container: deps.Ctn, ctx: deps.Ctx
) -> dict[str, str]:
    await container.captcha.verify(body.captcha)
    await container.auth.forgot_password(ctx, identifier=body.identifier)
    return {"status": "accepted"}  # same answer for known and unknown accounts


@router.post("/auth/password/reset", status_code=204)
async def password_reset(body: schema.ResetIn, container: deps.Ctn, ctx: deps.Ctx) -> None:
    await container.auth.reset_password(
        ctx, new_password=body.new_password, token=body.token, phone=body.phone, code=body.code
    )


@router.post("/auth/password/change")
async def password_change(
    body: schema.ChangePasswordIn, response: Response, container: deps.Ctn, ctx: deps.Ctx,
    session: deps.ReqSession,
) -> dict[str, Any]:  # fmt: skip
    authorize(principal_from_session(session, utcnow()), "me:update")
    user = await _current_user(container, session)
    token, fresh = await container.auth.change_password(
        ctx, session, user, current=body.current_password, new=body.new_password
    )
    return await _session_reply(container, response, token, fresh, "home", user)


@router.post("/auth/email/verify", status_code=204)
async def email_verify(body: schema.TokenIn, container: deps.Ctn, ctx: deps.Ctx) -> None:
    await container.auth.verify_email(ctx, body.token)


@router.post("/auth/email/resend", status_code=202)
async def email_resend(container: deps.Ctn, session: deps.ReqSession) -> dict[str, str]:
    authorize(principal_from_session(session, utcnow()), "me:update")
    user = await _current_user(container, session)
    await container.auth.request_email_verification(user)
    return {"status": "accepted"}
