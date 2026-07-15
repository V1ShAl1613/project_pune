from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import AuditMixin, BaseModel, SoftDeleteMixin, TimestampMixin, UUIDMixin, VersionMixin

if TYPE_CHECKING:
    from app.database.models.identity import Permission, Role, User


class PermissionGroup(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "permission_groups"
    __table_args__ = (
        UniqueConstraint("code", name="uq_permission_groups_code"),
        Index("ix_permission_groups_status", "status"),
    )

    code: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    permissions: Mapped[list[PermissionGroupPermission]] = relationship(cascade="all, delete-orphan", overlaps="group")


class PermissionGroupPermission(BaseModel, TimestampMixin, AuditMixin):
    __tablename__ = "permission_group_permissions"
    __table_args__ = (
        UniqueConstraint("group_id", "permission_id", name="uq_permission_group_permissions_group_permission"),
        Index("ix_permission_group_permissions_group_id", "group_id"),
        Index("ix_permission_group_permissions_permission_id", "permission_id"),
    )

    group_id: Mapped[UUID] = mapped_column(ForeignKey("permission_groups.id", ondelete="CASCADE"), primary_key=True)
    permission_id: Mapped[UUID] = mapped_column(ForeignKey("permissions.id", ondelete="CASCADE"), primary_key=True)
    granted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    group: Mapped[PermissionGroup] = relationship(overlaps="permissions")
    permission: Mapped[Permission] = relationship(overlaps="permissions")


class RoleHierarchy(BaseModel, TimestampMixin, AuditMixin):
    __tablename__ = "role_hierarchy"
    __table_args__ = (
        UniqueConstraint("parent_role_id", "child_role_id", name="uq_role_hierarchy_parent_child"),
        Index("ix_role_hierarchy_parent_role_id", "parent_role_id"),
        Index("ix_role_hierarchy_child_role_id", "child_role_id"),
    )

    parent_role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    child_role_id: Mapped[UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
    depth: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    parent_role: Mapped[Role] = relationship(foreign_keys=[parent_role_id])
    child_role: Mapped[Role] = relationship(foreign_keys=[child_role_id])


class AuthorizationPolicy(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "authorization_policies"
    __table_args__ = (
        UniqueConstraint("code", name="uq_authorization_policies_code"),
        Index("ix_authorization_policies_priority", "priority"),
        Index("ix_authorization_policies_resource_action", "resource", "action"),
        Index("ix_authorization_policies_effect_enabled", "effect", "enabled"),
    )

    code: Mapped[str] = mapped_column(String(128), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    effect: Mapped[str] = mapped_column(String(16), nullable=False, default="allow")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)
    subject_type: Mapped[str] = mapped_column(String(32), nullable=False, default="role")
    subject_value: Mapped[str | None] = mapped_column(String(128), nullable=True)
    resource: Mapped[str] = mapped_column(String(128), nullable=False)
    action: Mapped[str] = mapped_column(String(64), nullable=False)
    conditions: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
