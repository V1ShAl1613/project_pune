from __future__ import annotations

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.banking.repositories.banking_repository import BankingRepository
from app.banking.services.banking_service import BankingService
from app.core.settings import AppSettings
from app.dependencies.providers import get_logger, provide_database_session, provide_redis_client, provide_settings


def provide_banking_repository(session: AsyncSession = Depends(provide_database_session)) -> BankingRepository:
    return BankingRepository(session=session)


def provide_banking_service(
    repository: BankingRepository = Depends(provide_banking_repository),
    settings: AppSettings = Depends(provide_settings),
    redis_client: Redis = Depends(provide_redis_client),
) -> BankingService:
    return BankingService(repository=repository, settings=settings, redis_client=redis_client, logger=get_logger())
