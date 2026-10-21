"""Bangladesh mobile numbers to E.164 (pure; no I/O).

Accepts Latin or Bangla digits and the usual separators. `[0-9]` is used on purpose: the regex
digit class also matches Bangla digits, which must be converted explicitly, not slip through.
"""

from __future__ import annotations

import re

_BANGLA_DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")
_SEPARATORS = re.compile(r"[ \-().\u200c\u200d]")  # space, dash, parens, dot, ZWNJ, ZWJ
_E164_BD = re.compile(r"\+8801[3-9][0-9]{8}")
_MAX_INPUT = 40


class PhoneError(ValueError):
    """Not a valid Bangladesh mobile number."""


def normalise_phone(raw: str) -> str:
    if not isinstance(raw, str) or not raw.strip() or len(raw) > _MAX_INPUT:
        raise PhoneError("invalid phone")
    digits = _SEPARATORS.sub("", raw.strip().translate(_BANGLA_DIGITS))
    if digits.startswith("+"):
        candidate = digits
    elif digits.startswith("00880"):
        candidate = "+" + digits[2:]
    elif digits.startswith("880"):
        candidate = "+" + digits
    elif digits.startswith("01"):
        candidate = "+880" + digits[1:]
    else:
        raise PhoneError("invalid phone")
    if not _E164_BD.fullmatch(candidate):
        raise PhoneError("invalid phone")
    return candidate


def mask_phone(e164: str) -> str:
    """For UI/logs: keep the country code and the last two digits only."""
    return e164[:4] + "*" * max(len(e164) - 6, 0) + e164[-2:] if len(e164) > 6 else "*" * len(e164)
