from __future__ import annotations

from dataclasses import dataclass

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import BaseRepository, EntityT
from app.services.base import BaseService


@dataclass(slots=True)
class ServiceFactory:
    session: AsyncSession
    redis_client: Redis | None = None

    def create(self, model: type[EntityT]) -> BaseService[EntityT]:
        repository = BaseRepository(self.session, model)
        return BaseService(repository=repository, session=self.session, redis_client=self.redis_client)
