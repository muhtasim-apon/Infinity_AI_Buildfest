"""Health and metrics endpoints.

/health        liveness (no dependencies) - Render health check
/health/ready  database reachable - keep-warm + UptimeRobot (also keeps Supabase from pausing)
/metrics       Prometheus; reachable only with METRICS_TOKEN (Nginx also blocks it externally)
/healthz,/readyz  legacy aliases so the existing UptimeRobot monitor survives the cut-over.
GET and HEAD are both allowed: monitors probe with HEAD.
"""

from __future__ import annotations

import hmac
import time

from fastapi import APIRouter, Request, Response
from fastapi.responses import JSONResponse
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest
from sqlalchemy import text

from app.core.errors import problem

router = APIRouter()
_STARTED = time.monotonic()
HEALTH_HITS = Counter("cg_health_requests_total", "Health endpoint requests", ["endpoint"])


@router.api_route("/health", methods=["GET", "HEAD"], include_in_schema=False)
@router.api_route("/healthz", methods=["GET", "HEAD"], include_in_schema=False)
async def health() -> dict[str, object]:
    HEALTH_HITS.labels("health").inc()
    return {"status": "ok", "uptime_s": int(time.monotonic() - _STARTED)}


@router.api_route("/health/ready", methods=["GET", "HEAD"], include_in_schema=False)
@router.api_route("/readyz", methods=["GET", "HEAD"], include_in_schema=False)
async def ready(request: Request) -> JSONResponse:
    HEALTH_HITS.labels("ready").inc()
    engine = getattr(request.app.state, "engine", None)
    if engine is None:
        return JSONResponse({"db": "not configured"}, status_code=503)
    try:
        async with engine.connect() as conn:
            await conn.execute(text("select 1"))
    except Exception as exc:  # report the failure type only, never the connection string
        return JSONResponse({"db": "down", "error": type(exc).__name__}, status_code=503)
    return JSONResponse({"db": "ok"})


@router.get("/metrics", include_in_schema=False)
async def metrics(request: Request) -> Response:
    expected: str = request.app.state.settings.metrics_token
    supplied = request.headers.get("x-metrics-token", "")
    # No token configured -> endpoint hidden (fail closed). Constant-time compare.
    if not expected or not hmac.compare_digest(supplied, expected):
        return problem(404, "not_found")
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
