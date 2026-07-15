from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.authorization import AuthorizationPolicy


@dataclass(slots=True)
class PolicyRepository:
    session: AsyncSession

    async def list_policies(self) -> list[AuthorizationPolicy]:
        result = await self.session.execute(select(AuthorizationPolicy).order_by(AuthorizationPolicy.priority.asc(), AuthorizationPolicy.code.asc()))
        return list(result.scalars().all())

    async def active_policies(self) -> list[AuthorizationPolicy]:
        result = await self.session.execute(
            select(AuthorizationPolicy)
            .where(AuthorizationPolicy.enabled.is_(True), AuthorizationPolicy.deleted_at.is_(None))
            .order_by(AuthorizationPolicy.priority.asc(), AuthorizationPolicy.code.asc())
        )
        return list(result.scalars().all())

    async def get_by_id(self, policy_id: UUID) -> AuthorizationPolicy | None:
        return await self.session.get(AuthorizationPolicy, policy_id)

    async def get_by_code(self, code: str) -> AuthorizationPolicy | None:
        result = await self.session.execute(select(AuthorizationPolicy).where(AuthorizationPolicy.code == code))
        return result.scalar_one_or_none()

    async def create(self, policy: AuthorizationPolicy) -> AuthorizationPolicy:
        self.session.add(policy)
        await self.session.flush()
        return policy

    async def update(self, policy: AuthorizationPolicy, values: dict[str, object]) -> AuthorizationPolicy:
        for key, value in values.items():
            if hasattr(policy, key):
                setattr(policy, key, value)
        await self.session.flush()
        return policy

    async def delete(self, policy: AuthorizationPolicy) -> None:
        await self.session.delete(policy)

