from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.core.settings import AppSettings, get_settings
from app.database.connection import create_database_engine, create_session_factory
from app.database.health import check_database_health, check_redis_health
from app.database.redis import RedisManager, get_redis_manager


@dataclass(slots=True)
class DatabaseManager:
    """Coordinates engine, sessions, Redis, and startup validation."""

    settings: AppSettings = field(default_factory=get_settings)
    _engine: AsyncEngine | object | None = None
    _session_factory: async_sessionmaker[AsyncSession] | object | None = None
    _redis_manager: RedisManager | None = None

    def get_engine(self) -> AsyncEngine | object:
        if self._engine is None:
            self._engine = create_database_engine(self.settings)
        return self._engine

    def get_session_factory(self) -> async_sessionmaker[AsyncSession] | object:
        if self._session_factory is None:
            self._session_factory = create_session_factory(self.settings)
        return self._session_factory

    def get_redis_manager(self) -> RedisManager:
        if self._redis_manager is None:
            self._redis_manager = get_redis_manager(self.settings)
        return self._redis_manager

    async def validate_connection(self) -> dict[str, object]:
        return await check_database_health(self.get_session_factory())

    async def validate_redis_connection(self) -> dict[str, object]:
        return await check_redis_health(self.get_redis_manager().get_client())

    async def startup_checks(self) -> dict[str, dict[str, object]]:
        return {
            "database": await self.validate_connection(),
            "redis": await self.validate_redis_connection(),
        }

    async def close(self) -> None:
        engine = self.get_engine()
        if hasattr(engine, "dispose"):
            await engine.dispose()  # type: ignore[func-returns-value]
        await self.get_redis_manager().close()
