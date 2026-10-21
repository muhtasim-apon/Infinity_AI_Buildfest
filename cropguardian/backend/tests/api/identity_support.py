"""Shared harness for identity API tests: a running app over real Postgres + Redis, a CSRF-aware
client, and helpers that create staff users directly in the database (the owner's job in real life)."""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator

import httpx
import psycopg
import pytest
from fastapi.testclient import TestClient
from redis import Redis as SyncRedis

from app.core.config import Settings
from app.core.security import hash_password
from app.main import create_app

REDIS_URL = os.environ.get("TEST_REDIS_URL", "")
API_DB = os.environ.get("TEST_API_DATABASE_URL", "")
SUPER_DB = os.environ.get("TEST_SUPER_DATABASE_URL", "")
ORIGIN = "https://testserver"
STRONG = "river-lantern-orchard-47"
STAFF_PW = "Tr0ub4dor&3-quietly-purple"

needs_services = pytest.mark.skipif(
    not (REDIS_URL and API_DB and SUPER_DB), reason="TEST_* service URLs not set"
)


def make_settings(**over: object) -> Settings:
    base: dict[str, object] = {
        "cg_env": "test",
        "database_url": API_DB,
        "redis_url": REDIS_URL,
        "app_base_url": ORIGIN,
        "api_base_url": ORIGIN,
        "captcha_bypass": True,
        "demo_enabled": True,
        "demo_seed_on_start": True,
        "sms_provider": "disabled",
        "email_provider": "disabled",
        "secret_key": "test-secret-key-0123456789abcdef0123456789",
    }
    return Settings(_env_file=None, **{**base, **over})  # type: ignore[arg-type]


class Browser:
    """One cookie jar over a shared TestClient (and so a shared event loop and connection pool)."""

    def __init__(self, client: TestClient) -> None:
        self._client = client
        self.cookies = httpx.Cookies()

    def _send(self, method: str, path: str, **kw):  # type: ignore[no-untyped-def]
        self._client.cookies = self.cookies
        try:
            return getattr(self._client, method)(path, **kw)
        finally:
            self.cookies = httpx.Cookies(self._client.cookies)

    def get(self, path: str, **kw):  # type: ignore[no-untyped-def]
        return self._send("get", path, **kw)

    def post(self, path: str, **kw):  # type: ignore[no-untyped-def]
        return self._send("post", path, **kw)

    def put(self, path: str, **kw):  # type: ignore[no-untyped-def]
        return self._send("put", path, **kw)

    def patch(self, path: str, **kw):  # type: ignore[no-untyped-def]
        return self._send("patch", path, **kw)

    def delete(self, path: str, **kw):  # type: ignore[no-untyped-def]
        return self._send("delete", path, **kw)


class Api:
    """CSRF-aware wrapper: remembers the token, sends Origin, follows token rotation."""

    def __init__(self, client: TestClient) -> None:
        self.shared = client
        self.c = Browser(client)
        self.csrf = ""

    def spawn(self) -> Api:
        """A second, independent browser (own cookies) on the same running app."""
        other = Api(self.shared)
        other.refresh_csrf()
        return other

    def refresh_csrf(self) -> str:
        r = self.c.get("/api/v1/auth/csrf")
        self.csrf = r.json()["csrf_token"]
        return self.csrf

    def _headers(self, extra: dict[str, str] | None = None, *, csrf: bool = True) -> dict[str, str]:
        headers = {"Origin": ORIGIN}
        if csrf:
            headers["X-CSRF-Token"] = self.csrf
        return {**headers, **(extra or {})}

    def _learn(self, response):  # type: ignore[no-untyped-def]
        try:
            token = response.json().get("csrf_token")
        except ValueError:
            token = None
        if token:
            self.csrf = token
        return response

    def get(self, path: str, **kw):  # type: ignore[no-untyped-def]
        return self._learn(self.c.get(path, **kw))

    def post(self, path: str, json=None, *, csrf: bool = True, headers=None):  # type: ignore[no-untyped-def]
        return self._learn(self.c.post(path, json=json, headers=self._headers(headers, csrf=csrf)))

    def put(self, path: str, json=None):  # type: ignore[no-untyped-def]
        return self._learn(self.c.put(path, json=json, headers=self._headers()))

    def patch(self, path: str, json=None):  # type: ignore[no-untyped-def]
        return self._learn(self.c.patch(path, json=json, headers=self._headers()))

    def delete(self, path: str):  # type: ignore[no-untyped-def]
        return self._learn(self.c.delete(path, headers=self._headers()))

    def sms_code(self, phone: str) -> str:
        return self.c.get(f"/api/v1/__test__/sms/{phone}").json()["code"]

    def email_link(self, email: str) -> str:
        return self.c.get("/api/v1/__test__/email-link", params={"email": email}).json()["link"]


def flush_redis() -> None:
    client = SyncRedis.from_url(REDIS_URL)
    client.flushdb()
    client.close()


@pytest.fixture
def app_client() -> Iterator[Api]:
    flush_redis()
    app = create_app(make_settings())
    with TestClient(app, base_url=ORIGIN, raise_server_exceptions=False) as client:

        async def no_sleep(_seconds: float) -> None:
            return None

        app.state.container.auth.sleep = no_sleep  # lockout delays are tested by value, not waited
        api = Api(client)
        api.refresh_csrf()
        yield api


def sql(query: str, params: tuple = ()) -> list[tuple]:
    with psycopg.connect(SUPER_DB, autocommit=True) as conn, conn.cursor() as cur:
        cur.execute(query, params)
        return cur.fetchall() if cur.description else []


def new_phone() -> str:
    return f"+88017{uuid.uuid4().int % 10**8:08d}"


def local_phone(e164: str) -> str:
    return "0" + e164[4:]


def make_staff(role: str = "ADMIN", password: str = STAFF_PW) -> tuple[str, str]:
    """Create an ACTIVE staff user without TOTP. Returns (email, user_id)."""
    uid = str(uuid.uuid4())
    email = f"staff-{uid[:8]}@example.org"
    sql(
        "INSERT INTO users (id, tenant_id, role, email, display_name, password_hash, status, "
        "region_codes, email_verified_at) VALUES (%s,'real',%s,%s,'Test Staff',%s,'ACTIVE',"
        "ARRAY['D1'], now())",
        (uid, role, email, hash_password(password)),
    )
    return email, uid


def register_farmer(api: Api, phone: str | None = None, password: str = STRONG) -> str:
    phone = phone or new_phone()
    api.c.post("/api/v1/__test__/reset-limits")  # helper may be called several times per test
    r = api.post(
        "/api/v1/auth/register/farmer",
        {
            "phone": local_phone(phone), "password": password, "display_name": "Rahima",
            "locale": "bn", "accept_service": True, "training_use": True,
        },
    )  # fmt: skip
    assert r.status_code == 202, r.text
    verify = api.post("/api/v1/auth/otp/verify", {"phone": phone, "code": api.sms_code(phone)})
    assert verify.status_code == 200, verify.text
    return phone
