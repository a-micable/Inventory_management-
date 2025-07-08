"""Redis cache client and helpers."""

from __future__ import annotations

import json
import logging
from typing import Any

import redis.asyncio as aioredis

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_redis: aioredis.Redis | None = None


async def init_redis() -> None:
    global _redis
    _redis = aioredis.from_url(settings.redis_url, decode_responses=True)
    await _redis.ping()
    logger.info("Redis connection established")


async def close_redis() -> None:
    global _redis
    if _redis:
        await _redis.aclose()
        _redis = None


async def get_redis() -> aioredis.Redis:
    if _redis is None:
        await init_redis()
    assert _redis is not None
    return _redis


async def cache_get(key: str) -> Any | None:
    redis = await get_redis()
    raw = await redis.get(key)
    if raw is None:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


async def cache_set(key: str, value: Any, ttl: int | None = None) -> None:
    redis = await get_redis()
    serialized = json.dumps(value, default=str)
    await redis.set(key, serialized, ex=ttl or settings.cache_ttl_seconds)


async def cache_delete(key: str) -> None:
    redis = await get_redis()
    await redis.delete(key)


async def cache_delete_pattern(pattern: str) -> int:
    redis = await get_redis()
    deleted = 0
    async for key in redis.scan_iter(match=pattern):
        await redis.delete(key)
        deleted += 1
    return deleted
