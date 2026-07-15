from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.authorization.models import AuthorizationContext
from app.authorization.repositories.cache_repository import AuthorizationCacheRepository
from app.authorization.repositories.permission_repository import PermissionRepository
from app.authorization.repositories.role_repository import RoleRepository
from app.database.models.identity import User
from app.exceptions.base import AuthorizationApplicationException


@dataclass(slots=True)
class PermissionEngine:
    role_repository: RoleRepository
    permission_repository: PermissionRepository
    cache_repository: AuthorizationCacheRepository
    cache_ttl_seconds: int

    async def build_context(self, user: User) -> AuthorizationContext:
        roles = await self._resolve_roles(user.id)
        permissions = await self._resolve_permissions(roles)
        context = AuthorizationContext(
            user_id=user.id,
            session_id=user.sessions[0].id if getattr(user, "sessions", None) else user.id,
            role_codes={role.code for role in roles},
            permission_codes={permission.code for permission in permissions},
            is_super_admin="Super Admin" in {role.name for role in roles},
        )
        await self.cache_repository.cache_context(context, self.cache_ttl_seconds)
        await self.cache_repository.cache_roles(user.id, [role.code for role in roles], self.cache_ttl_seconds)
        await self.cache_repository.cache_permissions(user.id, [permission.code for permission in permissions], self.cache_ttl_seconds)
        return context

    async def has_permission(self, user: User, permission_code: str) -> bool:
        context = await self.build_context(user)
        return permission_code in context.permission_codes or context.is_super_admin

    async def _resolve_roles(self, user_id: UUID) -> list[User]:
        direct_roles = await self.role_repository.list_user_roles(user_id)
        resolved: list = []
        visited: set[UUID] = set()

        async def visit(role) -> None:
            if role.id in visited:
                return
            visited.add(role.id)
            resolved.append(role)
            for parent_id in await self.role_repository.parent_role_ids(role.id):
                parent_role = await self.role_repository.get_by_id(parent_id)
                if parent_role is None:
                    continue
                await visit(parent_role)

        for role in direct_roles:
            await visit(role)
        return resolved

    async def _resolve_permissions(self, roles) -> list:
        permissions: dict[UUID, object] = {}
        for role in roles:
            for permission in await self.permission_repository.permissions_for_role(role.id):
                permissions[permission.id] = permission
        return list(permissions.values())

