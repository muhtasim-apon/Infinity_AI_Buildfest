"""Outbound HTTP client: host allow-list (SSRF defence) + circuit breaker (spec 16.3, 17.3).

Every outbound call in the app goes through `AllowListedClient`; `check_forbidden.py` rejects
direct `httpx` use elsewhere. Only https to allow-listed hostnames, no redirects to other hosts,
no private/loopback literals.
"""

from __future__ import annotations

import ipaddress
import time
from collections.abc import Callable
from typing import Any
from urllib.parse import urlsplit

import httpx


class OutboundBlockedError(Exception):
    """Raised when a URL is not allowed by the allow-list."""


class CircuitOpenError(Exception):
    """Raised while the circuit breaker is open."""


class CircuitBreaker:
    """Opens after `threshold` consecutive failures for `reset_seconds` (spec: 5 / 60 s)."""

    def __init__(
        self,
        threshold: int = 5,
        reset_seconds: float = 60.0,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        if threshold < 1 or reset_seconds <= 0:
            raise ValueError("threshold >= 1 and reset_seconds > 0 required")
        self.threshold = threshold
        self.reset_seconds = reset_seconds
        self._monotonic = monotonic
        self._failures = 0
        self._opened_at: float | None = None

    @property
    def is_open(self) -> bool:
        if self._opened_at is None:
            return False
        if self._monotonic() - self._opened_at >= self.reset_seconds:
            # half-open: allow one trial call; a failure re-opens immediately
            self._opened_at = None
            self._failures = self.threshold - 1
            return False
        return True

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self.threshold:
            self._opened_at = self._monotonic()


def validate_url(url: str, allowlist: set[str] | frozenset[str]) -> str:
    """Return the URL if allowed, else raise OutboundBlockedError (fail closed)."""
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if parts.scheme != "https":
        raise OutboundBlockedError("only https is allowed")
    if parts.username or parts.password:
        raise OutboundBlockedError("credentials in URL are not allowed")
    if not host:
        raise OutboundBlockedError("missing host")
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        ip = None
    if ip is not None:
        raise OutboundBlockedError("IP literals are not allowed")
    if host not in {h.lower() for h in allowlist}:
        raise OutboundBlockedError("host not in allow-list")
    return url


class AllowListedClient:
    def __init__(
        self,
        allowlist: set[str] | frozenset[str],
        *,
        connect_timeout: float = 3.0,
        read_timeout: float = 8.0,
        breaker: CircuitBreaker | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._allowlist = frozenset(allowlist)
        self._breaker = breaker or CircuitBreaker()
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(read_timeout, connect=connect_timeout),
            follow_redirects=False,  # a redirect could escape the allow-list
            transport=transport,
        )

    async def request(self, method: str, url: str, **kwargs: Any) -> httpx.Response:
        validate_url(url, self._allowlist)
        if self._breaker.is_open:
            raise CircuitOpenError("circuit open")
        try:
            response = await self._client.request(method, url, **kwargs)
        except httpx.HTTPError:
            self._breaker.record_failure()
            raise
        if response.status_code >= 500:
            self._breaker.record_failure()
        else:
            self._breaker.record_success()
        return response

    async def aclose(self) -> None:
        await self._client.aclose()
