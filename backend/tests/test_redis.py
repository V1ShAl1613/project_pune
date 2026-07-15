from __future__ import annotations

import pytest

from app.core.settings import TestingSettings
from app.database.health import check_redis_health
from app.database.redis import get_redis_manager


def test_redis_manager_builds_client_from_settings() -> None:
    manager = get_redis_manager(TestingSettings())
    client = manager.get_client()
    assert client is not None


@pytest.mark.asyncio
async def test_redis_health_with_fake_client() -> None:
    class FakeRedis:
        async def ping(self):
            return True

    result = await check_redis_health(FakeRedis())
    assert result["status"] == "healthy"
