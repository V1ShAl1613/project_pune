from __future__ import annotations

import pytest

from app.core.settings import TestingSettings
from app.database.engine import create_database_engine
from app.database.health import check_database_health


def test_database_engine_uses_postgresql_configuration() -> None:
    engine = create_database_engine(TestingSettings())
    assert "postgresql" in str(engine.url)
    assert engine.pool is not None


@pytest.mark.asyncio
async def test_database_health_with_fake_session() -> None:
    class FakeSession:
        async def execute(self, statement):
            return object()

    class FakeFactory:
        def __call__(self):
            return self

        async def __aenter__(self):
            return FakeSession()

        async def __aexit__(self, exc_type, exc, tb):
            return False

    result = await check_database_health(FakeFactory())
    assert result["status"] == "healthy"
