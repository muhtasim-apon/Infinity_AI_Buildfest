"""Behaviours needed for a platform deploy (Render): health checks must pass, misconfiguration must
fail closed, and request logging must be useful without leaking query strings."""

import logging

import pytest
from fastapi.testclient import TestClient

from app.core.config import ConfigError, Settings
from app.main import create_app

PUBLIC_HOST = "cropgurdian-backend.onrender.com"


def prod_settings(**over) -> Settings:
    base = {
        "cg_env": "production",
        "secret_key": "k" * 40,
        "app_base_url": "https://web.example.org",
        "database_url": "postgresql://u:p@h/db",
        "redis_url": "redis://:pw@red:6379/0",
        "sms_provider": "disabled",
        "email_provider": "disabled",
        "trusted_hosts": [PUBLIC_HOST],
        "_env_file": None,
    }
    return Settings(**{**base, **over})


@pytest.fixture
def prod_client() -> TestClient:
    return TestClient(create_app(prod_settings()), raise_server_exceptions=False)


@pytest.mark.parametrize("path", ["/health", "/healthz"])
def test_liveness_passes_for_any_host_header(prod_client, path):
    # Platform health checkers use an internal address, not the public hostname.
    for host in ("10.24.6.28:10000", "localhost", "anything.internal"):
        assert prod_client.get(path, headers={"Host": host}).status_code == 200


@pytest.mark.security
def test_other_paths_are_still_host_checked(prod_client):
    assert prod_client.get("/health/ready", headers={"Host": "10.24.6.28"}).status_code == 400
    assert prod_client.get("/nope", headers={"Host": "evil.example.com"}).status_code == 400
    assert prod_client.get("/nope", headers={"Host": PUBLIC_HOST}).status_code == 404


@pytest.mark.security
def test_host_exemption_is_exact_not_a_prefix(prod_client):
    for path in ("/healthz/x", "/health/../metrics", "/healthcheck", "/health/ready"):
        assert prod_client.get(path, headers={"Host": "evil.example.com"}).status_code == 400


@pytest.mark.security
def test_render_without_cg_env_defaults_to_production_and_refuses_insecure_config(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.delenv("CG_ENV", raising=False)
    # CG_ENV forgotten + no secrets: the service must REFUSE to start, not run in dev mode.
    with pytest.raises(ConfigError):
        Settings(_env_file=None)
    # CG_ENV forgotten but otherwise fully configured: it runs as production (docs off).
    monkeypatch.setenv("SECRET_KEY", "k" * 40)
    monkeypatch.setenv("APP_BASE_URL", "https://web.example.org")
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@h/db")
    monkeypatch.setenv("REDIS_URL", "redis://:pw@red:6379/0")
    monkeypatch.setenv("SMS_PROVIDER", "disabled")
    monkeypatch.setenv("EMAIL_PROVIDER", "disabled")
    monkeypatch.setenv("TRUSTED_HOSTS", f'["{PUBLIC_HOST}"]')
    s = Settings(_env_file=None)
    assert s.cg_env == "production"
    client = TestClient(create_app(s), raise_server_exceptions=False)
    assert client.get("/docs", headers={"Host": PUBLIC_HOST}).status_code == 404


def test_not_on_render_defaults_to_development(monkeypatch):
    monkeypatch.delenv("RENDER", raising=False)
    monkeypatch.delenv("CG_ENV", raising=False)
    assert Settings(_env_file=None).cg_env == "development"


def test_explicit_cg_env_wins_over_render(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.setenv("CG_ENV", "test")
    assert Settings(_env_file=None).cg_env == "test"


@pytest.mark.security
def test_request_log_has_path_status_duration_but_never_the_query(capsys):
    app = create_app(prod_settings(log_level="debug"))
    client = TestClient(app, raise_server_exceptions=False)
    client.get("/nope?token=SECRET123&otp=999", headers={"Host": PUBLIC_HOST})
    out = capsys.readouterr().out
    assert '"event": "request"' in out
    assert '"path": "/nope"' in out
    assert '"status": 404' in out
    assert "duration_ms" in out
    assert "SECRET123" not in out
    assert "otp=999" not in out
    logging.getLogger().handlers.clear()


def test_rejected_requests_are_logged_too(capsys):
    app = create_app(prod_settings())
    TestClient(app, raise_server_exceptions=False).get(
        "/nope", headers={"Host": "evil.example.com"}
    )
    out = capsys.readouterr().out
    assert '"status": 400' in out
