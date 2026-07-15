from __future__ import annotations

from uuid import UUID

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index, JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import AuditMixin, BaseModel, SoftDeleteMixin, TimestampMixin, UUIDMixin, VersionMixin

if TYPE_CHECKING:
    from app.database.models.identity import Role, User
    from app.database.models.tenancy import DepartmentSettings, OrganizationSettings, TeamSettings, Tenant, Employee


class Organization(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "organizations"
    __table_args__ = (
        Index("ix_organizations_tenant_status", "tenant_id", "status"),
        UniqueConstraint("code", name="uq_organizations_code"),
        Index("ix_organizations_name_status", "name", "status"),
    )

    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    description: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    organization_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    organization_settings: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    tenant: Mapped[Tenant] = relationship(back_populates="organizations")
    users: Mapped[list[User]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    departments: Mapped[list[Department]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    roles: Mapped[list[Role]] = relationship(back_populates="organization", cascade="all, delete-orphan")
    settings: Mapped[OrganizationSettings | None] = relationship(back_populates="organization", cascade="all, delete-orphan", uselist=False)


class Department(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "departments"
    __table_args__ = (
        Index("ix_departments_tenant_status", "tenant_id", "status"),
        UniqueConstraint("organization_id", "code", name="uq_departments_organization_code"),
        Index("ix_departments_organization_name", "organization_id", "name"),
    )

    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    organization_id: Mapped[UUID] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    manager_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    department_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    tenant: Mapped[Tenant] = relationship(back_populates="departments")
    organization: Mapped[Organization] = relationship(back_populates="departments")
    teams: Mapped[list[Team]] = relationship(back_populates="department", cascade="all, delete-orphan")
    users: Mapped[list[User]] = relationship(back_populates="department", foreign_keys="User.department_id")
    manager: Mapped[User | None] = relationship(foreign_keys=[manager_user_id])
    settings: Mapped[DepartmentSettings | None] = relationship(back_populates="department", cascade="all, delete-orphan", uselist=False)
    employees: Mapped[list[Employee]] = relationship(back_populates="department", cascade="all, delete-orphan")


class Team(BaseModel, UUIDMixin, TimestampMixin, SoftDeleteMixin, AuditMixin, VersionMixin):
    __tablename__ = "teams"
    __table_args__ = (
        Index("ix_teams_tenant_status", "tenant_id", "status"),
        UniqueConstraint("department_id", "code", name="uq_teams_department_code"),
        Index("ix_teams_department_name", "department_id", "name"),
    )

    tenant_id: Mapped[UUID] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    department_id: Mapped[UUID] = mapped_column(ForeignKey("departments.id", ondelete="CASCADE"), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    lead_user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    team_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)

    tenant: Mapped[Tenant] = relationship(back_populates="teams")
    department: Mapped[Department] = relationship(back_populates="teams")
    users: Mapped[list[User]] = relationship(back_populates="team", foreign_keys="User.team_id")
    lead: Mapped[User | None] = relationship(foreign_keys=[lead_user_id])
    settings: Mapped[TeamSettings | None] = relationship(back_populates="team", cascade="all, delete-orphan", uselist=False)
    employees: Mapped[list[Employee]] = relationship(back_populates="team", cascade="all, delete-orphan")
