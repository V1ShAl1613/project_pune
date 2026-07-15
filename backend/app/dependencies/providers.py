from __future__ import annotations

import logging
from collections.abc import AsyncIterator

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession

from app.core.settings import AppSettings, get_settings
from app.database.engine import create_database_engine
from app.database.redis import RedisManager, get_redis_manager
from app.database.session import get_database_session, get_session_factory
from app.repositories.factory import RepositoryFactory
from app.services.factory import ServiceFactory


def provide_settings() -> AppSettings:
    return get_settings()


def get_settings_dependency() -> AppSettings:
    return provide_settings()


def get_logger() -> logging.Logger:
    return logging.getLogger("sentinel.app")


def get_audit_logger() -> logging.Logger:
    return logging.getLogger("sentinel.audit")


def provide_database_engine(settings: AppSettings = Depends(provide_settings)) -> AsyncEngine:
    return create_database_engine(settings)


def provide_session_factory(settings: AppSettings = Depends(provide_settings)):
    return get_session_factory(settings)


async def provide_database_session() -> AsyncIterator[AsyncSession]:
    async for session in get_database_session():
        yield session


def provide_redis_manager(settings: AppSettings = Depends(provide_settings)) -> RedisManager:
    return get_redis_manager(settings)


async def provide_redis_client(manager: RedisManager = Depends(provide_redis_manager)) -> AsyncIterator[Redis]:
    client = manager.get_client()
    yield client


def provide_repository_factory(session: AsyncSession = Depends(provide_database_session)) -> RepositoryFactory:
    return RepositoryFactory(session)


def provide_service_factory(
    session: AsyncSession = Depends(provide_database_session),
    redis_client: Redis = Depends(provide_redis_client),
) -> ServiceFactory:
    return ServiceFactory(session=session, redis_client=redis_client)
