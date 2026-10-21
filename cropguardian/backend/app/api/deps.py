"""Request-scoped dependencies: container, session, principal, CSRF, global rate limit, cookies."""

from __future__ import annotations

from typing import Annotated
from urllib.parse import urlsplit

from fastapi import Depends, Request, Response

from app.core import csrf
from app.core.authz import Principal, principal_from_session
from app.core.clock import utcnow
from app.core.config import Settings
from app.core.errors import AppError
from app.core.security import hmac_hex
from app.core.sessions import COOKIE_NAME, FARMER_KEEP, SessionData
from app.services.auth import RequestCtx
from app.services.container import Container
from app.services.users import RequestInfo

_COOKIE_BASE = {"httponly": True, "secure": True, "samesite": "lax", "path": "/"}


def get_container(request: Request) -> Container:
    container = getattr(request.app.state, "container", None)
    if container is None:
        raise AppError(503, "service_unavailable", "The service is starting. Try again shortly.")
    return container  # type: ignore[no-any-return]


Ctn = Annotated[Container, Depends(get_container)]


def _origin(url: str) -> str:
    parts = urlsplit(url)
    return f"{parts.scheme}://{parts.netloc}".lower() if parts.scheme and parts.netloc else ""


def allowed_origins(settings: Settings) -> set[str]:
    candidates = [settings.app_base_url, settings.public_origin, settings.api_base_url]
    return {o for o in (_origin(u) for u in [*candidates, *settings.cors_origins]) if o}


def client_ip(request: Request, settings: Settings) -> str:
    hops = settings.trusted_proxy_hops
    forwarded = request.headers.get("x-forwarded-for", "")
    if hops > 0 and forwarded:
        parts = [p.strip() for p in forwarded.split(",") if p.strip()]
        if len(parts) >= hops:
            return parts[-hops][:64]
    return request.client.host if request.client else "unknown"


def request_ctx(request: Request, container: Container) -> RequestCtx:
    ip = client_ip(request, container.settings)
    return RequestCtx(
        ip=ip,
        ip_hash=hmac_hex(container.settings.secret_key, "ip", ip)[:32],
        user_agent=request.headers.get("user-agent", "")[:255],
        request_id=getattr(request.state, "request_id", ""),
    )


def get_ctx(request: Request, container: Ctn) -> RequestCtx:
    return request_ctx(request, container)


def get_info(ctx: Annotated[RequestCtx, Depends(get_ctx)]) -> RequestInfo:
    return RequestInfo(request_id=ctx.request_id, ip_hash=ctx.ip_hash)


Ctx = Annotated[RequestCtx, Depends(get_ctx)]
Info = Annotated[RequestInfo, Depends(get_info)]


async def optional_session(
    request: Request, response: Response, container: Ctn
) -> SessionData | None:
    """Load the session from its cookie, slide the idle window, rotate the token when due."""
    cached = getattr(request.state, "session_loaded", False)
    if cached:
        return request.state.session  # type: ignore[no-any-return]
    data = await container.sessions.load(request.cookies.get(COOKIE_NAME))
    if data is not None:
        data = await container.sessions.touch(data)
        if container.sessions.should_rotate(data):
            ctx = request_ctx(request, container)
            token, data = await container.sessions.rotate(
                data, ip_hash=ctx.ip_hash, user_agent=ctx.user_agent
            )
            set_session_cookie(response, token, data)
    request.state.session_loaded = True
    request.state.session = data
    return data


OptSession = Annotated[SessionData | None, Depends(optional_session)]


async def require_session(session: OptSession) -> SessionData:
    if session is None:
        raise AppError(401, "authentication_required")
    return session


ReqSession = Annotated[SessionData, Depends(require_session)]


async def optional_principal(session: OptSession) -> Principal | None:
    return principal_from_session(session, utcnow()) if session else None


OptPrincipal = Annotated[Principal | None, Depends(optional_principal)]


async def csrf_guard(request: Request, container: Ctn, session: OptSession) -> None:
    """Every unsafe request (POST/PUT/PATCH/DELETE) must carry the double-submit token + Origin."""
    reason = csrf.check_request(
        method=request.method,
        secret_key=container.settings.secret_key,
        binding=session.csrf_secret if session else csrf.ANON_BINDING,
        cookie_token=request.cookies.get(csrf.COOKIE_NAME),
        header_token=request.headers.get(csrf.HEADER_NAME),
        origin=request.headers.get("origin"),
        referer=request.headers.get("referer"),
        allowed_origins=allowed_origins(container.settings),
    )
    if reason:
        raise AppError(403, "csrf_failed")


async def global_rate_limit(request: Request, container: Ctn, session: OptSession) -> None:
    """Spec 16.8: 120/min per signed-in user, 60/min per IP when anonymous (reads fail open)."""
    if session is not None:
        await container.limiter.enforce("api_user", session.user_id)
    else:
        await container.limiter.enforce("api_anon", client_ip(request, container.settings))


COMMON_DEPS = [Depends(global_rate_limit), Depends(csrf_guard)]


def set_session_cookie(response: Response, token: str, data: SessionData) -> None:
    max_age = int(FARMER_KEEP.total_seconds()) if data.keep_signed_in else None
    response.set_cookie(COOKIE_NAME, token, max_age=max_age, **_COOKIE_BASE)  # type: ignore[arg-type]


def clear_session_cookies(response: Response) -> None:
    for name in (COOKIE_NAME, csrf.COOKIE_NAME):
        response.delete_cookie(name, path="/", secure=True, httponly=True, samesite="lax")


def issue_csrf(response: Response, container: Container, binding: str) -> str:
    token = csrf.make_token(container.settings.secret_key, binding)
    response.set_cookie(csrf.COOKIE_NAME, token, **_COOKIE_BASE)  # type: ignore[arg-type]
    return token
