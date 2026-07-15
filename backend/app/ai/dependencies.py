from __future__ import annotations

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.clients.ollama_client import OllamaClient
from app.ai.repositories.ai_repository import AIRepository
from app.ai.services.ai_service import AIService
from app.core.settings import AppSettings
from app.dependencies.providers import get_logger, provide_database_session, provide_redis_client, provide_settings


def provide_ollama_client(settings: AppSettings = Depends(provide_settings)) -> OllamaClient:
    return OllamaClient(settings)


def provide_ai_repository(session: AsyncSession = Depends(provide_database_session)) -> AIRepository:
    return AIRepository(session)


def provide_ai_service(
    repository: AIRepository = Depends(provide_ai_repository),
    settings: AppSettings = Depends(provide_settings),
    ollama_client: OllamaClient = Depends(provide_ollama_client),
    redis_client: Redis = Depends(provide_redis_client),
) -> AIService:
    return AIService(repository=repository, settings=settings, ollama_client=ollama_client, redis_client=redis_client, logger=get_logger())
