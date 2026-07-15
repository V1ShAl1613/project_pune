from __future__ import annotations

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.clients.ollama_client import OllamaClient
from app.core.settings import AppSettings
from app.dependencies.providers import get_logger, provide_database_session, provide_redis_client, provide_settings
from app.prompt.repositories.prompt_repository import PromptRepository
from app.prompt.services.prompt_service import PromptService


def provide_prompt_repository(session: AsyncSession = Depends(provide_database_session)) -> PromptRepository:
    return PromptRepository(session)


def provide_prompt_service(
    repository: PromptRepository = Depends(provide_prompt_repository),
    settings: AppSettings = Depends(provide_settings),
    redis_client: Redis = Depends(provide_redis_client),
) -> PromptService:
    return PromptService(
        repository=repository,
        settings=settings,
        ollama_client=OllamaClient(settings),
        redis_client=redis_client,
        logger=get_logger(),
    )
