"""Injectable clock. All times are UTC (spec 0.2.9); Asia/Dhaka conversion happens at the edge."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime

Clock = Callable[[], datetime]


def utcnow() -> datetime:
    """Timezone-aware current UTC time."""
    return datetime.now(UTC)


def ensure_utc(value: datetime) -> datetime:
    """Reject naive datetimes (they silently become local time bugs); normalise others to UTC."""
    if value.tzinfo is None:
        raise ValueError("naive datetime not allowed; use timezone-aware UTC")
    return value.astimezone(UTC)
