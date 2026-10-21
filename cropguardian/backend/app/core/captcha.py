"""Self-hosted proof-of-work CAPTCHA, ALTCHA-style (spec 16.15). No third party, no tracking.

The server signs `challenge = sha256(salt + secret_number)` with an expiry and an issue time.
The browser searches for the number, then posts the payload back. The server checks the signature,
expiry, the work itself and a minimum elapsed time, and burns the challenge in Redis (one use).
This slows scripted abuse; it is not a human check, and the docs say so.
"""

from __future__ import annotations

import base64
import json
import secrets
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.clock import utcnow
from app.core.errors import AppError
from app.core.security import hmac_hex, safe_equal, sha256_hex

MAX_NUMBER = 50_000
TTL_SECONDS = 300
MIN_ELAPSED_SECONDS = 2


@dataclass(frozen=True)
class Challenge:
    algorithm: str
    challenge: str
    salt: str
    signature: str
    maxnumber: int
    issued_at: int
    expires_at: int


class Captcha:
    def __init__(
        self,
        secret_key: str,
        redis: Redis | None,
        *,
        bypass: bool = False,
        now: Callable[[], float] | None = None,
    ) -> None:
        self._key = secret_key
        self._redis = redis
        self._bypass = bypass
        self._now = now or (lambda: utcnow().timestamp())

    def _sign(self, challenge: str, salt: str, issued: int, expires: int) -> str:
        return hmac_hex(self._key, "captcha", challenge, salt, str(issued), str(expires))

    def issue(self) -> Challenge:
        issued = int(self._now())
        expires = issued + TTL_SECONDS
        salt = secrets.token_hex(12)
        number = secrets.randbelow(MAX_NUMBER + 1)
        challenge = sha256_hex(f"{salt}{number}")
        return Challenge(
            "SHA-256", challenge, salt, self._sign(challenge, salt, issued, expires),
            MAX_NUMBER, issued, expires,
        )  # fmt: skip

    async def verify(self, payload: str | None) -> None:
        """Raises AppError 400 captcha_invalid / 503 when unavailable. Returns None on success."""
        if self._bypass:
            return
        data = self._decode(payload)
        challenge, salt = str(data["challenge"]), str(data["salt"])
        issued, expires, number = (
            int(data["issued_at"]),
            int(data["expires_at"]),
            int(data["number"]),
        )
        if not safe_equal(str(data["signature"]), self._sign(challenge, salt, issued, expires)):
            raise _invalid()
        now = self._now()
        if now > expires or now - issued < MIN_ELAPSED_SECONDS:
            raise _invalid()
        if not 0 <= number <= MAX_NUMBER or not safe_equal(
            sha256_hex(f"{salt}{number}"), challenge
        ):
            raise _invalid()
        await self._burn(challenge)

    async def _burn(self, challenge: str) -> None:
        if self._redis is None:
            raise AppError(503, "captcha_unavailable", "Try again shortly.")
        try:
            fresh = await self._redis.set(
                f"cg:captcha:{challenge}", "1", nx=True, ex=TTL_SECONDS * 2
            )
        except (RedisError, OSError) as exc:
            raise AppError(503, "captcha_unavailable", "Try again shortly.") from exc
        if not fresh:
            raise _invalid()  # replay

    @staticmethod
    def _decode(payload: str | None) -> dict[str, Any]:
        if not payload or len(payload) > 2048:
            raise _invalid()
        try:
            data = json.loads(base64.b64decode(payload, validate=True))
            if not isinstance(data, dict) or not {
                "challenge", "salt", "signature", "issued_at", "expires_at", "number",
            } <= set(data):  # fmt: skip
                raise _invalid()
            int(data["number"]), int(data["issued_at"]), int(data["expires_at"])  # type check only
        except (ValueError, TypeError) as exc:
            raise _invalid() from exc
        return data


def _invalid() -> AppError:
    return AppError(400, "captcha_invalid", "Please solve the check again.")


def solve(challenge: Challenge) -> str:
    """Reference solver used by tests and the e2e script (the browser has its own in JS)."""
    for number in range(challenge.maxnumber + 1):
        if sha256_hex(f"{challenge.salt}{number}") == challenge.challenge:
            body = {
                "challenge": challenge.challenge, "salt": challenge.salt,
                "signature": challenge.signature, "issued_at": challenge.issued_at,
                "expires_at": challenge.expires_at, "number": number,
            }  # fmt: skip
            return base64.b64encode(json.dumps(body).encode()).decode()
    raise ValueError("no solution")  # pragma: no cover - unreachable for a genuine challenge
