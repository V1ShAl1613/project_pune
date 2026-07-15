from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from app.auth.models import AuthContext
from app.authorization.models import AuthorizationContext, AuthorizationDecision
from app.authorization.permissions.catalog import DEFAULT_PERMISSION_CODES, DEFAULT_PERMISSION_GROUPS, DEFAULT_ROLE_DEFINITIONS, DEFAULT_ROLE_HIERARCHY
from app.authorization.policies.engine import PolicyEngine
from app.authorization.repositories.cache_repository import AuthorizationCacheRepository
from app.authorization.repositories.permission_repository import PermissionRepository
from app.authorization.repositories.policy_repository import PolicyRepository
from app.authorization.repositories.role_repository import RoleRepository
from app.authorization.schemas.authorization import (
    PermissionAssignmentRequest,
    PermissionCreateRequest,
    PermissionGroupAssignmentRequest,
    PermissionGroupCreateRequest,
    PermissionGroupUpdateRequest,
    PermissionUpdateRequest,
    PolicyCreateRequest,
    PolicyUpdateRequest,
    RoleAssignmentRequest,
    RoleCreateRequest,
    RoleHierarchyRequest,
    RoleUpdateRequest,
)
from app.database.models.authorization import AuthorizationPolicy, PermissionGroup
from app.database.models.identity import Permission, RefreshToken, Role, User, UserRole
from app.database.models.operational import AuditLog
from app.core.settings import AppSettings
from app.exceptions.base import AuthorizationApplicationException, BaseApplicationException


@dataclass(slots=True)
class AuthorizationService:
    role_repository: RoleRepository
    permission_repository: PermissionRepository
    policy_repository: PolicyRepository
    cache_repository: AuthorizationCacheRepository
    settings: AppSettings
    logger: logging.Logger
    audit_logger: logging.Logger

    async def list_roles(self) -> list[Role]:
        return await self.role_repository.list_roles()

    async def create_role(self, request: RoleCreateRequest, actor: AuthContext | None = None) -> Role:
        if await self.role_repository.get_by_code(request.code) is not None:
            raise BaseApplicationException("Role already exists", status_code=409, error_code="role_conflict")
        role = Role(code=request.code, name=request.name, description=request.description, status=request.status)
        created = await self.role_repository.create(role)
        await self._audit("role_create", "Role", str(created.id), actor, after=self._snapshot_role(created))
        await self._invalidate_all_caches()
        return created

    async def update_role(self, role_id: UUID, request: RoleUpdateRequest, actor: AuthContext | None = None) -> Role:
        role = await self._get_role_or_raise(role_id)
        before = self._snapshot_role(role)
        updated = await self.role_repository.update(role, request.model_dump(exclude_none=True))
        await self._audit("role_update", "Role", str(updated.id), actor, before=before, after=self._snapshot_role(updated))
        await self._invalidate_all_caches()
        return updated

    async def delete_role(self, role_id: UUID, actor: AuthContext | None = None) -> None:
        role = await self._get_role_or_raise(role_id)
        await self._audit("role_delete", "Role", str(role.id), actor, before=self._snapshot_role(role))
        await self.role_repository.delete(role)
        await self._invalidate_all_caches()

    async def list_permissions(self) -> list[Permission]:
        return await self.permission_repository.list_permissions()

    async def create_permission(self, request: PermissionCreateRequest, actor: AuthContext | None = None) -> Permission:
        if await self.permission_repository.get_by_code(request.code) is not None:
            raise BaseApplicationException("Permission already exists", status_code=409, error_code="permission_conflict")
        if await self._permission_conflict_exists(request.resource, request.action):
            raise BaseApplicationException("Permission resource/action conflict", status_code=409, error_code="permission_conflict")
        permission = Permission(
            code=request.code,
            resource=request.resource,
            action=request.action,
            description=request.description,
            category=request.category,
        )
        created = await self.permission_repository.create(permission)
        await self._audit("permission_create", "Permission", str(created.id), actor, after=self._snapshot_permission(created))
        await self._invalidate_all_caches()
        return created

    async def update_permission(self, permission_id: UUID, request: PermissionUpdateRequest, actor: AuthContext | None = None) -> Permission:
        permission = await self._get_permission_or_raise(permission_id)
        before = self._snapshot_permission(permission)
        updates = request.model_dump(exclude_none=True)
        if updates.get("resource") or updates.get("action"):
            resource = updates.get("resource", permission.resource)
            action = updates.get("action", permission.action)
            if await self._permission_conflict_exists(str(resource), str(action), exclude_id=permission.id):
                raise BaseApplicationException("Permission resource/action conflict", status_code=409, error_code="permission_conflict")
        updated = await self.permission_repository.update(permission, updates)
        await self._audit("permission_update", "Permission", str(updated.id), actor, before=before, after=self._snapshot_permission(updated))
        await self._invalidate_all_caches()
        return updated

    async def delete_permission(self, permission_id: UUID, actor: AuthContext | None = None) -> None:
        permission = await self._get_permission_or_raise(permission_id)
        await self._audit("permission_delete", "Permission", str(permission.id), actor, before=self._snapshot_permission(permission))
        await self.permission_repository.delete(permission)
        await self._invalidate_all_caches()

    async def list_permission_groups(self) -> list[PermissionGroup]:
        return await self.permission_repository.list_groups()

    async def create_permission_group(self, request: PermissionGroupCreateRequest, actor: AuthContext | None = None) -> PermissionGroup:
        if await self.permission_repository.get_group_by_code(request.code) is not None:
            raise BaseApplicationException("Permission group already exists", status_code=409, error_code="permission_group_conflict")
        group = PermissionGroup(code=request.code, name=request.name, description=request.description, status=request.status)
        created = await self.permission_repository.create_group(group)
        await self._audit("permission_group_create", "PermissionGroup", str(created.id), actor, after=self._snapshot_group(created))
        return created

    async def update_permission_group(self, group_id: UUID, request: PermissionGroupUpdateRequest, actor: AuthContext | None = None) -> PermissionGroup:
        group = await self._get_group_or_raise(group_id)
        before = self._snapshot_group(group)
        updated = await self.permission_repository.update_group(group, request.model_dump(exclude_none=True))
        await self._audit("permission_group_update", "PermissionGroup", str(updated.id), actor, before=before, after=self._snapshot_group(updated))
        return updated

    async def delete_permission_group(self, group_id: UUID, actor: AuthContext | None = None) -> None:
        group = await self._get_group_or_raise(group_id)
        await self._audit("permission_group_delete", "PermissionGroup", str(group.id), actor, before=self._snapshot_group(group))
        await self.permission_repository.delete_group(group)

    async def assign_permission_to_group(self, group_id: UUID, request: PermissionGroupAssignmentRequest, actor: AuthContext | None = None) -> None:
        await self._get_group_or_raise(group_id)
        await self._get_permission_or_raise(request.permission_id)
        await self.permission_repository.assign_permission_to_group(group_id, request.permission_id)
        await self._audit("permission_group_assign", "PermissionGroup", str(group_id), actor, after={"permission_id": str(request.permission_id)})

    async def revoke_permission_from_group(self, group_id: UUID, request: PermissionGroupAssignmentRequest, actor: AuthContext | None = None) -> None:
        await self.permission_repository.revoke_permission_from_group(group_id, request.permission_id)
        await self._audit("permission_group_revoke", "PermissionGroup", str(group_id), actor, after={"permission_id": str(request.permission_id)})

    async def list_policies(self) -> list[AuthorizationPolicy]:
        return await self.policy_repository.list_policies()

    async def create_policy(self, request: PolicyCreateRequest, actor: AuthContext | None = None) -> AuthorizationPolicy:
        if await self.policy_repository.get_by_code(request.code) is not None:
            raise BaseApplicationException("Policy already exists", status_code=409, error_code="policy_conflict")
        policy = AuthorizationPolicy(**request.model_dump())
        created = await self.policy_repository.create(policy)
        await self._audit("policy_create", "AuthorizationPolicy", str(created.id), actor, after=self._snapshot_policy(created))
        await self._cache_policy(created)
        return created

    async def update_policy(self, policy_id: UUID, request: PolicyUpdateRequest, actor: AuthContext | None = None) -> AuthorizationPolicy:
        policy = await self._get_policy_or_raise(policy_id)
        before = self._snapshot_policy(policy)
        updated = await self.policy_repository.update(policy, request.model_dump(exclude_none=True))
        await self._audit("policy_update", "AuthorizationPolicy", str(updated.id), actor, before=before, after=self._snapshot_policy(updated))
        await self._cache_policy(updated)
        return updated

    async def delete_policy(self, policy_id: UUID, actor: AuthContext | None = None) -> None:
        policy = await self._get_policy_or_raise(policy_id)
        await self._audit("policy_delete", "AuthorizationPolicy", str(policy.id), actor, before=self._snapshot_policy(policy))
        await self.policy_repository.delete(policy)
        await self._invalidate_all_caches()

    async def assign_role_to_user(self, user_id: UUID, request: RoleAssignmentRequest, actor: AuthContext | None = None) -> None:
        await self._get_role_or_raise(request.role_id)
        await self._get_user_or_raise(user_id)
        existing_roles = await self.role_repository.list_user_roles(user_id)
        if any(role.id == request.role_id for role in existing_roles):
            raise BaseApplicationException("Role already assigned", status_code=409, error_code="role_assignment_conflict")
        await self.role_repository.assign_user_role(user_id, request.role_id)
        await self._audit("role_assignment", "UserRole", f"{user_id}:{request.role_id}", actor, after={"user_id": str(user_id), "role_id": str(request.role_id)})
        await self._invalidate_user_cache(user_id)

    async def revoke_role_from_user(self, user_id: UUID, request: RoleAssignmentRequest, actor: AuthContext | None = None) -> None:
        await self.role_repository.revoke_user_role(user_id, request.role_id)
        await self._audit("role_revoke", "UserRole", f"{user_id}:{request.role_id}", actor, after={"user_id": str(user_id), "role_id": str(request.role_id)})
        await self._invalidate_user_cache(user_id)

    async def assign_permission_to_role(self, role_id: UUID, request: PermissionAssignmentRequest, actor: AuthContext | None = None) -> None:
        await self._get_role_or_raise(role_id)
        await self._get_permission_or_raise(request.permission_id)
        existing_permissions = await self.permission_repository.permissions_for_role(role_id)
        if any(permission.id == request.permission_id for permission in existing_permissions):
            raise BaseApplicationException("Permission already assigned to role", status_code=409, error_code="permission_assignment_conflict")
        await self.permission_repository.assign_permission_to_role(role_id, request.permission_id)
        await self._audit("permission_assignment", "RolePermission", f"{role_id}:{request.permission_id}", actor, after={"role_id": str(role_id), "permission_id": str(request.permission_id)})
        await self._invalidate_all_caches()

    async def revoke_permission_from_role(self, role_id: UUID, request: PermissionAssignmentRequest, actor: AuthContext | None = None) -> None:
        await self.permission_repository.revoke_permission_from_role(role_id, request.permission_id)
        await self._audit("permission_revoke", "RolePermission", f"{role_id}:{request.permission_id}", actor, after={"role_id": str(role_id), "permission_id": str(request.permission_id)})
        await self._invalidate_all_caches()

    async def add_role_hierarchy(self, request: RoleHierarchyRequest, actor: AuthContext | None = None) -> None:
        if request.parent_role_id == request.child_role_id:
            raise BaseApplicationException("Circular role hierarchy", status_code=409, error_code="role_hierarchy_conflict")
        await self._get_role_or_raise(request.parent_role_id)
        await self._get_role_or_raise(request.child_role_id)
        descendants = await self._descendant_role_ids(request.child_role_id)
        if request.parent_role_id in descendants:
            raise BaseApplicationException("Circular role hierarchy", status_code=409, error_code="role_hierarchy_conflict")
        await self.role_repository.add_hierarchy(request.parent_role_id, request.child_role_id, request.depth)
        await self._audit("role_hierarchy_create", "RoleHierarchy", f"{request.parent_role_id}:{request.child_role_id}", actor, after=request.model_dump())
        await self._invalidate_all_caches()

    async def remove_role_hierarchy(self, request: RoleHierarchyRequest, actor: AuthContext | None = None) -> None:
        await self.role_repository.remove_hierarchy(request.parent_role_id, request.child_role_id)
        await self._audit("role_hierarchy_delete", "RoleHierarchy", f"{request.parent_role_id}:{request.child_role_id}", actor, after=request.model_dump())
        await self._invalidate_all_caches()

    async def build_context(self, auth_context: AuthContext) -> AuthorizationContext:
        user = await self._get_user_or_raise(auth_context.user_id)
        roles = await self.role_repository.list_user_roles(user.id)
        permissions = await self._effective_permissions_for_roles(roles)
        context = AuthorizationContext(
            user_id=user.id,
            session_id=auth_context.session_id,
            role_codes={role.code for role in roles},
            permission_codes={permission.code for permission in permissions},
            policy_codes=set(),
            is_super_admin=any(role.name == "Super Admin" for role in roles),
        )
        await self.cache_repository.cache_context(context, self._cache_ttl())
        await self.cache_repository.cache_roles(user.id, sorted(context.role_codes), self._cache_ttl())
        await self.cache_repository.cache_permissions(user.id, sorted(context.permission_codes), self._cache_ttl())
        return context

    async def authorize(
        self,
        auth_context: AuthContext,
        *,
        resource: str,
        action: str,
        permission_code: str | None = None,
        role_code: str | None = None,
        any_permission_codes: list[str] | None = None,
        any_role_codes: list[str] | None = None,
        owner_id: UUID | None = None,
    ) -> AuthorizationDecision:
        context = await self.build_context(auth_context)

        if owner_id is not None and owner_id == auth_context.user_id:
            return AuthorizationDecision(allowed=True, reason="ownership_match")

        if role_code is not None and role_code not in context.role_codes:
            return AuthorizationDecision(allowed=False, reason="role_required")

        if any_role_codes is not None and not any(role in context.role_codes for role in any_role_codes):
            return AuthorizationDecision(allowed=False, reason="role_required")

        required_permissions = [permission_code] if permission_code else []
        if any_permission_codes is not None:
            required_permissions.extend(any_permission_codes)
        if required_permissions and not any(permission in context.permission_codes for permission in required_permissions):
            await self._log_unauthorized(auth_context, resource, action, reason="permission_required")
            return AuthorizationDecision(allowed=False, reason="permission_required")

        policy_decision = await PolicyEngine(self.policy_repository).evaluate(context, resource, action)
        if not policy_decision.allowed and policy_decision.reason in {"deny_override", "no_allow_policy"}:
            await self._log_unauthorized(auth_context, resource, action, reason=policy_decision.reason)
            return policy_decision

        if required_permissions or role_code or any_role_codes or owner_id is not None:
            return AuthorizationDecision(allowed=True, reason="permission_granted", matched_permission=permission_code)

        return policy_decision if policy_decision.allowed else AuthorizationDecision(allowed=True, reason="default_allow")

    async def bootstrap_defaults(self) -> None:
        permissions: dict[str, Permission] = {}
        for code in DEFAULT_PERMISSION_CODES:
            permission = await self.permission_repository.get_by_code(code)
            if permission is None:
                resource, action = self._split_permission_code(code)
                permission = await self.permission_repository.create(
                    Permission(code=code, resource=resource, action=action, description=f"Default permission for {code}")
                )
            permissions[code] = permission

        roles: dict[str, Role] = {}
        for definition in DEFAULT_ROLE_DEFINITIONS:
            code = str(definition["code"])
            role = await self.role_repository.get_by_code(code)
            if role is None:
                role = await self.role_repository.create(
                    Role(code=code, name=str(definition["name"]), description=f"Default role {definition['name']}")
                )
            roles[code] = role
            for permission_code in definition["permissions"]:
                permission = permissions[str(permission_code)]
                existing = await self.permission_repository.permissions_for_role(role.id)
                if all(item.id != permission.id for item in existing):
                    await self.permission_repository.assign_permission_to_role(role.id, permission.id)

        for parent_code, child_code in DEFAULT_ROLE_HIERARCHY:
            parent_role = roles[parent_code]
            child_role = roles[child_code]
            descendants = await self._descendant_role_ids(child_role.id)
            if parent_role.id not in descendants:
                try:
                    await self.role_repository.add_hierarchy(parent_role.id, child_role.id, depth=1)
                except Exception:
                    pass

        for group_definition in DEFAULT_PERMISSION_GROUPS:
            code = str(group_definition["code"])
            group = await self.permission_repository.get_group_by_code(code)
            if group is None:
                group = await self.permission_repository.create_group(
                    PermissionGroup(code=code, name=str(group_definition["name"]), description=f"Default permission group {group_definition['name']}")
                )
            for permission_code in group_definition["permissions"]:
                permission = permissions[str(permission_code)]
                existing = await self.permission_repository.group_permissions(group.id)
                if all(item.id != permission.id for item in existing):
                    await self.permission_repository.assign_permission_to_group(group.id, permission.id)

    async def _effective_permissions_for_roles(self, roles: list[Role]) -> list[Permission]:
        permissions: dict[UUID, Permission] = {}
        for role in roles:
            for permission in await self.permission_repository.permissions_for_role(role.id):
                permissions[permission.id] = permission
            for parent_id in await self.role_repository.parent_role_ids(role.id):
                parent_role = await self.role_repository.get_by_id(parent_id)
                if parent_role is None:
                    continue
                for permission in await self.permission_repository.permissions_for_role(parent_role.id):
                    permissions[permission.id] = permission
        return list(permissions.values())

    async def _descendant_role_ids(self, role_id: UUID) -> set[UUID]:
        descendants: set[UUID] = set()
        queue = [role_id]
        while queue:
            current = queue.pop()
            for child_id in await self.role_repository.child_role_ids(current):
                if child_id in descendants:
                    continue
                descendants.add(child_id)
                queue.append(child_id)
        return descendants

    async def _permission_conflict_exists(self, resource: str, action: str, *, exclude_id: UUID | None = None) -> bool:
        for permission in await self.permission_repository.list_permissions():
            if exclude_id is not None and permission.id == exclude_id:
                continue
            if permission.resource == resource and permission.action == action:
                return True
        return False

    async def _get_role_or_raise(self, role_id: UUID) -> Role:
        role = await self.role_repository.get_by_id(role_id)
        if role is None:
            raise AuthorizationApplicationException("Role not found")
        return role

    async def _get_permission_or_raise(self, permission_id: UUID) -> Permission:
        permission = await self.permission_repository.get_by_id(permission_id)
        if permission is None:
            raise AuthorizationApplicationException("Permission not found")
        return permission

    async def _get_group_or_raise(self, group_id: UUID) -> PermissionGroup:
        group = await self.permission_repository.session.get(PermissionGroup, group_id)
        if group is None:
            raise AuthorizationApplicationException("Permission group not found")
        return group

    async def _get_policy_or_raise(self, policy_id: UUID) -> AuthorizationPolicy:
        policy = await self.policy_repository.get_by_id(policy_id)
        if policy is None:
            raise AuthorizationApplicationException("Policy not found")
        return policy

    async def _get_user_or_raise(self, user_id: UUID) -> User:
        user = await self.role_repository.session.get(User, user_id)
        if user is None:
            raise AuthorizationApplicationException("User not found")
        return user

    async def _invalidate_all_caches(self) -> None:
        await self.cache_repository.invalidate_all()

    async def _invalidate_user_cache(self, user_id: UUID) -> None:
        await self.cache_repository.invalidate_user(user_id)

    async def _cache_policy(self, policy: AuthorizationPolicy) -> None:
        await self.cache_repository.cache_policy(policy.code, self._snapshot_policy(policy), self._cache_ttl())

    def _cache_ttl(self) -> int:
        return max(300, int(self.settings.session_idle_timeout_minutes * 60))

    async def _audit(
        self,
        action: str,
        entity_type: str,
        entity_id: str,
        actor: AuthContext | None,
        *,
        before: dict[str, object] | None = None,
        after: dict[str, object] | None = None,
    ) -> None:
        audit_log = AuditLog(
            actor_user_id=actor.user_id if actor else None,
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            before_state=before,
            after_state=after,
            context={"source": "authorization_service"},
            request_path=None,
            request_method=None,
            status="success",
        )
        self.role_repository.session.add(audit_log)
        await self.role_repository.session.flush()
        self.audit_logger.info(action, extra={"entity_type": entity_type, "entity_id": entity_id})

    async def _log_unauthorized(self, auth_context: AuthContext, resource: str, action: str, *, reason: str) -> None:
        audit_log = AuditLog(
            actor_user_id=auth_context.user_id,
            entity_type=resource,
            entity_id=str(auth_context.user_id),
            action=f"unauthorized_{action}",
            before_state=None,
            after_state=None,
            context={"reason": reason},
            request_path=None,
            request_method=None,
            status="forbidden",
        )
        self.role_repository.session.add(audit_log)
        await self.role_repository.session.flush()

    def _snapshot_role(self, role: Role) -> dict[str, object]:
        return {"id": str(role.id), "code": role.code, "name": role.name, "description": role.description, "status": role.status}

    def _snapshot_permission(self, permission: Permission) -> dict[str, object]:
        return {
            "id": str(permission.id),
            "code": permission.code,
            "resource": permission.resource,
            "action": permission.action,
            "description": permission.description,
            "category": permission.category,
        }

    def _snapshot_group(self, group: PermissionGroup) -> dict[str, object]:
        return {"id": str(group.id), "code": group.code, "name": group.name, "description": group.description, "status": group.status}

    def _snapshot_policy(self, policy: AuthorizationPolicy) -> dict[str, object]:
        return {
            "id": str(policy.id),
            "code": policy.code,
            "name": policy.name,
            "description": policy.description,
            "effect": policy.effect,
            "priority": policy.priority,
            "subject_type": policy.subject_type,
            "subject_value": policy.subject_value,
            "resource": policy.resource,
            "action": policy.action,
            "conditions": policy.conditions,
            "enabled": policy.enabled,
        }

    def _split_permission_code(self, code: str) -> tuple[str, str]:
        if "." not in code:
            return code.lower(), code.lower()
        resource, action = code.split(".", 1)
        return resource, action.lower()

