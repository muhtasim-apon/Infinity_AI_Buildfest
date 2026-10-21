"""Property-based API fuzzing from the OpenAPI schema (spec 19.4): no request may cause a 5xx.

A real uvicorn server runs in a thread (lifespan included, so Postgres + Redis are live), and
schemathesis generates inputs for every operation. 4xx are expected (CSRF, auth, validation); a 5xx or
a response that violates the declared content type is a failure.
"""

import socket
import threading
import time

import pytest
import schemathesis
import uvicorn
from hypothesis import HealthCheck, settings

from app.main import create_app
from tests.api.identity_support import flush_redis, make_settings, needs_services

pytestmark = [pytest.mark.integration, pytest.mark.security, needs_services]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


@pytest.fixture(scope="module")
def base_url():
    flush_redis()
    port = _free_port()
    app = create_app(make_settings(trusted_hosts=["127.0.0.1", "localhost", "testserver"]))
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    for _ in range(100):
        if server.started:
            break
        time.sleep(0.1)
    assert server.started, "server did not start"
    yield f"http://127.0.0.1:{port}"
    server.should_exit = True
    thread.join(timeout=10)


schema = schemathesis.openapi.from_asgi("/openapi.json", create_app(make_settings()))


@schema.parametrize()
@settings(max_examples=12, deadline=None, suppress_health_check=list(HealthCheck))
def test_no_operation_returns_a_server_error(case, base_url):
    response = case.call(base_url=base_url)
    assert response.status_code < 500, f"{case.method} {case.path} -> {response.status_code}"
