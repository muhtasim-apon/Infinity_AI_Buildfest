"""Wires the identity services once per application (created in the lifespan)."""

from __future__ import annotations

from dataclasses import dataclass

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

from app.core.captcha import Captcha
from app.core.config import Settings
from app.core.platform_settings import defaults
from app.core.ratelimit import RateLimiter
from app.core.redis import make_redis
from app.core.sessions import SessionStore
from app.services.auth import AuthService
from app.services.llm import LlamaService
from app.services.notify import Notifier
from app.services.scans import ScanService
from app.services.users import UsersService


@dataclass
class Container:
    settings: Settings
    engine: AsyncEngine
    redis: Redis | None
    sessions: SessionStore
    limiter: RateLimiter
    captcha: Captcha
    notifier: Notifier
    auth: AuthService
    users: UsersService
    llm: LlamaService | None = None
    scans: ScanService | None = None

    async def close(self) -> None:
        if self.llm is not None:
            await self.llm.aclose()
        if self.redis is not None:
            await self.redis.aclose()


def build_container(settings: Settings, engine: AsyncEngine) -> Container:
    redis = make_redis(settings)
    demo_minutes = int(defaults()["demo.session_minutes"])
    sessions = SessionStore(engine, redis, demo_minutes=demo_minutes)
    limiter = RateLimiter(redis)
    # CAPTCHA bypass is for the automated test environment only; Settings refuses it elsewhere.
    captcha = Captcha(
        settings.secret_key,
        redis,
        bypass=settings.captcha_bypass and settings.cg_env == "test",
    )
    notifier = Notifier(settings, engine)
    auth = AuthService(
        settings=settings, engine=engine, redis=redis, sessions=sessions, limiter=limiter,
        captcha=captcha, notifier=notifier,
    )  # fmt: skip
    llm = LlamaService(settings, redis)
    scans = ScanService(engine, llm, settings.max_upload_mb)
    return Container(
        settings, engine, redis, sessions, limiter, captcha, notifier, auth, UsersService(engine),
        llm, scans,
    )  # fmt: skip
