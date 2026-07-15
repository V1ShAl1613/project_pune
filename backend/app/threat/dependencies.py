from __future__ import annotations

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import AppSettings
from app.dependencies.providers import get_logger, provide_database_session, provide_redis_client, provide_settings
from app.threat.repositories.threat_repository import ThreatRepository
from app.threat.services.threat_service import ThreatService


def provide_threat_repository(session: AsyncSession = Depends(provide_database_session)) -> ThreatRepository:
    return ThreatRepository(session=session)


def provide_threat_service(
    repository: ThreatRepository = Depends(provide_threat_repository),
    settings: AppSettings = Depends(provide_settings),
    redis_client: Redis = Depends(provide_redis_client),
) -> ThreatService:
    return ThreatService(repository=repository, settings=settings, redis_client=redis_client, logger=get_logger())
