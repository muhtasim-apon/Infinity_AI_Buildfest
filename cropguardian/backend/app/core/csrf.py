"""CSRF defence (spec 16.6): double-submit cookie bound to the session + Origin check.

The token is `nonce.HMAC(secret_key, nonce|binding)`. `binding` is the session's csrf secret (or a
fixed label before login), so a token minted for one session is useless in another, and a cookie
planted from a sibling subdomain cannot be forged without SECRET_KEY.
"""

from __future__ import annotations

from collections.abc import Iterable
from urllib.parse import urlsplit

from app.core.security import hmac_hex, new_token, safe_equal

COOKIE_NAME = "__Host-cg_csrf"
HEADER_NAME = "x-csrf-token"
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS"})
ANON_BINDING = "anonymous"


def make_token(secret_key: str, binding: str) -> str:
    nonce = new_token(16)
    return f"{nonce}.{hmac_hex(secret_key, 'csrf', nonce, binding)}"


def token_is_valid(secret_key: str, binding: str, token: str) -> bool:
    nonce, dot, mac = token.partition(".")
    if not dot or not nonce or not mac:
        return False
    return safe_equal(mac, hmac_hex(secret_key, "csrf", nonce, binding))


def origin_allowed(
    origin_header: str | None, referer_header: str | None, allowed: Iterable[str]
) -> bool:
    """Unsafe requests must say where they came from. Missing both => refuse (fail closed)."""
    allowed_set = {a.rstrip("/").lower() for a in allowed if a}
    if origin_header and origin_header != "null":
        return origin_header.rstrip("/").lower() in allowed_set
    if origin_header == "null" or not referer_header:
        return False
    parts = urlsplit(referer_header)
    if not parts.scheme or not parts.netloc:
        return False
    return f"{parts.scheme}://{parts.netloc}".lower() in allowed_set


def check_request(  # noqa: PLR0913
    *,
    method: str,
    secret_key: str,
    binding: str,
    cookie_token: str | None,
    header_token: str | None,
    origin: str | None,
    referer: str | None,
    allowed_origins: Iterable[str],
) -> str:
    """Returns "" when the request passes, else a short reason code (for logs/tests)."""
    if method.upper() in SAFE_METHODS:
        return ""
    if not origin_allowed(origin, referer, allowed_origins):
        return "origin"
    if not cookie_token or not header_token or not safe_equal(cookie_token, header_token):
        return "mismatch"
    if not token_is_valid(secret_key, binding, header_token):
        return "invalid"
    return ""
