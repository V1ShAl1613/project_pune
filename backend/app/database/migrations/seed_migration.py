from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.services.seed_service import SeedService


async def seed_reference_data(session: AsyncSession) -> dict[str, int]:
    """Apply deterministic seed data after schema migration."""

    service = SeedService()
    return await service.seed(session)
