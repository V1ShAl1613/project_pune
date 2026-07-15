from __future__ import annotations

import time
from collections.abc import Callable

from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def check_database_health(session_factory: Callable[[], AsyncSession] | None = None) -> dict[str, object]:
    started = time.perf_counter()
    try:
        if session_factory is None:
            return {"status": "unavailable", "message": "session_factory not configured", "latency_ms": 0.0}
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
        return _build_result("healthy", "database connection available", started)
    except Exception as exc:  # pragma: no cover - defensive guard
        return _build_result("unhealthy", str(exc), started)


async def check_redis_health(redis_client: Redis | None = None) -> dict[str, object]:
    started = time.perf_counter()
    try:
        if redis_client is None:
            return {"status": "unavailable", "message": "redis client not configured", "latency_ms": 0.0}
        await redis_client.ping()
        return _build_result("healthy", "redis connection available", started)
    except Exception as exc:  # pragma: no cover - defensive guard
        return _build_result("unhealthy", str(exc), started)


def _build_result(status: str, message: str, started: float) -> dict[str, object]:
    return {
        "status": status,
        "message": message,
        "latency_ms": round((time.perf_counter() - started) * 1000.0, 2),
    }
