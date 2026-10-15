"""Typed application settings, loaded from the environment.

Every variable is documented in ``.env.example``. Secrets come from the Render environment
group ``cropguardian-secrets`` in production and are never committed.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # core
    environment: str = "development"
    log_level: str = "info"
    app_base_url: str = "http://localhost:5173"  # the ONLY allowed CORS origin

    # supabase
    supabase_url: str = ""
    supabase_service_role_key: SecretStr = SecretStr("")
    supabase_jwt_secret: SecretStr = SecretStr("")
    database_url: SecretStr = SecretStr("")
    db_pool_size: int = Field(5, ge=1, le=20)
    storage_bucket_scans: str = "scans"
    storage_bucket_models: str = "models"

    # vision model
    model_name: str = "crop-disease-classifier"
    model_version: str = "v0.1.0"
    model_path: str = "/app/models/classifier.int8.onnx"
    model_confidence_threshold: float = Field(0.70, gt=0, lt=1)  # replaced by calibrated τ
    model_temperature: float = Field(1.0, gt=0)
    inference_timeout_ms: int = 4000
    max_upload_mb: int = 5

    # llm / rag
    llm_provider: str = "anthropic"
    anthropic_api_key: SecretStr = SecretStr("")
    llm_model: str = "claude-sonnet-5-5"
    llm_timeout_ms: int = 20000
    rag_top_k: int = 8
    rag_min_score: float = 0.55

    # outbreak
    open_meteo_base_url: str = "https://api.open-meteo.com/v1/forecast"
    outbreak_radius_km: float = 5.0
    outbreak_min_reports: int = 3
    outbreak_window_days: int = 7

    # automation & security
    n8n_webhook_secret: SecretStr = SecretStr("")
    rate_limit_scans_per_hour: int = 30
    rate_limit_advisory_per_hour: int = 60


@lru_cache
def get_settings() -> Settings:
    """Process-wide settings singleton."""
    return Settings()
