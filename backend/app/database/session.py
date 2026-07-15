from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.settings import AppSettings, get_settings
from app.database.engine import create_session_factory


def get_session_factory(settings: AppSettings | None = None) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(settings or get_settings())


async def get_database_session() -> AsyncIterator[AsyncSession]:
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
