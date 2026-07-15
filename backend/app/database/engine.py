from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.settings import AppSettings, get_settings


@dataclass(slots=True)
class FallbackAsyncEngine:
    url: object
    pool: object


@dataclass(slots=True)
class FallbackSessionFactory:
    engine: FallbackAsyncEngine

    def __call__(self):
        return self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, statement):
        return object()


def create_database_engine(settings: AppSettings | None = None) -> AsyncEngine:
    resolved = settings or get_settings()
    try:
        return create_async_engine(
            resolved.database_url,
            echo=resolved.debug,
            future=True,
            pool_size=resolved.database_pool_size,
            max_overflow=resolved.database_max_overflow,
            pool_timeout=resolved.database_pool_timeout,
            pool_recycle=resolved.database_pool_recycle,
            pool_pre_ping=True,
        )
    except ModuleNotFoundError:
        return FallbackAsyncEngine(url=make_url(resolved.database_url), pool=object())


def create_session_factory(settings: AppSettings | None = None) -> async_sessionmaker:
    engine = create_database_engine(settings)
    if isinstance(engine, FallbackAsyncEngine):
        return FallbackSessionFactory(engine)
    return async_sessionmaker(engine, expire_on_commit=False, autoflush=False)
