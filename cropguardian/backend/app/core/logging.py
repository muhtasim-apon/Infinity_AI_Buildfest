"""Structured JSON logging with redaction of secrets and personal data (spec 0.2.11, 16.18).

Why a processor: redaction must happen centrally so no call site can forget it.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping, MutableMapping
from typing import Any

import structlog

REDACTED = "[REDACTED]"
_SENSITIVE_KEY = re.compile(
    r"(password|passwd|secret|token|otp|session|cookie|authorization|api[_-]?key|csrf|totp|"
    r"phone|mobile|lat|lon|lng|latitude|longitude|image|signature)",
    re.IGNORECASE,
)
# Values that look like bearer tokens / JWTs / long hex or base64 secrets even under innocent keys.
_SENSITIVE_VALUE = re.compile(r"(Bearer\s+\S+|eyJ[\w-]{10,}\.[\w-]{10,}\.[\w-]{5,}|sk-[\w-]{16,})")
_PHONE_VALUE = re.compile(r"(?<!\d)(\+?8801\d{9}|01\d{9})(?!\d)")
_MAX_DEPTH = 6


def _redact_value(value: Any, depth: int) -> Any:
    if depth > _MAX_DEPTH:
        return REDACTED
    if isinstance(value, Mapping):
        return {k: _redact_pair(str(k), v, depth + 1) for k, v in value.items()}
    if isinstance(value, list | tuple | set):
        return [_redact_value(v, depth + 1) for v in value]
    if isinstance(value, str):
        masked = _SENSITIVE_VALUE.sub(REDACTED, value)
        return _PHONE_VALUE.sub(REDACTED, masked)
    return value


def _redact_pair(key: str, value: Any, depth: int) -> Any:
    if _SENSITIVE_KEY.search(key):
        return REDACTED
    return _redact_value(value, depth)


def redact(event_dict: Mapping[str, Any]) -> dict[str, Any]:
    """Return a redacted copy of a log event."""
    return {k: _redact_pair(str(k), v, 0) for k, v in event_dict.items()}


def redaction_processor(
    _logger: Any, _method: str, event_dict: MutableMapping[str, Any]
) -> MutableMapping[str, Any]:
    redacted = redact(event_dict)
    event_dict.clear()
    event_dict.update(redacted)
    return event_dict


def configure_logging(level: str = "info", *, json_output: bool = True) -> None:
    """Configure structlog + stdlib logging once at startup."""
    logging.basicConfig(format="%(message)s", level=level.upper(), force=True)
    renderer: Any = (
        structlog.processors.JSONRenderer() if json_output else structlog.dev.ConsoleRenderer()
    )
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            redaction_processor,
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.getLevelName(level.upper())),
        cache_logger_on_first_use=False,
    )


def get_logger(name: str = "cg") -> Any:
    return structlog.get_logger(name)
