from __future__ import annotations

from collections.abc import Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Any, AsyncIterator
from uuid import UUID

from sqlalchemy import delete, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Directory, Department, Employee, Organization, OrganizationSettings, Team, TeamSettings, Tenant, User, UserPreference, UserProfile
from app.database.models.identity import Role, UserRole
from app.database.models.organization import Department as DepartmentModel, Organization as OrganizationModel, Team as TeamModel


@dataclass(slots=True)
class IdentityRepository:
    session: AsyncSession

    @asynccontextmanager
    async def transaction(self) -> AsyncIterator[AsyncSession]:
        if self.session.in_transaction():
            async with self.session.begin_nested():
                yield self.session
            tx = self.session.get_transaction()
            if tx is not None and not tx.nested:
                await self.session.commit()
        else:
            async with self.session.begin():
                yield self.session

    async def get_tenant(self, tenant_id: UUID) -> Tenant | None:
        return await self.session.get(Tenant, tenant_id)

    async def get_tenant_by_code(self, code: str) -> Tenant | None:
        result = await self.session.execute(select(Tenant).where(Tenant.code == code))
        return result.scalar_one_or_none()

    async def list_tenants(self) -> list[Tenant]:
        result = await self.session.execute(select(Tenant).order_by(Tenant.name.asc()))
        return list(result.scalars().all())

    async def create_tenant(self, tenant: Tenant) -> Tenant:
        self.session.add(tenant)
        await self.session.flush()
        return tenant

    async def update_tenant(self, tenant: Tenant, values: dict[str, Any]) -> Tenant:
        for key, value in values.items():
            if hasattr(tenant, key):
                setattr(tenant, key, value)
        await self.session.flush()
        return tenant

    async def delete_tenant(self, tenant: Tenant) -> None:
        await self.session.delete(tenant)

    async def get_organization(self, organization_id: UUID) -> OrganizationModel | None:
        return await self.session.get(OrganizationModel, organization_id)

    async def get_organization_by_code(self, tenant_id: UUID, code: str) -> OrganizationModel | None:
        result = await self.session.execute(select(OrganizationModel).where(OrganizationModel.tenant_id == tenant_id, OrganizationModel.code == code))
        return result.scalar_one_or_none()

    async def list_organizations(self, tenant_id: UUID, filters: dict[str, Any] | None = None) -> list[OrganizationModel]:
        statement = select(OrganizationModel).where(OrganizationModel.tenant_id == tenant_id)
        if filters:
            if status := filters.get("status"):
                statement = statement.where(OrganizationModel.status == status)
            if search := filters.get("search"):
                statement = statement.where(or_(OrganizationModel.name.ilike(f"%{search}%"), OrganizationModel.code.ilike(f"%{search}%")))
        result = await self.session.execute(statement.order_by(OrganizationModel.name.asc()))
        return list(result.scalars().all())

    async def create_organization(self, organization: OrganizationModel) -> OrganizationModel:
        self.session.add(organization)
        await self.session.flush()
        return organization

    async def update_organization(self, organization: OrganizationModel, values: dict[str, Any]) -> OrganizationModel:
        for key, value in values.items():
            if hasattr(organization, key):
                setattr(organization, key, value)
        await self.session.flush()
        return organization

    async def delete_organization(self, organization: OrganizationModel) -> None:
        await self.session.delete(organization)

    async def get_department(self, department_id: UUID) -> DepartmentModel | None:
        return await self.session.get(DepartmentModel, department_id)

    async def get_department_by_code(self, organization_id: UUID, code: str) -> DepartmentModel | None:
        result = await self.session.execute(select(DepartmentModel).where(DepartmentModel.organization_id == organization_id, DepartmentModel.code == code))
        return result.scalar_one_or_none()

    async def list_departments(self, tenant_id: UUID, filters: dict[str, Any] | None = None) -> list[DepartmentModel]:
        statement = select(DepartmentModel).where(DepartmentModel.tenant_id == tenant_id)
        if filters:
            if organization_id := filters.get("organization_id"):
                statement = statement.where(DepartmentModel.organization_id == organization_id)
            if status := filters.get("status"):
                statement = statement.where(DepartmentModel.status == status)
            if search := filters.get("search"):
                statement = statement.where(or_(DepartmentModel.name.ilike(f"%{search}%"), DepartmentModel.code.ilike(f"%{search}%")))
        result = await self.session.execute(statement.order_by(DepartmentModel.name.asc()))
        return list(result.scalars().all())

    async def create_department(self, department: DepartmentModel) -> DepartmentModel:
        self.session.add(department)
        await self.session.flush()
        return department

    async def update_department(self, department: DepartmentModel, values: dict[str, Any]) -> DepartmentModel:
        for key, value in values.items():
            if hasattr(department, key):
                setattr(department, key, value)
        await self.session.flush()
        return department

    async def delete_department(self, department: DepartmentModel) -> None:
        await self.session.delete(department)

    async def get_team(self, team_id: UUID) -> TeamModel | None:
        return await self.session.get(TeamModel, team_id)

    async def get_team_by_code(self, department_id: UUID, code: str) -> TeamModel | None:
        result = await self.session.execute(select(TeamModel).where(TeamModel.department_id == department_id, TeamModel.code == code))
        return result.scalar_one_or_none()

    async def list_teams(self, tenant_id: UUID, filters: dict[str, Any] | None = None) -> list[TeamModel]:
        statement = select(TeamModel).where(TeamModel.tenant_id == tenant_id)
        if filters:
            if department_id := filters.get("department_id"):
                statement = statement.where(TeamModel.department_id == department_id)
            if status := filters.get("status"):
                statement = statement.where(TeamModel.status == status)
            if search := filters.get("search"):
                statement = statement.where(or_(TeamModel.name.ilike(f"%{search}%"), TeamModel.code.ilike(f"%{search}%")))
        result = await self.session.execute(statement.order_by(TeamModel.name.asc()))
        return list(result.scalars().all())

    async def create_team(self, team: TeamModel) -> TeamModel:
        self.session.add(team)
        await self.session.flush()
        return team

    async def update_team(self, team: TeamModel, values: dict[str, Any]) -> TeamModel:
        for key, value in values.items():
            if hasattr(team, key):
                setattr(team, key, value)
        await self.session.flush()
        return team

    async def delete_team(self, team: TeamModel) -> None:
        await self.session.delete(team)

    async def get_user(self, user_id: UUID) -> User | None:
        return await self.session.get(User, user_id)

    async def get_user_by_email(self, tenant_id: UUID, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.tenant_id == tenant_id, func.lower(User.email) == email.strip().lower()))
        return result.scalar_one_or_none()

    async def get_user_by_username(self, tenant_id: UUID, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.tenant_id == tenant_id, func.lower(User.username) == username.strip().lower()))
        return result.scalar_one_or_none()

    async def get_user_by_employee_id(self, tenant_id: UUID, employee_id: str) -> User | None:
        result = await self.session.execute(select(User).where(User.tenant_id == tenant_id, User.employee_id == employee_id))
        return result.scalar_one_or_none()

    async def list_users(self, tenant_id: UUID, filters: dict[str, Any] | None = None) -> list[User]:
        statement = select(User).where(User.tenant_id == tenant_id)
        if filters:
            if organization_id := filters.get("organization_id"):
                statement = statement.where(User.organization_id == organization_id)
            if department_id := filters.get("department_id"):
                statement = statement.where(User.department_id == department_id)
            if team_id := filters.get("team_id"):
                statement = statement.where(User.team_id == team_id)
            if status := filters.get("status"):
                statement = statement.where(User.status == status)
            if search := filters.get("search"):
                statement = statement.where(or_(User.display_name.ilike(f"%{search}%"), User.email.ilike(f"%{search}%"), User.username.ilike(f"%{search}%")))
        result = await self.session.execute(statement.order_by(User.display_name.asc()))
        return list(result.scalars().all())

    async def create_user(self, user: User) -> User:
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_user(self, user: User, values: dict[str, Any]) -> User:
        for key, value in values.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self.session.flush()
        return user

    async def delete_user(self, user: User) -> None:
        await self.session.delete(user)

    async def get_profile(self, user_id: UUID) -> UserProfile | None:
        result = await self.session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        return result.scalar_one_or_none()

    async def upsert_profile(self, profile: UserProfile) -> UserProfile:
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def get_preferences(self, user_id: UUID) -> UserPreference | None:
        result = await self.session.execute(select(UserPreference).where(UserPreference.user_id == user_id))
        return result.scalar_one_or_none()

    async def upsert_preferences(self, preferences: UserPreference) -> UserPreference:
        self.session.add(preferences)
        await self.session.flush()
        return preferences

    async def get_employee(self, user_id: UUID) -> Employee | None:
        result = await self.session.execute(select(Employee).where(Employee.user_id == user_id))
        return result.scalar_one_or_none()

    async def upsert_employee(self, employee: Employee) -> Employee:
        self.session.add(employee)
        await self.session.flush()
        return employee

    async def get_directory_entry(self, tenant_id: UUID, entity_type: str, entity_id: UUID) -> Directory | None:
        result = await self.session.execute(select(Directory).where(Directory.tenant_id == tenant_id, Directory.entity_type == entity_type, Directory.entity_id == entity_id))
        return result.scalar_one_or_none()

    async def upsert_directory_entry(self, entry: Directory) -> Directory:
        self.session.add(entry)
        await self.session.flush()
        return entry

    async def delete_directory_entry(self, tenant_id: UUID, entity_type: str, entity_id: UUID) -> int:
        result = await self.session.execute(delete(Directory).where(Directory.tenant_id == tenant_id, Directory.entity_type == entity_type, Directory.entity_id == entity_id))
        await self.session.flush()
        return int(result.rowcount or 0)

    async def search_directory(self, tenant_id: UUID, filters: dict[str, Any] | None = None) -> list[Directory]:
        statement = select(Directory).where(Directory.tenant_id == tenant_id)
        if filters:
            if entity_type := filters.get("entity_type"):
                statement = statement.where(Directory.entity_type == entity_type)
            if status := filters.get("status"):
                statement = statement.where(Directory.status == status)
            if search := filters.get("search"):
                statement = statement.where(
                    or_(
                        Directory.display_name.ilike(f"%{search}%"),
                        Directory.email.ilike(f"%{search}%"),
                        Directory.organization_name.ilike(f"%{search}%"),
                        Directory.department_name.ilike(f"%{search}%"),
                        Directory.team_name.ilike(f"%{search}%"),
                    )
                )
        result = await self.session.execute(statement.order_by(Directory.display_name.asc()))
        return list(result.scalars().all())

    async def list_user_roles(self, user_id: UUID) -> list[Role]:
        result = await self.session.execute(select(Role).join(UserRole, UserRole.role_id == Role.id).where(UserRole.user_id == user_id))
        return list(result.scalars().unique().all())

