"""Crop Guardian API application factory (spec 16.9 middleware order).

Debug features (docs, OpenAPI) are off in production (16.14). CORS is off by default because the SPA
and API share one origin; development allows exactly the Vite origin.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import health
from app.core.config import Settings, get_settings
from app.core.errors import install_error_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import (
    BodySizeLimitMiddleware,
    RequestIdMiddleware,
    SecurityHeadersMiddleware,
    build_csp,
)
from app.db.session import make_engine
from app.jobs.worker import start_inprocess_worker, stop_inprocess_worker


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level, json_output=settings.is_production)
    log = get_logger("cg.main")

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        app.state.settings = settings
        app.state.engine = make_engine(settings) if settings.database_url else None
        app.state.worker = await start_inprocess_worker(settings)
        log.info("startup", env=settings.cg_env, jobs_mode=settings.jobs_mode)
        try:
            yield
        finally:
            await stop_inprocess_worker(app.state.worker)
            if app.state.engine is not None:
                await app.state.engine.dispose()

    prod = settings.is_production
    app = FastAPI(
        title="Crop Guardian API",
        version="0.1.0",
        docs_url=None if prod else "/docs",
        redoc_url=None,
        openapi_url=None if prod else "/openapi.json",
        lifespan=lifespan,
    )
    app.state.settings = settings
    app.state.engine = None

    # add_middleware wraps outward: the LAST added runs FIRST. Spec order is
    # request-id -> trusted host -> body limit -> security headers, so add in reverse.
    app.add_middleware(SecurityHeadersMiddleware, csp=build_csp())
    app.add_middleware(BodySizeLimitMiddleware, max_bytes=1_048_576)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.trusted_hosts)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,  # explicit list, never "*"
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "X-CSRF-Token"],
        )
    app.add_middleware(RequestIdMiddleware)

    install_error_handlers(app)
    app.include_router(health.router)
    return app


app = create_app()
