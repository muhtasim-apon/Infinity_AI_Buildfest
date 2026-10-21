from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app


@pytest.fixture
def settings() -> Settings:
    return Settings(cg_env="test", metrics_token="", database_url="", _env_file=None)  # type: ignore[call-arg]


@pytest.fixture
def client(settings: Settings) -> TestClient:
    return TestClient(create_app(settings), raise_server_exceptions=False)
