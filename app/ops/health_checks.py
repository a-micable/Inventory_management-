"""Extended health check utilities."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ComponentHealth:
    name: str
    status: str
    latency_ms: float | None = None
    message: str | None = None
    checked_at: datetime | None = None


async def check_database(session) -> ComponentHealth:
    import time
    from sqlalchemy import text
    start = time.perf_counter()
    try:
        await session.execute(text("SELECT 1"))
        latency = (time.perf_counter() - start) * 1000
        return ComponentHealth(name="database", status="healthy", latency_ms=latency)
    except Exception as exc:
        return ComponentHealth(name="database", status="unhealthy", message=str(exc))


async def check_redis() -> ComponentHealth:
    import time
    from app.core.cache import get_redis
    start = time.perf_counter()
    try:
        redis = await get_redis()
        await redis.ping()
        latency = (time.perf_counter() - start) * 1000
        return ComponentHealth(name="redis", status="healthy", latency_ms=latency)
    except Exception as exc:
        return ComponentHealth(name="redis", status="unhealthy", message=str(exc))


async def check_celery() -> ComponentHealth:
    try:
        from app.workers.celery_app import celery_app
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        if stats:
            return ComponentHealth(name="celery", status="healthy", message=f"{len(stats)} workers")
        return ComponentHealth(name="celery", status="degraded", message="No workers responding")
    except Exception as exc:
        return ComponentHealth(name="celery", status="unhealthy", message=str(exc))
