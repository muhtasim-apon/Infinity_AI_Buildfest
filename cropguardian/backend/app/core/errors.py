"""RFC 7807 problem+json errors. No stack traces, SQL or internal paths to clients (16.14)."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

PROBLEM_JSON = "application/problem+json"
_log = get_logger("cg.errors")

_TITLES = {
    400: "Bad request",
    401: "Authentication required",
    403: "Forbidden",
    404: "Not found",
    405: "Method not allowed",
    409: "Conflict",
    413: "Payload too large",
    415: "Unsupported media type",
    422: "Validation failed",
    429: "Too many requests",
    503: "Service unavailable",
}


class AppError(Exception):
    """Domain/API error that maps to a safe problem response."""

    def __init__(
        self, status: int, code: str, detail: str = "", extra: dict[str, Any] | None = None
    ):
        super().__init__(code)
        self.status = status
        self.code = code
        self.detail = detail
        self.extra = extra or {}


def problem(
    status: int, code: str, detail: str = "", request_id: str | None = None, **extra: Any
) -> JSONResponse:
    body: dict[str, Any] = {
        "type": f"https://cropguardian.invalid/problems/{code}",
        "title": _TITLES.get(status, "Error"),
        "status": status,
        "code": code,
    }
    if detail:
        body["detail"] = detail
    if request_id:
        body["request_id"] = request_id
    body.update(extra)
    return JSONResponse(body, status_code=status, media_type=PROBLEM_JSON)


def _rid(request: Request) -> str | None:
    return getattr(request.state, "request_id", None)


def install_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def _app_error(request: Request, exc: AppError) -> JSONResponse:
        response = problem(exc.status, exc.code, exc.detail, _rid(request), **exc.extra)
        if exc.status == 429 and "retry_after" in exc.extra:
            response.headers["Retry-After"] = str(exc.extra["retry_after"])
        return response

    @app.exception_handler(StarletteHTTPException)
    async def _http_error(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        # Uniform, non-revealing: do not echo exc.detail (may contain internals).
        return problem(exc.status_code, f"http_{exc.status_code}", request_id=_rid(request))

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        # Field locations and messages only; never echo submitted values (could hold PII/secrets).
        errors = [
            {"loc": [str(p) for p in e.get("loc", ())], "msg": str(e.get("msg", ""))}
            for e in exc.errors()
        ]
        return problem(422, "validation_error", request_id=_rid(request), errors=errors)

    @app.exception_handler(Exception)
    async def _unhandled(request: Request, exc: Exception) -> JSONResponse:
        _log.error("unhandled_exception", error_type=type(exc).__name__, request_id=_rid(request))
        return problem(500, "internal_error", request_id=_rid(request))
