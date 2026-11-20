"""Typed configuration (spec section 6.1) with production safety validation.

Why: a misconfigured production stack (debug on, wildcard CORS, default secrets, plain-HTTP origin)
must refuse to start rather than run insecurely (spec 0.2.3, "fail closed", 16.14).
"""

from __future__ import annotations

import hmac
import os
from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_SECRETS = {"", "change-me", "changeme", "secret", "password", "dev-secret"}
_MIN_SECRET_LEN = 32
DEV_SECRET = "dev-only-secret-key-never-use-in-production-0000"  # noqa: S105


def _default_env() -> Literal["development", "production"]:
    """Render sets RENDER=true on every service. If CG_ENV was forgotten there, assume production so
    the strict validation below runs (and refuses to start) instead of silently running in dev mode
    with /docs enabled and a localhost-only host list."""
    return "production" if os.environ.get("RENDER") else "development"


class ConfigError(RuntimeError):
    """Raised when production configuration is unsafe. Message never contains secret values."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # --- core ---------------------------------------------------------------------------------
    cg_env: Literal["development", "test", "staging", "production"] = Field(
        default_factory=_default_env
    )
    log_level: Literal["debug", "info", "warning", "error"] = "info"
    app_base_url: str = "http://localhost:5173"
    api_base_url: str = "http://localhost:8000"
    serve_spa: bool = False
    secret_key: str = ""
    cors_origins: list[str] = Field(default_factory=list)
    trusted_hosts: list[str] = Field(
        default_factory=lambda: ["localhost", "127.0.0.1", "testserver"]
    )

    # --- data ---------------------------------------------------------------------------------
    database_url: str = ""  # runtime connection (app role set per transaction)
    migration_database_url: str = ""  # Alembic only (owner role)
    db_pool_size: int = Field(default=5, ge=1, le=50)
    redis_url: str = ""
    jobs_mode: Literal["inprocess", "worker", "off"] = "inprocess"

    # --- storage ------------------------------------------------------------------------------
    s3_endpoint_url: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_region: str = "us-east-1"
    storage_bucket_scans: str = "scans"
    storage_bucket_models: str = "models"
    max_upload_mb: int = Field(default=5, ge=1, le=20)

    # --- LLM (Meta Llama API, OpenAI-compatible endpoint; DECISIONS D-031) ---------------------
    # The key is typed into the Render dashboard only; it is never logged or echoed.
    llama_api_key: str = ""
    llm_base_url: str = "https://api.llama.com/compat/v1"
    llm_model: str = "Llama-4-Maverick-17B-128E-Instruct-FP8"
    llm_timeout_s: float = Field(default=20.0, ge=2, le=60)
    llm_daily_call_cap: int = Field(default=400, ge=0, le=20_000)  # hard stop on spend per day
    llm_daily_budget_usd: float = Field(default=2.0, ge=0)
    advice_mode: Literal["live", "static"] = "live"

    # --- outbound allow-list (spec 16.7 / 17.3) -----------------------------------------------
    outbound_allowlist: list[str] = Field(
        default_factory=lambda: ["api.llama.com", "api.open-meteo.com"]
    )

    # --- identity (Phase 1) -------------------------------------------------------------------
    public_origin: str = ""  # origin used in emailed links; defaults to app_base_url
    sms_provider: Literal["console", "disabled"] = "console"
    email_provider: Literal["console", "disabled"] = "console"
    demo_enabled: bool = False
    demo_seed_on_start: bool = False
    trusted_proxy_hops: int = Field(
        default=0, ge=0, le=3
    )  # proxies in front that append X-Forwarded-For
    captcha_bypass: bool = False  # honoured ONLY when cg_env == "test"

    # --- observability ------------------------------------------------------------------------
    sentry_dsn: str = ""
    metrics_token: str = ""

    @property
    def origin_for_links(self) -> str:
        return (self.public_origin or self.app_base_url).rstrip("/")

    @property
    def is_production(self) -> bool:
        return self.cg_env in ("production", "staging")

    @model_validator(mode="after")
    def _validate_production(self) -> Settings:  # noqa: PLR0912
        if os.environ.get("RENDER") and self.cg_env not in ("production", "staging"):
            # CG_ENV=test enables the test router and CAPTCHA bypass; development opens /docs.
            # A hosted service must never run in either mode, whatever the dashboard says.
            raise ConfigError(
                "insecure configuration: CG_ENV must be production or staging on Render"
            )
        if not self.is_production:
            if not self.secret_key:
                self.secret_key = DEV_SECRET  # keeps HMAC/AES features usable in dev and tests
            return self
        problems: list[str] = []
        weak = self.secret_key.lower() in _INSECURE_SECRETS or hmac.compare_digest(
            self.secret_key, DEV_SECRET
        )
        if weak or len(self.secret_key) < _MIN_SECRET_LEN:
            problems.append("SECRET_KEY missing, default or shorter than 32 chars")
        if not self.app_base_url.startswith("https://"):
            problems.append("APP_BASE_URL must be https in production")
        if "*" in self.cors_origins:
            problems.append("CORS wildcard is forbidden")
        if any(not o.startswith("https://") for o in self.cors_origins):
            problems.append("every CORS origin must be https in production")
        if "*" in self.trusted_hosts:
            problems.append("TRUSTED_HOSTS wildcard is forbidden")
        if not self.database_url:
            problems.append("DATABASE_URL is required")
        if not self.redis_url:
            problems.append(
                "REDIS_URL is required (sessions and rate limits fail closed without it)"
            )
        if self.captcha_bypass:
            problems.append("CAPTCHA_BYPASS is forbidden outside the test environment")
        if self.sms_provider == "console":
            problems.append("SMS_PROVIDER=console prints codes to logs: use disabled")
        if self.email_provider == "console":
            problems.append("EMAIL_PROVIDER=console prints links to logs: use disabled")
        if problems:
            # Only the *names* of failed checks are reported; values are never echoed.
            raise ConfigError("insecure production configuration: " + "; ".join(problems))
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
