"""Rate limiting (threat T14, OWASP LLM10).

Token bucket per user id (authenticated) and per IP (anonymous, e.g. demo session).
In-memory is acceptable because Render free runs a single instance (A4); counters reset on
restart, which only makes limits more lenient briefly. Exceeded → 429 + ``Retry-After``.
Also enforces a daily LLM token budget across all users.
"""

from __future__ import annotations


def check(key: str, limit_per_hour: int) -> tuple[bool, int]:
    """Return ``(allowed, retry_after_seconds)``."""
    raise NotImplementedError
