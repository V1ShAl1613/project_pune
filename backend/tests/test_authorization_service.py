from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.auth.models import AuthContext
from app.authorization.models import AuthorizationContext
from app.authorization.permissions.catalog import DEFAULT_PERMISSION_CODES
from app.authorization.repositories.cache_repository import AuthorizationCacheRepository
from app.authorization.schemas.authorization import (
    PermissionAssignmentRequest,
    PermissionCreateRequest,
    PermissionGroupCreateRequest,
    PolicyCreateRequest,
    RoleAssignmentRequest,
    RoleCreateRequest,
    RoleHierarchyRequest,
)
from app.authorization.services.authorization_service import AuthorizationService
from app.core.settings import TestingSettings
from app.database.models.authorization import AuthorizationPolicy, PermissionGroup
from app.database.models.identity import Permission, Role, User, UserRole
from app.database.models.operational import AuditLog


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, object] = {}

    async def setex(self, key: str, ttl_seconds: int, value: object) -> None:
        self.values[key] = value

    async def get(self, key: str):
        return self.values.get(key)

    async def delete(self, *keys: str) -> None:
        for key in keys:
            self.values.pop(key, None)

    async def flushdb(self) -> None:
        self.values.clear()

    async def scan_iter(self, match: str | None = None):
        for key in list(self.values.keys()):
            if match is None or key.startswith(match.rstrip("*")):
                yield key


class FakeSession:
    def __init__(self) -> None:
        self.store: dict[type[object], dict[object, object]] = {
            Role: {},
            Permission: {},
            PermissionGroup: {},
            AuthorizationPolicy: {},
            User: {},
            AuditLog: {},
            UserRole: {},
        }

    def add(self, entity) -> None:
        if getattr(entity, "id", None) is None and hasattr(entity, "id"):
            entity.id = uuid4()
        bucket = self.store.setdefault(type(entity), {})
        identifier = getattr(entity, "id", None)
        if identifier is not None:
            bucket[identifier] = entity

    async def flush(self) -> None:
        return None

    async def get(self, model, identifier):
        return self.store.get(model, {}).get(identifier)

    async def delete(self, entity) -> None:
        bucket = self.store.get(type(entity), {})
        identifier = getattr(entity, "id", None)
        if identifier is not None:
            bucket.pop(identifier, None)


@dataclass(slots=True)
class FakeRoleRepository:
    session: FakeSession
    hierarchies: list[tuple[UUID, UUID, int, bool]] = field(default_factory=list)
    user_roles: dict[UUID, list[UserRole]] = field(default_factory=dict)

    async def list_roles(self) -> list[Role]:
        return sorted(self.session.store[Role].values(), key=lambda role: role.name)

    async def get_by_id(self, role_id: UUID) -> Role | None:
        return self.session.store[Role].get(role_id)

    async def get_by_code(self, code: str) -> Role | None:
        for role in self.session.store[Role].values():
            if role.code == code:
                return role
        return None

    async def create(self, role: Role) -> Role:
        self.session.add(role)
        return role

    async def update(self, role: Role, values: dict[str, object]) -> Role:
        for key, value in values.items():
            setattr(role, key, value)
        return role

    async def delete(self, role: Role) -> None:
        self.session.store[Role].pop(role.id, None)

    async def assign_user_role(self, user_id: UUID, role_id: UUID) -> UserRole:
        assignment = UserRole(user_id=user_id, role_id=role_id)
        assignment.role = self.session.store[Role][role_id]
        self.user_roles.setdefault(user_id, []).append(assignment)
        self.session.add(assignment)
        return assignment

    async def revoke_user_role(self, user_id: UUID, role_id: UUID) -> int:
        assignments = self.user_roles.get(user_id, [])
        self.user_roles[user_id] = [assignment for assignment in assignments if assignment.role_id != role_id]
        return 1

    async def list_user_roles(self, user_id: UUID) -> list[Role]:
        return [assignment.role for assignment in self.user_roles.get(user_id, [])]

    async def add_hierarchy(self, parent_role_id: UUID, child_role_id: UUID, depth: int = 1):
        self.hierarchies.append((parent_role_id, child_role_id, depth, True))

    async def remove_hierarchy(self, parent_role_id: UUID, child_role_id: UUID) -> int:
        self.hierarchies = [edge for edge in self.hierarchies if not (edge[0] == parent_role_id and edge[1] == child_role_id)]
        return 1

    async def parent_role_ids(self, child_role_id: UUID) -> list[UUID]:
        return [parent_id for parent_id, child_id, depth, active in self.hierarchies if child_id == child_role_id and active]

    async def child_role_ids(self, parent_role_id: UUID) -> list[UUID]:
        return [child_id for parent_id, child_id, depth, active in self.hierarchies if parent_id == parent_role_id and active]


@dataclass(slots=True)
class FakePermissionRepository:
    session: FakeSession
    role_permissions: dict[UUID, set[UUID]] = field(default_factory=dict)
    group_assignments: dict[UUID, set[UUID]] = field(default_factory=dict)

    async def list_permissions(self) -> list[Permission]:
        return sorted(self.session.store[Permission].values(), key=lambda permission: permission.code)

    async def get_by_id(self, permission_id: UUID) -> Permission | None:
        return self.session.store[Permission].get(permission_id)

    async def get_by_code(self, code: str) -> Permission | None:
        for permission in self.session.store[Permission].values():
            if permission.code == code:
                return permission
        return None

    async def create(self, permission: Permission) -> Permission:
        self.session.add(permission)
        return permission

    async def update(self, permission: Permission, values: dict[str, object]) -> Permission:
        for key, value in values.items():
            setattr(permission, key, value)
        return permission

    async def delete(self, permission: Permission) -> None:
        self.session.store[Permission].pop(permission.id, None)

    async def assign_permission_to_role(self, role_id: UUID, permission_id: UUID):
        self.role_permissions.setdefault(role_id, set()).add(permission_id)

    async def revoke_permission_from_role(self, role_id: UUID, permission_id: UUID) -> int:
        self.role_permissions.setdefault(role_id, set()).discard(permission_id)
        return 1

    async def permissions_for_role(self, role_id: UUID) -> list[Permission]:
        ids = self.role_permissions.get(role_id, set())
        return [self.session.store[Permission][permission_id] for permission_id in ids]

    async def list_groups(self) -> list[PermissionGroup]:
        return sorted(self.session.store[PermissionGroup].values(), key=lambda group: group.code)

    async def get_group_by_code(self, code: str) -> PermissionGroup | None:
        for group in self.session.store[PermissionGroup].values():
            if group.code == code:
                return group
        return None

    async def create_group(self, group: PermissionGroup) -> PermissionGroup:
        self.session.add(group)
        return group

    async def update_group(self, group: PermissionGroup, values: dict[str, object]) -> PermissionGroup:
        for key, value in values.items():
            setattr(group, key, value)
        return group

    async def delete_group(self, group: PermissionGroup) -> None:
        self.session.store[PermissionGroup].pop(group.id, None)

    async def assign_permission_to_group(self, group_id: UUID, permission_id: UUID):
        self.group_assignments.setdefault(group_id, set()).add(permission_id)

    async def revoke_permission_from_group(self, group_id: UUID, permission_id: UUID) -> int:
        self.group_assignments.setdefault(group_id, set()).discard(permission_id)
        return 1

    async def group_permissions(self, group_id: UUID) -> list[Permission]:
        ids = self.group_assignments.get(group_id, set())
        return [self.session.store[Permission][permission_id] for permission_id in ids]


@dataclass(slots=True)
class FakePolicyRepository:
    session: FakeSession

    async def list_policies(self) -> list[AuthorizationPolicy]:
        return sorted(self.session.store[AuthorizationPolicy].values(), key=lambda policy: policy.priority)

    async def active_policies(self) -> list[AuthorizationPolicy]:
        return [policy for policy in self.session.store[AuthorizationPolicy].values() if policy.enabled and policy.deleted_at is None]

    async def get_by_id(self, policy_id: UUID) -> AuthorizationPolicy | None:
        return self.session.store[AuthorizationPolicy].get(policy_id)

    async def get_by_code(self, code: str) -> AuthorizationPolicy | None:
        for policy in self.session.store[AuthorizationPolicy].values():
            if policy.code == code:
                return policy
        return None

    async def create(self, policy: AuthorizationPolicy) -> AuthorizationPolicy:
        self.session.add(policy)
        return policy

    async def update(self, policy: AuthorizationPolicy, values: dict[str, object]) -> AuthorizationPolicy:
        for key, value in values.items():
            setattr(policy, key, value)
        return policy

    async def delete(self, policy: AuthorizationPolicy) -> None:
        self.session.store[AuthorizationPolicy].pop(policy.id, None)


def build_service() -> tuple[AuthorizationService, FakeSession, FakeRoleRepository, FakePermissionRepository, FakePolicyRepository]:
    session = FakeSession()
    redis = FakeRedis()
    settings = TestingSettings()
    cache_repository = AuthorizationCacheRepository(redis)
    role_repository = FakeRoleRepository(session)
    permission_repository = FakePermissionRepository(session)
    policy_repository = FakePolicyRepository(session)
    service = AuthorizationService(
        role_repository=role_repository,
        permission_repository=permission_repository,
        policy_repository=policy_repository,
        cache_repository=cache_repository,
        settings=settings,
        logger=__import__("logging").getLogger("test.authorization"),
        audit_logger=__import__("logging").getLogger("test.authorization.audit"),
    )
    return service, session, role_repository, permission_repository, policy_repository


@pytest.mark.asyncio
async def test_bootstrap_defaults_and_role_hierarchy() -> None:
    service, session, role_repository, permission_repository, policy_repository = build_service()

    await service.bootstrap_defaults()

    assert await role_repository.get_by_code("super_admin") is not None
    assert await permission_repository.get_by_code("Role.Read") is not None
    assert len(await role_repository.list_roles()) == 10
    assert len(await permission_repository.list_permissions()) == len(DEFAULT_PERMISSION_CODES)
    assert len(role_repository.hierarchies) == 4


@pytest.mark.asyncio
async def test_authorize_respects_role_inheritance_and_deny_policy() -> None:
    service, session, role_repository, permission_repository, policy_repository = build_service()
    await service.bootstrap_defaults()

    user = User(email="alice@example.com", username="alice", display_name="Alice", status="active", password_hash="hash")
    session.add(user)
    read_only = await role_repository.get_by_code("read_only")
    assert read_only is not None
    await role_repository.assign_user_role(user.id, read_only.id)

    context = await service.authorize(AuthContext(user_id=user.id, session_id=user.id, access_token_jti="jti", refresh_token_jti=None, token_type="access"), resource="Dashboard", action="Read", permission_code="Dashboard.Read")
    assert context.allowed is True

    policy = AuthorizationPolicy(code="deny_dashboard_for_read_only", name="Deny dashboard", effect="deny", priority=1, subject_type="role", subject_value="read_only", resource="Dashboard", action="Read", conditions={}, enabled=True)
    session.add(policy)
    denied = await service.authorize(AuthContext(user_id=user.id, session_id=user.id, access_token_jti="jti", refresh_token_jti=None, token_type="access"), resource="Dashboard", action="Read", permission_code="Dashboard.Read")
    assert denied.allowed is False
    assert denied.reason == "deny_override"


@pytest.mark.asyncio
async def test_role_and_permission_crud_and_assignments() -> None:
    service, session, role_repository, permission_repository, policy_repository = build_service()

    role = await service.create_role(RoleCreateRequest(code="security_lead", name="Security Lead"))
    permission = await service.create_permission(PermissionCreateRequest(code="Role.Export", resource="Role", action="Export", description="Export role data"))
    group = await service.create_permission_group(PermissionGroupCreateRequest(code="role_exports", name="Role Exports"))

    await service.assign_permission_to_role(role.id, PermissionAssignmentRequest(permission_id=permission.id))
    await service.assign_permission_to_group(group.id, __import__("app.authorization.schemas.authorization", fromlist=["PermissionGroupAssignmentRequest"]).PermissionGroupAssignmentRequest(permission_id=permission.id))

    updated_role = await service.update_role(role.id, __import__("app.authorization.schemas.authorization", fromlist=["RoleUpdateRequest"]).RoleUpdateRequest(description="Updated"))
    assert updated_role.description == "Updated"

    user = User(email="bob@example.com", username="bob", display_name="Bob", status="active", password_hash="hash")
    session.add(user)
    await service.assign_role_to_user(user.id, RoleAssignmentRequest(role_id=role.id))
    authorized = await service.authorize(AuthContext(user_id=user.id, session_id=user.id, access_token_jti="jti", refresh_token_jti=None, token_type="access"), resource="Role", action="Export", permission_code="Role.Export")
    assert authorized.allowed is True
