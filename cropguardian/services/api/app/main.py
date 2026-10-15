"""FastAPI application factory.

Startup (lifespan):
  1. load settings; 2. open the DB pool; 3. load the ONNX session once and verify its
  SHA-256 against the active ``model_versions`` row (threat T6) — refuse to become ready
  on mismatch; 4. register routers.

Render free specifics (docs/deployment/challenges-and-recovery.md):
  - ``/healthz`` never touches the DB, so the platform health check passes quickly after a
    cold start; ``/readyz`` reports DB + model for monitors.
  - No state is kept on local disk; restarts are safe.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import admin, alerts, audit, demo, health, hooks, review, scans


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Open DB pool and load the model; close on shutdown.

    TODO(apon): app.state.db = await db.create_pool(settings)
    TODO(apon): app.state.model = inference.load_session(settings) — verify sha256
    """
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    is_prod = settings.environment == "production"
    app = FastAPI(
        title="Crop Guardian API",
        version="0.1.0",
        lifespan=lifespan,
        docs_url=None if is_prod else "/docs",       # OWASP A05: no interactive docs in prod
        openapi_url=None if is_prod else "/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.app_base_url],          # exact origin, never "*"
        allow_methods=["GET", "POST", "PUT"],
        allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
        allow_credentials=False,
    )
    # TODO(apon): request-id middleware, security headers, rate limiter, problem+json handlers
    for r in (health, demo, scans, review, alerts, admin, audit, hooks):
        app.include_router(r.router)
    return app


app = create_app()
