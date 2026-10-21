"""Authorization matrix harness: every OpenAPI route x every principal (spec 16.5).

Loads `authz_matrix.yaml`, builds one signed-in browser per principal, and asserts the exact outcome.
A route that exists but is missing from the matrix fails the build.
"""

import time
import uuid
from pathlib import Path

import pyotp
import pytest
import yaml
from fastapi.testclient import TestClient

from app.main import create_app
from tests.api.identity_support import (
    STAFF_PW,
    Api,
    flush_redis,
    make_settings,
    make_staff,
    needs_services,
    register_farmer,
)

pytestmark = [pytest.mark.security, pytest.mark.integration, needs_services]

MATRIX = yaml.safe_load((Path(__file__).parent / "authz_matrix.yaml").read_text(encoding="utf-8"))
PRINCIPALS = [
    "anonymous",
    "farmer",
    "reviewer",
    "admin",
    "demo_farmer",
    "demo_reviewer",
    "demo_admin",
]
OUTCOMES = {
    "public": dict.fromkeys(PRINCIPALS, "allow"),
    "session": {**dict.fromkeys(PRINCIPALS, "allow"), "anonymous": 401},
    "farmer_only": {
        "anonymous": 401,
        "farmer": "allow",
        "reviewer": 403,
        "admin": 403,
        "demo_farmer": "allow",
        "demo_reviewer": 403,
        "demo_admin": 403,
    },  # fmt: skip
    "staff_only": {
        "anonymous": 401,
        "farmer": 403,
        "reviewer": "allow",
        "admin": "allow",
        "demo_farmer": 403,
        "demo_reviewer": 403,
        "demo_admin": 403,
    },  # fmt: skip
    "admin_only": {
        "anonymous": 404,
        "farmer": 404,
        "reviewer": 404,
        "admin": "allow",
        "demo_farmer": 404,
        "demo_reviewer": 404,
        "demo_admin": "allow",
    },  # fmt: skip
}


def staff_browser(api: Api, role: str, *, step_up: bool) -> Api:
    email, _ = make_staff(role)
    assert (
        api.post("/api/v1/auth/login", {"identifier": email, "password": STAFF_PW}).status_code
        == 200
    )
    totp = pyotp.TOTP(api.post("/api/v1/auth/totp/setup").json()["secret"])
    assert api.post("/api/v1/auth/totp/confirm", {"code": totp.now()}).status_code == 200
    if step_up:
        step = api.post("/api/v1/auth/step-up", {"code": totp.at(time.time() + 30)})
        assert step.status_code == 200, step.text
    return api


def build(world: Api, name: str) -> Api:
    api = world.spawn()
    world.c.post("/api/v1/__test__/reset-limits")
    if name == "anonymous":
        return api
    if name == "farmer":
        register_farmer(api)
    elif name == "reviewer":
        staff_browser(api, "REVIEWER", step_up=False)
    elif name == "admin":
        staff_browser(api, "ADMIN", step_up=True)
    else:
        role = name.upper()
        assert api.post("/api/v1/demo/session", {"role": role}).status_code == 201
    return api


@pytest.fixture(scope="module")
def world():
    flush_redis()
    app = create_app(make_settings())
    with TestClient(app, base_url="https://testserver", raise_server_exceptions=False) as client:

        async def no_sleep(_s: float) -> None:
            return None

        app.state.container.auth.sleep = no_sleep
        root = Api(client)
        root.refresh_csrf()
        browsers = {name: build(root, name) for name in PRINCIPALS}
        yield root, browsers, app


def openapi_routes(app) -> set[str]:
    out = set()
    for path, ops in app.openapi()["paths"].items():
        for method in ops:
            if method.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                out.add(f"{method.upper()} {path}")
    return out


def test_every_route_has_a_matrix_entry(world):
    _, _, app = world
    routes = openapi_routes(app)
    missing = sorted(routes - set(MATRIX["routes"]))
    stale = sorted(set(MATRIX["routes"]) - routes)
    assert not missing, f"routes without an authz matrix entry: {missing}"
    assert not stale, f"matrix entries for routes that no longer exist: {stale}"
    for key, spec in MATRIX["routes"].items():
        assert spec["kind"] in OUTCOMES, key


def request_for(api: Api, key: str, spec: dict):
    method, path = key.split(" ", 1)
    for name, value in (spec.get("path") or {}).items():
        path = path.replace("{" + name + "}", value)
    body = spec.get("body")
    if body is not None:
        body = {k: (v.replace("{rand}", uuid.uuid4().hex[:10]) if isinstance(v, str) else v)
                for k, v in body.items()}  # fmt: skip
    return (
        getattr(api, method.lower())(
            path, **({"json": body} if body is not None and method in ("POST",) else {})
        )
        if method in ("GET", "DELETE", "POST")
        else getattr(api, method.lower())(path, body)
    )


CASES = [(key, principal) for key in MATRIX["routes"] for principal in PRINCIPALS]


@pytest.mark.parametrize(("key", "principal"), CASES, ids=[f"{k}|{p}" for k, p in CASES])
def test_matrix(world, key, principal):
    root, browsers, _ = world
    spec = MATRIX["routes"][key]
    expected = OUTCOMES[spec["kind"]][principal]
    expected = (spec.get("overrides") or {}).get(principal, expected)
    root.c.post("/api/v1/__test__/reset-limits")  # the matrix makes many calls from one address
    api = build(root, principal) if spec.get("destructive") else browsers[principal]
    response = request_for(api, key, spec)
    if expected == "allow":
        allowed = spec.get("ok") or MATRIX["default_ok"]
        assert (
            response.status_code in allowed
        ), f"{key} as {principal}: {response.status_code} {response.text}"
    else:
        assert (
            response.status_code == expected
        ), f"{key} as {principal}: {response.status_code} {response.text}"
