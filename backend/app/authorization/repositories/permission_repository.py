from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models.authorization import PermissionGroup, PermissionGroupPermission
from app.database.models.identity import Permission, RolePermission


@dataclass(slots=True)
class PermissionRepository:
    session: AsyncSession

    async def list_permissions(self) -> list[Permission]:
        result = await self.session.execute(select(Permission).order_by(Permission.resource.asc(), Permission.action.asc()))
        return list(result.scalars().all())

    async def get_by_id(self, permission_id: UUID) -> Permission | None:
        return await self.session.get(Permission, permission_id)

    async def get_by_code(self, code: str) -> Permission | None:
        result = await self.session.execute(select(Permission).where(Permission.code == code))
        return result.scalar_one_or_none()

    async def create(self, permission: Permission) -> Permission:
        self.session.add(permission)
        await self.session.flush()
        return permission

    async def update(self, permission: Permission, values: dict[str, object]) -> Permission:
        for key, value in values.items():
            if hasattr(permission, key):
                setattr(permission, key, value)
        await self.session.flush()
        return permission

    async def delete(self, permission: Permission) -> None:
        await self.session.delete(permission)

    async def assign_permission_to_role(self, role_id: UUID, permission_id: UUID) -> RolePermission:
        assignment = RolePermission(role_id=role_id, permission_id=permission_id)
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def revoke_permission_from_role(self, role_id: UUID, permission_id: UUID) -> int:
        result = await self.session.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id, RolePermission.permission_id == permission_id)
        )
        await self.session.flush()
        return int(result.rowcount or 0)

    async def permissions_for_role(self, role_id: UUID) -> list[Permission]:
        statement = select(Permission).join(RolePermission, RolePermission.permission_id == Permission.id).where(RolePermission.role_id == role_id)
        result = await self.session.execute(statement)
        return list(result.scalars().unique().all())

    async def list_groups(self) -> list[PermissionGroup]:
        result = await self.session.execute(select(PermissionGroup).order_by(PermissionGroup.name.asc()))
        return list(result.scalars().all())

    async def get_group_by_code(self, code: str) -> PermissionGroup | None:
        result = await self.session.execute(select(PermissionGroup).where(PermissionGroup.code == code))
        return result.scalar_one_or_none()

    async def create_group(self, group: PermissionGroup) -> PermissionGroup:
        self.session.add(group)
        await self.session.flush()
        return group

    async def update_group(self, group: PermissionGroup, values: dict[str, object]) -> PermissionGroup:
        for key, value in values.items():
            if hasattr(group, key):
                setattr(group, key, value)
        await self.session.flush()
        return group

    async def delete_group(self, group: PermissionGroup) -> None:
        await self.session.delete(group)

    async def assign_permission_to_group(self, group_id: UUID, permission_id: UUID) -> PermissionGroupPermission:
        assignment = PermissionGroupPermission(group_id=group_id, permission_id=permission_id)
        self.session.add(assignment)
        await self.session.flush()
        return assignment

    async def revoke_permission_from_group(self, group_id: UUID, permission_id: UUID) -> int:
        result = await self.session.execute(
            delete(PermissionGroupPermission).where(
                PermissionGroupPermission.group_id == group_id,
                PermissionGroupPermission.permission_id == permission_id,
            )
        )
        await self.session.flush()
        return int(result.rowcount or 0)

    async def group_permissions(self, group_id: UUID) -> list[Permission]:
        statement = select(Permission).join(PermissionGroupPermission, PermissionGroupPermission.permission_id == Permission.id).where(PermissionGroupPermission.group_id == group_id)
        result = await self.session.execute(statement)
        return list(result.scalars().unique().all())

