"""Redis sliding-window rate limits (spec 16.8). One Lua script checks and records every window of a
rule atomically, so concurrent requests cannot slip past the limit together.

Fail-closed rules (login, OTP, register, reset, demo, CAPTCHA) answer 503 when Redis is unreachable;
read rules fail open and log the outage once per call.
"""

from __future__ import annotations

import hashlib
import time
from collections.abc import Callable
from dataclasses import dataclass

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.errors import AppError
from app.core.logging import get_logger

_log = get_logger("cg.ratelimit")

_LUA = """
local now = tonumber(ARGV[1])
local member = ARGV[2]
local n = #KEYS
for i = 1, n do
  local limit = tonumber(ARGV[1 + i * 2])
  local window = tonumber(ARGV[2 + i * 2])
  redis.call('ZREMRANGEBYSCORE', KEYS[i], 0, now - window)
  if redis.call('ZCARD', KEYS[i]) >= limit then
    local oldest = redis.call('ZRANGE', KEYS[i], 0, 0, 'WITHSCORES')
    return {0, math.max(tonumber(oldest[2]) + window - now, 1)}
  end
end
for i = 1, n do
  local window = tonumber(ARGV[2 + i * 2])
  redis.call('ZADD', KEYS[i], now, member)
  redis.call('PEXPIRE', KEYS[i], window)
end
return {1, 0}
"""


@dataclass(frozen=True)
class Rule:
    name: str
    windows: tuple[tuple[int, int], ...]  # (limit, seconds)
    fail_closed: bool = False


@dataclass(frozen=True)
class Decision:
    allowed: bool
    retry_after: int = 0  # whole seconds, >= 1 when not allowed


MIN, HOUR, DAY = 60, 3600, 86400
RULES: dict[str, Rule] = {
    r.name: r
    for r in (
        Rule("api_user", ((120, MIN),)),
        Rule("api_anon", ((60, MIN),)),
        Rule("login", ((5, MIN), (20, HOUR)), fail_closed=True),
        Rule("register", ((5, HOUR),), fail_closed=True),
        Rule("otp_send", ((1, MIN), (5, HOUR)), fail_closed=True),  # per phone
        Rule("otp_send_ip", ((5, HOUR),), fail_closed=True),  # per IP
        Rule("otp_verify", ((10, HOUR),), fail_closed=True),
        Rule("password_reset", ((3, HOUR),), fail_closed=True),
        Rule("demo_session", ((10, HOUR),), fail_closed=True),
        Rule("captcha", ((30, MIN),), fail_closed=True),
        Rule("scan_create", ((30, HOUR), (100, DAY))),
        Rule("analyze", ((30, HOUR),)),
        Rule("reviewer_action", ((600, HOUR),)),
        Rule("alert_approve", ((30, HOUR),)),
        Rule("export_delete", ((2, DAY),)),
        Rule("public_read", ((120, MIN),)),
        Rule("client_error", ((30, MIN),)),
        Rule("webhook", ((60, MIN),)),
        Rule("admin", ((300, MIN),)),
        Rule("step_up", ((5, 10 * MIN),), fail_closed=True),
        Rule("totp_verify", ((5, 10 * MIN),), fail_closed=True),
        Rule("email_token", ((10, HOUR),), fail_closed=True),
    )
}


def _digest(identifier: str) -> str:
    """Identifiers (phones, emails, IPs) are hashed so Redis keys never hold personal data."""
    return hashlib.sha256(identifier.encode()).hexdigest()[:32]


class RateLimiter:
    def __init__(self, redis: Redis | None, now_ms: Callable[[], int] | None = None) -> None:
        self._redis = redis
        self._now_ms = now_ms or (lambda: int(time.time() * 1000))
        self._seq = 0

    async def hit(self, rule_name: str, identifier: str) -> Decision:
        rule = RULES[rule_name]
        if self._redis is None:
            return self._unavailable(rule, "not configured")
        now = self._now_ms()
        self._seq += 1
        member = f"{now}-{self._seq}-{time.perf_counter_ns()}"
        base = f"cg:rl:{rule.name}:{_digest(identifier)}"
        keys = [f"{base}:{seconds}" for _, seconds in rule.windows]
        argv: list[int | str] = [now, member]
        for limit, seconds in rule.windows:
            argv += [limit, seconds * 1000]
        try:
            allowed, retry_ms = await self._redis.eval(_LUA, len(keys), *keys, *argv)  # type: ignore[misc,arg-type]
        except (RedisError, OSError) as exc:
            return self._unavailable(rule, type(exc).__name__)
        if allowed:
            return Decision(True)
        return Decision(False, max(1, -(-int(retry_ms) // 1000)))

    def _unavailable(self, rule: Rule, why: str) -> Decision:
        _log.warning(
            "ratelimit_unavailable", rule=rule.name, reason=why, fail_closed=rule.fail_closed
        )
        if rule.fail_closed:
            raise AppError(503, "rate_limiter_unavailable", "Try again shortly.")
        return Decision(True)

    async def enforce(self, rule_name: str, identifier: str) -> None:
        decision = await self.hit(rule_name, identifier)
        if not decision.allowed:
            raise AppError(429, "rate_limited", extra={"retry_after": decision.retry_after})
