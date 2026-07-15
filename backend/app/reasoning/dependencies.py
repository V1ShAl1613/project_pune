from __future__ import annotations

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import AppSettings
from app.dependencies.providers import get_logger, provide_database_session, provide_redis_client, provide_settings
from app.reasoning.repositories.reasoning_repository import ReasoningRepository
from app.reasoning.services.reasoning_service import ReasoningService


def provide_reasoning_repository(session: AsyncSession = Depends(provide_database_session)) -> ReasoningRepository:
    return ReasoningRepository(session=session)


def provide_reasoning_service(
    repository: ReasoningRepository = Depends(provide_reasoning_repository),
    settings: AppSettings = Depends(provide_settings),
    redis_client: Redis = Depends(provide_redis_client),
) -> ReasoningService:
    return ReasoningService(repository=repository, settings=settings, redis_client=redis_client, logger=get_logger())
