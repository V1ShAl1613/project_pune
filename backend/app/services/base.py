from __future__ import annotations

from dataclasses import dataclass
from typing import Generic

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository, EntityT


@dataclass(slots=True)
class BaseService(Generic[EntityT]):
    repository: BaseRepository[EntityT]
    session: AsyncSession
    redis_client: Redis | None = None

    async def health(self) -> bool:
        return True
