"""Outgoing messages: OTP SMS and transactional email (spec 14, 16.4, 16.7).

- Bangla first, English second, in one message (locale is a preference, not a barrier).
- HTML is autoescaped (Jinja2) and every variable passes `clean_text` (control characters,
  newlines, length), so a hostile name or user-agent cannot inject headers, markup or links.
- Links are built by the caller from PUBLIC_ORIGIN; `render_email` refuses anything that is
  not https (http only for localhost in development).
- `StrictUndefined`: a missing variable is an error, never a silently blank sentence.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates"
_CONTROL = re.compile("[" + chr(0) + "-" + chr(31) + chr(127) + chr(0x2028) + chr(0x2029) + "]")
MAX_FIELD = 120

_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(["html"]),
    undefined=StrictUndefined,
    keep_trailing_newline=True,
)

EMAIL_KINDS = ("verify", "reset", "invite", "new_device")

SUBJECTS = {
    "verify": "ইমেইল যাচাই করুন · Verify your email",
    "reset": "পাসওয়ার্ড পুনরুদ্ধার · Reset your password",
    "invite": "ফসল রক্ষীতে আমন্ত্রণ · Invitation to Crop Guardian",
    "new_device": "নতুন ডিভাইস থেকে লগইন · New device sign-in",
}


class MessageError(ValueError):
    """Bad template input (unknown kind, unsafe link, missing variable)."""


@dataclass(frozen=True)
class Email:
    subject: str
    text: str
    html: str


def clean_text(value: object, limit: int = MAX_FIELD) -> str:
    """NFC, drop control characters (header/line injection), collapse spaces, bound the length."""
    text = unicodedata.normalize("NFC", str(value))
    text = _CONTROL.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def check_link(link: str, *, allow_http_localhost: bool = False) -> str:
    parts = urlsplit(link)
    host = (parts.hostname or "").lower()
    ok_scheme = parts.scheme == "https" or (
        allow_http_localhost and parts.scheme == "http" and host in {"localhost", "127.0.0.1"}
    )
    if not ok_scheme or not host or parts.username or parts.password:
        raise MessageError("link must be an https URL without credentials")
    if any(c in link for c in " \r\n\t<>\"'"):
        raise MessageError("link contains unsafe characters")
    return link


def render_sms_otp(code: str, locale: str = "bn") -> str:
    if not re.fullmatch(r"[0-9]{6}", code):  # [0-9], not \d: \d also matches Bangla digits
        raise MessageError("OTP must be exactly 6 ASCII digits")
    if locale not in ("bn", "en"):
        raise MessageError("unsupported locale")
    return _env.get_template(f"sms_otp.{locale}.txt").render(code=code).strip()


def render_email(kind: str, *, allow_http_localhost: bool = False, **context: object) -> Email:
    if kind not in EMAIL_KINDS:
        raise MessageError(f"unknown email kind: {kind}")
    safe: dict[str, object] = {k: clean_text(v) for k, v in context.items() if k != "link"}
    if "link" in context:
        safe["link"] = check_link(str(context["link"]), allow_http_localhost=allow_http_localhost)
    try:
        text = _env.get_template(f"email_{kind}.txt").render(**safe)
        html = _env.get_template(f"email_{kind}.html").render(**safe)
    except Exception as exc:  # jinja2.UndefinedError and friends
        raise MessageError(f"cannot render {kind}: {type(exc).__name__}") from exc
    return Email(subject=SUBJECTS[kind], text=text.strip() + "\n", html=html)
