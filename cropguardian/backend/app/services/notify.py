"""Outgoing SMS / email (spec 14, 16.4). Providers: `console` (development: prints to stdout,
which is the point of the provider), `disabled` (public demo: nothing leaves the system).
Production refuses `console` (see Settings). In CG_ENV=test a Mailbox also captures messages for
the test-only router.

Emails are recorded in `email_outbox` first (SYSTEM only, never readable by users or admins) so a
message is never sent twice (`dedupe_key`) and a failure is visible.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass, field

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.config import Settings
from app.core.logging import get_logger
from app.core.messages import render_email, render_sms_otp
from app.db.session import system_scope
from app.domain.phone import mask_phone

_log = get_logger("cg.notify")


@dataclass
class Mailbox:
    """Test-only capture of what would have been sent. Never created outside CG_ENV=test."""

    sms: dict[str, list[str]] = field(default_factory=dict)
    links: dict[str, list[str]] = field(default_factory=dict)

    def last_code(self, phone: str) -> str:
        return self.sms[phone][-1]

    def last_link(self, email: str) -> str:
        return self.links[email.lower()][-1]


class Notifier:
    def __init__(self, settings: Settings, engine: AsyncEngine) -> None:
        self._settings = settings
        self._engine = engine
        self.mailbox: Mailbox | None = Mailbox() if settings.cg_env == "test" else None

    async def send_sms_otp(self, phone: str, code: str, locale: str = "bn") -> None:
        body = render_sms_otp(code, locale)
        if self.mailbox is not None:
            self.mailbox.sms.setdefault(phone, []).append(code)
        if self._settings.sms_provider == "console":
            sys.stdout.write(f"[sms:console] to={mask_phone(phone)} :: {body}\n")
            sys.stdout.flush()
        _log.info("sms_otp_dispatched", provider=self._settings.sms_provider)

    async def send_email(
        self,
        *,
        user_id: str | None,
        tenant_id: str,
        to_email: str,
        kind: str,
        dedupe_key: str | None = None,
        **context: object,
    ) -> None:
        mail = render_email(kind, allow_http_localhost=not self._settings.is_production, **context)
        provider = self._settings.email_provider
        status = "suppressed" if provider == "disabled" else "sent"
        async with system_scope(self._engine) as db:
            result = await db.execute(
                text(
                    "INSERT INTO email_outbox (tenant_id, user_id, to_email, kind, subject, "
                    "body_text, body_html, dedupe_key, status, sent_at) VALUES (:t, "
                    "CAST(:uid AS uuid), :to, :kind, :subject, :bt, :bh, :dk, :st, "
                    "CASE WHEN :st = 'sent' THEN now() END) ON CONFLICT (dedupe_key) DO NOTHING "
                    "RETURNING id"
                ),
                {
                    "t": tenant_id, "uid": user_id, "to": to_email, "kind": kind,
                    "subject": mail.subject, "bt": mail.text, "bh": mail.html, "dk": dedupe_key,
                    "st": status,
                },
            )  # fmt: skip
            fresh = result.first() is not None
        if not fresh:
            return  # already queued/sent: never send twice
        if self.mailbox is not None and "link" in context:
            self.mailbox.links.setdefault(to_email.lower(), []).append(str(context["link"]))
        if provider == "console":
            sys.stdout.write(f"[email:console] to={to_email} :: {mail.subject}\n{mail.text}\n")
            sys.stdout.flush()
        _log.info("email_dispatched", provider=provider, kind=kind)
