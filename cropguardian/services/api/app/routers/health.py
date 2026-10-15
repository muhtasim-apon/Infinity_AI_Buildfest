"""Liveness and readiness.

``/healthz`` — process is up. No DB, no model. Budget 200 ms. Render health check path.
``/readyz``  — DB reachable and model loaded with the expected hash. Budget 2 s.
"""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/readyz")
async def readyz() -> dict[str, object]:
    """Return ``{db, model: {name, version, sha256}}``; 503 if any component is down."""
    raise NotImplementedError
