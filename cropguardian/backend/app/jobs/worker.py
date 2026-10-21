"""arq worker settings, the `ping` job, the JOBS_MODE switch and a cron lock helper (spec 5.2, 13).

JOBS_MODE=inprocess (free hosting): the arq worker runs inside the API lifespan as an asyncio task.
JOBS_MODE=worker: a separate container runs `arq app.jobs.worker.WorkerSettings`.
JOBS_MODE=off: no jobs (tests, local without Redis).
"""

from __future__ import annotations

import asyncio
import os
from typing import Any

from arq.connections import RedisSettings
from arq.worker import Worker

from app.core.config import Settings
from app.core.logging import get_logger

_log = get_logger("cg.jobs")
CRON_LOCK_PREFIX = "cg:cronlock:"


async def ping(_ctx: dict[str, Any]) -> str:
    """Smoke job proving enqueue -> execute works end to end."""
    return "pong"


async def acquire_cron_lock(redis: Any, name: str, ttl_seconds: int) -> bool:
    """SET NX EX lock so a future second instance cannot double-run a cron job."""
    if ttl_seconds < 1:
        raise ValueError("ttl_seconds must be >= 1")
    return bool(await redis.set(f"{CRON_LOCK_PREFIX}{name}", "1", nx=True, ex=ttl_seconds))


def redis_settings_from_url(url: str) -> RedisSettings:
    return RedisSettings.from_dsn(url)


class WorkerSettings:
    """Used by the separate worker container: `arq app.jobs.worker.WorkerSettings`."""

    functions = [ping]  # noqa: RUF012 (arq reads this class attribute)
    max_jobs = 5
    job_timeout = 60
    redis_settings = RedisSettings.from_dsn(os.environ.get("REDIS_URL") or "redis://localhost:6379")


async def start_inprocess_worker(settings: Settings) -> asyncio.Task[None] | None:
    if settings.jobs_mode != "inprocess" or not settings.redis_url:
        return None
    worker = Worker(
        functions=[ping],
        redis_settings=redis_settings_from_url(settings.redis_url),
        max_jobs=WorkerSettings.max_jobs,
        handle_signals=False,  # the API process owns signals
    )
    task = asyncio.create_task(worker.async_run(), name="arq-inprocess")
    _log.info("inprocess_worker_started")
    return task


async def stop_inprocess_worker(task: asyncio.Task[None] | None) -> None:
    if task is None:
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    except Exception as exc:  # shutdown must never raise
        _log.warning("inprocess_worker_stop_error", error_type=type(exc).__name__)
