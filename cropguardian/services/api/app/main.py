"""Crop Guardian API — deployable starter.

Only health endpoints for now; the rest of the API is built from SPEC.md on top of this.
  /healthz  process is up (no DB) — Render health check
  /readyz   database reachable — UptimeRobot monitor (keeps API warm and Supabase active)
"""

import asyncpg
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = "development"
    app_base_url: str = "http://localhost:5173"
    database_url: str = ""


settings = Settings()
is_prod = settings.environment == "production"

app = FastAPI(
    title="Crop Guardian API",
    version="0.1.0",
    docs_url=None if is_prod else "/docs",  # debug off in production
    redoc_url=None,
    openapi_url=None if is_prod else "/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_base_url],  # only the web app, never "*"
    allow_methods=["GET", "POST", "PUT"],
    allow_headers=["Authorization", "Content-Type", "Idempotency-Key"],
)


# GET and HEAD: uptime monitors (e.g. UptimeRobot) check with HEAD requests; GET-only returns 405.
@app.api_route("/healthz", methods=["GET", "HEAD"])
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.api_route("/readyz", methods=["GET", "HEAD"])
async def readyz() -> JSONResponse:
    if not settings.database_url:
        return JSONResponse({"db": "not configured"}, status_code=503)
    try:
        # statement_cache_size=0: required by Supabase's transaction pooler (port 6543)
        conn = await asyncpg.connect(settings.database_url, statement_cache_size=0, timeout=5)
        try:
            await conn.fetchval("select 1")
        finally:
            await conn.close()
    except Exception as exc:  # report the failure type only, never the connection string
        return JSONResponse({"db": "down", "error": type(exc).__name__}, status_code=503)
    return JSONResponse({"db": "ok"})
