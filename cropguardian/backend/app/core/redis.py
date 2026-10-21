"""Redis client factory. Redis holds sessions, rate-limit windows and single-use markers; it is a
cache in front of Postgres for sessions, never the only record of anything that must survive a
restart."""

from __future__ import annotations

from redis.asyncio import Redis

from app.core.config import Settings


def make_redis(settings: Settings) -> Redis | None:
    if not settings.redis_url:
        return None
    client: Redis = Redis.from_url(
        settings.redis_url,
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
        health_check_interval=30,
    )
    return client
