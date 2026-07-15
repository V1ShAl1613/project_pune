from __future__ import annotations

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import AppSettings
from app.dependencies.providers import get_logger, provide_database_session, provide_redis_client, provide_settings
from app.knowledge.repositories.knowledge_repository import KnowledgeRepository
from app.knowledge.services.knowledge_service import KnowledgeService


def provide_knowledge_repository(session: AsyncSession = Depends(provide_database_session)) -> KnowledgeRepository:
    return KnowledgeRepository(session)


def provide_knowledge_service(
    repository: KnowledgeRepository = Depends(provide_knowledge_repository),
    settings: AppSettings = Depends(provide_settings),
    redis_client: Redis = Depends(provide_redis_client),
) -> KnowledgeService:
    return KnowledgeService(repository=repository, settings=settings, redis_client=redis_client, logger=get_logger())
