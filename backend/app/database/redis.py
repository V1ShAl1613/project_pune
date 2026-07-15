from __future__ import annotations

from dataclasses import dataclass

from redis.asyncio import ConnectionPool, Redis

from app.core.settings import AppSettings, get_settings


@dataclass(slots=True)
class RedisManager:
    settings: AppSettings
    _pool: ConnectionPool | None = None
    _client: Redis | None = None

    def get_client(self) -> Redis:
        if self._client is None:
            self._pool = ConnectionPool.from_url(
                self.settings.redis_url,
                max_connections=self.settings.redis_max_connections,
                socket_timeout=self.settings.redis_socket_timeout,
                decode_responses=True,
            )
            self._client = Redis(connection_pool=self._pool)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
        if self._pool is not None:
            await self._pool.disconnect()


def get_redis_manager(settings: AppSettings | None = None) -> RedisManager:
    return RedisManager(settings or get_settings())
