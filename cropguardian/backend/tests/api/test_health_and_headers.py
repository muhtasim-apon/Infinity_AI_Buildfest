import pytest
from fastapi import APIRouter
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

EXPECTED_HEADERS = [
    "content-security-policy",
    "strict-transport-security",
    "x-content-type-options",
    "referrer-policy",
    "permissions-policy",
    "cross-origin-opener-policy",
    "cross-origin-resource-policy",
    "x-frame-options",
    "x-request-id",
]


def test_health_ok_and_head_allowed(client):
    assert client.get("/health").json()["status"] == "ok"
    assert client.head("/health").status_code == 200
    assert client.get("/healthz").status_code == 200  # legacy alias


@pytest.mark.security
def test_security_headers_on_every_response(client):
    for path in ("/health", "/does-not-exist"):
        r = client.get(path)
        for h in EXPECTED_HEADERS:
            assert h in r.headers, f"{h} missing on {path}"
    csp = client.get("/health").headers["content-security-policy"]
    assert "unsafe-inline" not in csp
    assert "unsafe-eval" not in csp.replace("wasm-unsafe-eval", "")
    assert "frame-ancestors 'none'" in csp


def test_ready_without_database_is_503_and_leaks_nothing(client):
    r = client.get("/health/ready")
    assert r.status_code == 503
    assert "postgresql" not in r.text


@pytest.mark.security
def test_unknown_route_is_problem_json_without_internals(client):
    r = client.get("/nope")
    assert r.status_code == 404
    assert r.headers["content-type"].startswith("application/problem+json")
    assert "Traceback" not in r.text


@pytest.mark.security
def test_unhandled_exception_returns_500_with_request_id_only(settings):
    app = create_app(settings)
    router = APIRouter()

    @router.get("/boom")
    async def boom():
        raise RuntimeError("secret internal detail /etc/passwd")

    app.include_router(router)
    c = TestClient(app, raise_server_exceptions=False)
    r = c.get("/boom")
    assert r.status_code == 500
    assert "secret internal detail" not in r.text
    assert "request_id" in r.json()


@pytest.mark.security
def test_request_id_echoed_and_malformed_replaced(client):
    assert (
        client.get("/health", headers={"X-Request-ID": "abcdef123456"}).headers["x-request-id"]
        == "abcdef123456"
    )
    bad = client.get("/health", headers={"X-Request-ID": "x\ninjected: 1"})
    assert bad.headers["x-request-id"] != "x\ninjected: 1"


@pytest.mark.security
def test_bad_host_rejected(client):
    assert client.get("/health", headers={"Host": "evil.example.com"}).status_code == 400


@pytest.mark.security
def test_oversize_body_413(client):
    r = client.post("/health", content=b"x" * (1_048_576 + 1))
    assert r.status_code == 413


@pytest.mark.security
def test_metrics_hidden_without_token_and_with_wrong_token(client, settings):
    assert client.get("/metrics").status_code == 404
    s = Settings(cg_env="test", metrics_token="t" * 24, _env_file=None)  # type: ignore[call-arg]
    c = TestClient(create_app(s), raise_server_exceptions=False)
    assert c.get("/metrics").status_code == 404
    assert c.get("/metrics", headers={"X-Metrics-Token": "wrong"}).status_code == 404
    assert c.get("/metrics", headers={"X-Metrics-Token": "t" * 24}).status_code == 200


@pytest.mark.security
def test_docs_disabled_in_production():
    s = Settings(
        cg_env="production",
        secret_key="k" * 40,
        app_base_url="https://a.example.org",
        database_url="postgresql://u:p@h/db",
        trusted_hosts=["testserver"],
        _env_file=None,
    )  # type: ignore[call-arg]
    c = TestClient(create_app(s), raise_server_exceptions=False)
    assert c.get("/docs").status_code == 404
    assert c.get("/openapi.json").status_code == 404


@pytest.mark.security
def test_no_cors_headers_by_default(client):
    r = client.get("/health", headers={"Origin": "https://evil.example.com"})
    assert "access-control-allow-origin" not in r.headers


def test_validation_error_does_not_echo_values(settings):
    app = create_app(settings)
    router = APIRouter()

    @router.get("/n")
    async def n(x: int):
        return x

    app.include_router(router)
    r = TestClient(app).get("/n", params={"x": "super-secret-value"})
    assert r.status_code == 422
    assert "super-secret-value" not in r.text
