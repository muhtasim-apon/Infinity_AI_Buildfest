"""Open-redirect defence (spec 16.6): only same-site relative paths are ever followed."""

from __future__ import annotations

import re
from urllib.parse import unquote, urlsplit

MAX_LEN = 512
_CONTROL = re.compile("[" + chr(0) + "-" + chr(31) + chr(127) + "]")


def safe_return_to(value: str | None, default: str = "/") -> str:
    """`value` if it is a plain in-app path, else `default`. Checked before AND after decoding."""
    if not value or len(value) > MAX_LEN:
        return default
    for candidate in (value, unquote(value), unquote(unquote(value))):
        if not _is_plain_path(candidate):
            return default
    return value


def _is_plain_path(path: str) -> bool:
    if (
        not path.startswith("/")
        or path.startswith("//")
        or chr(92) in path
        or _CONTROL.search(path)
    ):
        return False
    parts = urlsplit(path)
    return not parts.scheme and not parts.netloc
