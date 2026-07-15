from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RoleBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    description: str | None = None
    status: str = "active"


class RoleCreateRequest(RoleBase):
    pass


class RoleUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    description: str | None = None
    status: str | None = None


class PermissionBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    resource: str
    action: str
    description: str | None = None
    category: str | None = None


class PermissionCreateRequest(PermissionBase):
    pass


class PermissionUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    resource: str | None = None
    action: str | None = None
    description: str | None = None
    category: str | None = None


class PermissionGroupCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    description: str | None = None
    status: str = "active"


class PermissionGroupUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    description: str | None = None
    status: str | None = None


class PolicyCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    description: str | None = None
    effect: str = Field(pattern="^(allow|deny)$")
    priority: int = Field(ge=0)
    subject_type: str = Field(pattern="^(role|permission|user|any)$")
    subject_value: str | None = None
    resource: str
    action: str
    conditions: dict[str, object] = Field(default_factory=dict)
    enabled: bool = True


class PolicyUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    description: str | None = None
    effect: str | None = Field(default=None, pattern="^(allow|deny)$")
    priority: int | None = Field(default=None, ge=0)
    subject_type: str | None = Field(default=None, pattern="^(role|permission|user|any)$")
    subject_value: str | None = None
    resource: str | None = None
    action: str | None = None
    conditions: dict[str, object] | None = None
    enabled: bool | None = None


class RoleAssignmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role_id: UUID


class PermissionAssignmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    permission_id: UUID


class PermissionGroupAssignmentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    permission_id: UUID


class RoleHierarchyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    parent_role_id: UUID
    child_role_id: UUID
    depth: int = Field(default=1, ge=1)


class RoleResponse(RoleBase):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class PermissionResponse(PermissionBase):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime


class PermissionGroupResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    code: str
    name: str
    description: str | None
    status: str
    created_at: datetime
    updated_at: datetime


class PolicyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    code: str
    name: str
    description: str | None
    effect: str
    priority: int
    subject_type: str
    subject_value: str | None
    resource: str
    action: str
    conditions: dict[str, object]
    enabled: bool
    created_at: datetime
    updated_at: datetime


class AuthorizationDecisionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed: bool
    reason: str
    matched_policy: str | None = None
    matched_permission: str | None = None

