from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.identity import Role, UserRole
from app.database.models.authorization import RoleHierarchy


@dataclass(slots=True)
class RoleRepository:
    session: AsyncSession

    async def list_roles(self) -> list[Role]:
        result = await self.session.execute(select(Role).order_by(Role.name.asc()))
        return list(result.scalars().all())

    async def get_by_id(self, role_id: UUID) -> Role | None:
        return await self.session.get(Role, role_id)

    async def get_by_code(self, code: str) -> Role | None:
        result = await self.session.execute(select(Role).where(Role.code == code))
        return result.scalar_one_or_none()

    async def create(self, role: Role) -> Role:
        self.session.add(role)
        await self.session.flush()
        return role

    async def update(self, role: Role, values: dict[str, object]) -> Role:
        for key, value in values.items():
            if hasattr(role, key):
                setattr(role, key, value)
        await self.session.flush()
        return role

    async def delete(self, role: Role) -> None:
        await self.session.delete(role)

    async def assign_user_role(self, user_id: UUID, role_id: UUID) -> UserRole:
        assignment = UserRole(user_id=user_id, role_id=role_id)
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def revoke_user_role(self, user_id: UUID, role_id: UUID) -> int:
        result = await self.session.execute(delete(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role_id))
        await self.session.flush()
        return int(result.rowcount or 0)

    async def list_user_roles(self, user_id: UUID) -> list[Role]:
        statement = select(Role).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id)
        result = await self.session.execute(statement)
        return list(result.scalars().unique().all())

    async def add_hierarchy(self, parent_role_id: UUID, child_role_id: UUID, depth: int = 1) -> RoleHierarchy:
        hierarchy = RoleHierarchy(parent_role_id=parent_role_id, child_role_id=child_role_id, depth=depth)
        self.session.add(hierarchy)
        await self.session.flush()
        return hierarchy

    async def remove_hierarchy(self, parent_role_id: UUID, child_role_id: UUID) -> int:
        result = await self.session.execute(
            delete(RoleHierarchy).where(
                RoleHierarchy.parent_role_id == parent_role_id,
                RoleHierarchy.child_role_id == child_role_id,
            )
        )
        await self.session.flush()
        return int(result.rowcount or 0)

    async def parent_role_ids(self, child_role_id: UUID) -> list[UUID]:
        result = await self.session.execute(select(RoleHierarchy.parent_role_id).where(RoleHierarchy.child_role_id == child_role_id, RoleHierarchy.active.is_(True)))
        return [row[0] for row in result.all()]

    async def child_role_ids(self, parent_role_id: UUID) -> list[UUID]:
        result = await self.session.execute(select(RoleHierarchy.child_role_id).where(RoleHierarchy.parent_role_id == parent_role_id, RoleHierarchy.active.is_(True)))
        return [row[0] for row in result.all()]

