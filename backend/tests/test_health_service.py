from __future__ import annotations

import pytest

from app.database.services.health_service import HealthService


class FakeDatabaseManager:
    async def startup_checks(self) -> dict[str, dict[str, object]]:
        return {
            "database": {"status": "healthy", "message": "ok", "latency_ms": 1.0},
            "redis": {"status": "healthy", "message": "ok", "latency_ms": 1.0},
        }


@pytest.mark.asyncio
async def test_health_service_returns_healthy_checks() -> None:
    service = HealthService(database_manager=FakeDatabaseManager())
    result = await service.validate_with_retry()
    assert result["database"]["status"] == "healthy"
    assert result["redis"]["status"] == "healthy"
