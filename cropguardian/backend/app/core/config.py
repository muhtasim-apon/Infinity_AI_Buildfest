"""Typed configuration (spec section 6.1) with production safety validation.

Why: a misconfigured production stack (debug on, wildcard CORS, default secrets, plain-HTTP origin)
must refuse to start rather than run insecurely (spec 0.2.3, "fail closed", 16.14).
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_INSECURE_SECRETS = {"", "change-me", "changeme", "secret", "password", "dev-secret"}
_MIN_SECRET_LEN = 32


class ConfigError(RuntimeError):
    """Raised when production configuration is unsafe. Message never contains secret values."""


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    # --- core ---------------------------------------------------------------------------------
    cg_env: Literal["development", "test", "staging", "production"] = "development"
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

    # --- LLM / budget (used from Phase 6; declared now so production validation is complete) ---
    anthropic_api_key: str = ""
    llm_daily_budget_usd: float = Field(default=2.0, ge=0)
    advice_mode: Literal["live", "static"] = "live"

    # --- outbound allow-list (spec 16.7 / 17.3) -----------------------------------------------
    outbound_allowlist: list[str] = Field(
        default_factory=lambda: ["api.anthropic.com", "api.open-meteo.com"]
    )

    # --- observability ------------------------------------------------------------------------
    sentry_dsn: str = ""
    metrics_token: str = ""

    @property
    def is_production(self) -> bool:
        return self.cg_env in ("production", "staging")

    @model_validator(mode="after")
    def _validate_production(self) -> Settings:
        if not self.is_production:
            return self
        problems: list[str] = []
        if self.secret_key.lower() in _INSECURE_SECRETS or len(self.secret_key) < _MIN_SECRET_LEN:
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
        if problems:
            # Only the *names* of failed checks are reported; values are never echoed.
            raise ConfigError("insecure production configuration: " + "; ".join(problems))
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
