"""Test-only helpers. Mounted ONLY when CG_ENV=test (see `app.main`); it reads captured SMS
codes and email links that production never exposes, and can reset rate-limit counters
between tests. A startup assertion and a boot test prove it is absent everywhere else."""

from __future__ import annotations

from fastapi import APIRouter, Request

from app.api import deps
from app.core.errors import AppError

router = APIRouter(prefix="/api/v1/__test__", tags=["test-only"], include_in_schema=False)


def _mailbox(container: deps.Container):  # type: ignore[no-untyped-def]
    if container.settings.cg_env != "test" or container.notifier.mailbox is None:
        raise AppError(404, "not_found")
    return container.notifier.mailbox


@router.get("/sms/{phone}")
async def last_sms_code(phone: str, container: deps.Ctn) -> dict[str, str]:
    box = _mailbox(container)
    if phone not in box.sms:
        raise AppError(404, "not_found")
    return {"code": box.last_code(phone)}


@router.get("/email-link")
async def last_email_link(email: str, container: deps.Ctn) -> dict[str, str]:
    box = _mailbox(container)
    if email.lower() not in box.links:
        raise AppError(404, "not_found")
    return {"link": box.last_link(email)}


@router.post("/reset-limits", status_code=204)
async def reset_limits(request: Request, container: deps.Ctn, failures: bool = False) -> None:
    _mailbox(container)
    if container.redis is not None:
        async for key in container.redis.scan_iter("cg:rl:*"):
            await container.redis.delete(key)
        if failures:  # also forget login-failure counters / locks
            async for key in container.redis.scan_iter("cg:lf:*"):
                await container.redis.delete(key)
