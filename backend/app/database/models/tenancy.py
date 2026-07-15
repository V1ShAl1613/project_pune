from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import AuditMixin, BaseModel, SoftDeleteMixin, TimestampMixin, UUIDMixin, VersionMixin

if TYPE_CHECKING:
    from app.database.models.identity import User
    from app.database.models.organization import Department, Organization, Team


class Tenant(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "tenants"
    __table_args__ = (
        UniqueConstraint("code", name="uq_tenants_code"),
        Index("ix_tenants_name_status", "name", "status"),
    )

    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    configuration: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    tenant_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    activated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    suspended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    organizations: Mapped[list[Organization]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    departments: Mapped[list[Department]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    teams: Mapped[list[Team]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    users: Mapped[list[User]] = relationship(back_populates="tenant", cascade="all, delete-orphan")
    employees: Mapped[list[Employee]] = relationship(back_populates="tenant", cascade="all, delete-orphan")


class OrganizationSettings(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, VersionMixin):
    __tablename__ = "organization_settings"
    __table_args__ = (UniqueConstraint("organization_id", name="uq_organization_settings_organization_id"),)

    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    settings: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    organization: Mapped[Organization] = relationship(back_populates="settings")


class DepartmentSettings(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, VersionMixin):
    __tablename__ = "department_settings"
    __table_args__ = (UniqueConstraint("department_id", name="uq_department_settings_department_id"),)

    department_id: Mapped[UUID] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    settings: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    department: Mapped[Department] = relationship(back_populates="settings")


class TeamSettings(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, VersionMixin):
    __tablename__ = "team_settings"
    __table_args__ = (UniqueConstraint("team_id", name="uq_team_settings_team_id"),)

    team_id: Mapped[UUID] = mapped_column(ForeignKey("teams.id", ondelete="CASCADE"), nullable=False)
    settings: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")

    team: Mapped[Team] = relationship(back_populates="settings")


class Employee(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "employees"
    __table_args__ = (
        UniqueConstraint("employee_id", name="uq_employees_employee_id"),
        UniqueConstraint("user_id", name="uq_employees_user_id"),
        Index("ix_employees_tenant_status", "tenant_id", "status"),
        Index("ix_employees_department_team", "department_id", "team_id"),
    )

    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    employee_id: Mapped[str] = mapped_column(String(64), nullable=False)
    designation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department_id: Mapped[UUID | None] = mapped_column(ForeignKey("departments.id", ondelete="SET NULL"), nullable=True)
    team_id: Mapped[UUID | None] = mapped_column(ForeignKey("teams.id", ondelete="SET NULL"), nullable=True)
    manager_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    hire_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    employment_status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    employee_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    tenant: Mapped[Tenant] = relationship(back_populates="employees")
    user: Mapped[User] = relationship(foreign_keys=[user_id], back_populates="employee_record")
    manager: Mapped[User | None] = relationship(foreign_keys=[manager_user_id])
    department: Mapped[Department | None] = relationship(back_populates="employees")
    team: Mapped[Team | None] = relationship(back_populates="employees")


class UserProfile(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, VersionMixin):
    __tablename__ = "user_profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_profiles_user_id"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    first_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    country: Mapped[str | None] = mapped_column(String(2), nullable=True)
    phone_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    profile_picture_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    theme: Mapped[str | None] = mapped_column(String(32), nullable=True)
    dashboard_layout: Mapped[str | None] = mapped_column(String(64), nullable=True)
    emergency_contact_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    emergency_contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    personal_information: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    contact_information: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    employment_information: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    accessibility_preferences: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    user: Mapped[User] = relationship(back_populates="profile_record")


class UserPreference(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, VersionMixin):
    __tablename__ = "user_preferences"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_preferences_user_id"),)

    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    theme: Mapped[str | None] = mapped_column(String(32), nullable=True)
    language: Mapped[str | None] = mapped_column(String(32), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    dashboard_layout: Mapped[str | None] = mapped_column(String(64), nullable=True)
    notification_preferences: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    security_preferences: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    accessibility_preferences: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    user: Mapped[User] = relationship(back_populates="preference_record")


class Directory(BaseModel, UUIDMixin, TimestampMixin, AuditMixin, VersionMixin):
    __tablename__ = "directory_entries"
    __table_args__ = (
        UniqueConstraint("tenant_id", "entity_type", "entity_id", name="uq_directory_entries_tenant_entity"),
        Index("ix_directory_entries_tenant_display_name", "tenant_id", "display_name"),
        Index("ix_directory_entries_tenant_email", "tenant_id", "email"),
        Index("ix_directory_entries_tenant_status", "tenant_id", "status"),
    )

    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    organization_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    team_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    role_codes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    directory_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

