from __future__ import annotations

import logging

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import AppSettings
from app.dependencies.providers import provide_database_session, provide_redis_client, provide_settings
from app.identity.repositories import IdentityRepository
from app.identity.services import IdentityService


def provide_identity_service(
    session: AsyncSession = Depends(provide_database_session),
    redis_client: Redis = Depends(provide_redis_client),
    settings: AppSettings = Depends(provide_settings),
) -> IdentityService:
    return IdentityService(
        repository=IdentityRepository(session),
        redis_client=redis_client,
        settings=settings,
        logger=logging.getLogger("sentinel.identity"),
        audit_logger=logging.getLogger("sentinel.audit"),
    )

