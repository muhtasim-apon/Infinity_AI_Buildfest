"""Request-pipeline middleware in the spec 16.9 order (Phase 0 subset):
1 request id -> 2 trusted host (Starlette) -> 3 body size limit -> 4 security headers.
Session, tenant, CSRF and rate limiting arrive in Phase 1 and slot in after these.
"""

from __future__ import annotations

import re
import time
import uuid

from starlette.datastructures import MutableHeaders
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.errors import problem
from app.core.logging import get_logger

_REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._-]{8,64}$")


def build_csp(s3_public_origin: str = "") -> str:
    extra = f" {s3_public_origin}" if s3_public_origin else ""
    return (
        "default-src 'self'; script-src 'self' 'wasm-unsafe-eval'; style-src 'self'; "
        f"img-src 'self' data: blob:{extra}; font-src 'self'; connect-src 'self'{extra}; "
        "media-src 'self' blob:; worker-src 'self' blob:; manifest-src 'self'; "
        "frame-ancestors 'none'; base-uri 'none'; form-action 'self'; object-src 'none'; "
        "upgrade-insecure-requests"
    )


SECURITY_HEADERS: dict[str, str] = {
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(self), microphone=(), geolocation=(self), payment=(), usb=()",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
    "X-Frame-Options": "DENY",
    "Cache-Control": "no-store",
}


class RequestIdMiddleware:
    """Accept a well-formed X-Request-ID from the proxy, else generate one; echo it back."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        headers = dict(scope.get("headers", []))
        incoming = headers.get(b"x-request-id", b"").decode("latin-1")
        rid = incoming if _REQUEST_ID_RE.match(incoming) else uuid.uuid4().hex
        scope.setdefault("state", {})["request_id"] = rid

        async def send_with_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)["X-Request-ID"] = rid
            await send(message)

        await self.app(scope, receive, send_with_id)


class BodySizeLimitMiddleware:
    """Reject bodies over `max_bytes` (Content-Length fast path + streaming count) with 413."""

    def __init__(self, app: ASGIApp, max_bytes: int = 1_048_576) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        rid = scope.get("state", {}).get("request_id")
        declared = dict(scope.get("headers", [])).get(b"content-length")
        if declared is not None:
            try:
                too_big = int(declared) > self.max_bytes
            except ValueError:
                too_big = True
            if too_big:
                await problem(413, "payload_too_large", request_id=rid)(scope, receive, send)
                return

        seen = 0
        exceeded = False

        async def limited_receive() -> Message:
            nonlocal seen, exceeded
            message = await receive()
            if message["type"] == "http.request":
                seen += len(message.get("body", b""))
                if seen > self.max_bytes:
                    exceeded = True
                    return {"type": "http.request", "body": b"", "more_body": False}
            return message

        started = False

        async def guarded_send(message: Message) -> None:
            nonlocal started
            if message["type"] == "http.response.start":
                started = True
            await send(message)

        await self.app(scope, limited_receive, guarded_send)
        if exceeded and not started:
            await problem(413, "payload_too_large", request_id=rid)(scope, receive, send)


class SecurityHeadersMiddleware:
    """Add the spec 16.3 headers to every HTTP response (also on the hosted stack, no Nginx)."""

    def __init__(self, app: ASGIApp, csp: str) -> None:
        self.app = app
        self.csp = csp

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = MutableHeaders(scope=message)
                for key, value in SECURITY_HEADERS.items():
                    if key not in headers:
                        headers[key] = value
                headers["Content-Security-Policy"] = self.csp
                if "server" in headers:
                    del headers["server"]
            await send(message)

        await self.app(scope, receive, send_with_headers)


LIVENESS_PATHS = frozenset({"/health", "/healthz"})


class LivenessExemptTrustedHost(TrustedHostMiddleware):
    """Trusted-host check (spec 16.3) except for the two liveness paths.

    Why: platform health checkers (Render, Docker, load balancers) call the instance by an internal
    address, not the public hostname. Rejecting them (400) keeps a deploy from ever going live. The
    exempt endpoints return a constant body and touch no data; other paths stay host-checked.
    """

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http" and scope.get("path") in LIVENESS_PATHS:
            await self.app(scope, receive, send)
            return
        await super().__call__(scope, receive, send)


_access_log = get_logger("cg.access")


class RequestLogMiddleware:
    """One structured line per request: method, path (never the query string), status, duration, id.

    Why: uvicorn's own access log is disabled because it prints query strings (possible tokens).
    Liveness probes are logged at debug level so a 5-second health check does not drown traffic.
    Sits just inside the request-id middleware so it also records requests rejected further in.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        started = time.perf_counter()
        status = 500

        async def capture(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = int(message["status"])
            await send(message)

        try:
            await self.app(scope, receive, capture)
        finally:
            path = str(scope.get("path", ""))
            emit = (
                _access_log.debug if path in LIVENESS_PATHS and status < 400 else _access_log.info
            )
            emit(
                "request",
                method=scope.get("method"),
                path=path,
                status=status,
                duration_ms=round((time.perf_counter() - started) * 1000, 1),
                request_id=scope.get("state", {}).get("request_id"),
            )
