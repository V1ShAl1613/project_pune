from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.base import CRUDRepository, EntityT


@dataclass(slots=True)
class RepositoryFactory:
    """Factory for typed repository instances."""

    session: AsyncSession

    def create(self, model: type[EntityT]) -> CRUDRepository[EntityT]:
        return CRUDRepository(self.session, model)
