from __future__ import annotations

from dataclasses import dataclass, field

from app.core.settings import AppSettings, get_settings
from app.database.services.database_manager import DatabaseManager


@dataclass(slots=True)
class HealthService:
    """Aggregates startup and runtime health checks with retry support."""

    database_manager: DatabaseManager = field(default_factory=DatabaseManager)
    max_retries: int = 3
    retry_delay_seconds: float = 0.5

    async def run_checks(self) -> dict[str, dict[str, object]]:
        return await self.database_manager.startup_checks()

    async def validate_with_retry(self) -> dict[str, dict[str, object]]:
        last_result: dict[str, dict[str, object]] = {}
        for attempt in range(self.max_retries):
            last_result = await self.run_checks()
            if last_result["database"]["status"] == "healthy" and last_result["redis"]["status"] == "healthy":
                return last_result
            if attempt < self.max_retries - 1:
                await self._sleep(self.retry_delay_seconds)
        return last_result

    async def _sleep(self, delay_seconds: float) -> None:
        import asyncio

        await asyncio.sleep(delay_seconds)
