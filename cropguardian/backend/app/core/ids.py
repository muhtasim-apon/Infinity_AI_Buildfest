"""UUID v7 (time-ordered) identifiers, RFC 9562. Random bits come from `secrets`."""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime

from app.core.clock import ensure_utc, utcnow


def uuid7(now: datetime | None = None) -> uuid.UUID:
    millis = int(ensure_utc(now or utcnow()).timestamp() * 1000)
    if not 0 <= millis < 1 << 48:
        raise ValueError("timestamp out of range for UUIDv7")
    rand = secrets.randbits(74)  # 12 bits rand_a + 62 bits rand_b
    value = (
        (millis << 80)
        | (0x7 << 76)
        | ((rand >> 62) << 64)
        | (0b10 << 62)
        | (rand & ((1 << 62) - 1))
    )
    return uuid.UUID(int=value)
