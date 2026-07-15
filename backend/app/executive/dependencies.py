from __future__ import annotations

from fastapi import Depends
from redis.asyncio import Redis

from app.core.settings import AppSettings
from app.dependencies.providers import get_logger, provide_redis_client, provide_settings
from app.executive.services.executive_service import ExecutiveService


def provide_executive_service(settings: AppSettings = Depends(provide_settings), redis_client: Redis = Depends(provide_redis_client)) -> ExecutiveService:
    return ExecutiveService(settings=settings, redis_client=redis_client, logger=get_logger())
