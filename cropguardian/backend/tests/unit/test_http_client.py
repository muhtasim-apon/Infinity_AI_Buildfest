import httpx
import pytest

from app.core.http import (
    AllowListedClient,
    CircuitBreaker,
    CircuitOpenError,
    OutboundBlockedError,
    validate_url,
)

ALLOW = {"api.anthropic.com"}


@pytest.mark.security
@pytest.mark.parametrize(
    "url",
    [
        "http://api.anthropic.com/v1",  # not https
        "https://evil.example.com/",
        "https://127.0.0.1/",
        "https://169.254.169.254/latest/meta-data",
        "https://user:pw@api.anthropic.com/",
        "https://api.anthropic.com.evil.com/",
        "ftp://api.anthropic.com/",
        "file:///etc/passwd",
        "https:///nohost",
    ],
)
def test_blocked_urls(url):
    with pytest.raises(OutboundBlockedError):
        validate_url(url, ALLOW)


def test_allowed_url_passes():
    assert validate_url("https://API.anthropic.com/v1/messages", ALLOW)


def test_breaker_opens_after_threshold_and_half_opens():
    now = [0.0]
    b = CircuitBreaker(threshold=3, reset_seconds=60, monotonic=lambda: now[0])
    for _ in range(3):
        b.record_failure()
    assert b.is_open
    now[0] = 61
    assert not b.is_open  # half-open trial
    b.record_failure()  # trial fails -> re-opens immediately
    assert b.is_open


def test_breaker_success_resets():
    b = CircuitBreaker(threshold=2)
    b.record_failure()
    b.record_success()
    b.record_failure()
    assert not b.is_open


def test_breaker_rejects_bad_params():
    with pytest.raises(ValueError):
        CircuitBreaker(threshold=0)
    with pytest.raises(ValueError):
        CircuitBreaker(reset_seconds=0)


async def test_client_blocks_disallowed_host_before_network():
    client = AllowListedClient(ALLOW, transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    with pytest.raises(OutboundBlockedError):
        await client.request("GET", "https://evil.example.com/")
    await client.aclose()


async def test_client_opens_circuit_on_5xx_and_does_not_follow_redirects():
    calls = []

    def handler(request):
        calls.append(request.url.host)
        return httpx.Response(503)

    breaker = CircuitBreaker(threshold=2)
    client = AllowListedClient(ALLOW, breaker=breaker, transport=httpx.MockTransport(handler))
    for _ in range(2):
        r = await client.request("GET", "https://api.anthropic.com/x")
        assert r.status_code == 503
    with pytest.raises(CircuitOpenError):
        await client.request("GET", "https://api.anthropic.com/x")
    assert len(calls) == 2
    await client.aclose()


async def test_redirect_is_not_followed():
    def handler(request):
        return httpx.Response(302, headers={"location": "https://evil.example.com/"})

    client = AllowListedClient(ALLOW, transport=httpx.MockTransport(handler))
    r = await client.request("GET", "https://api.anthropic.com/x")
    assert r.status_code == 302
    await client.aclose()
