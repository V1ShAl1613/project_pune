from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from redis.asyncio import Redis

from app.auth.models import AuthContext
from app.core.settings import AppSettings
from app.database.models import Directory, DepartmentSettings, Employee, OrganizationSettings, TeamSettings, Tenant, UserPreference, UserProfile
from app.database.models.identity import User
from app.database.models.organization import Department as DepartmentModel, Organization as OrganizationModel, Team as TeamModel
from app.exceptions.base import AuthorizationApplicationException, BaseApplicationException, ValidationApplicationException
from app.identity.repositories import IdentityRepository
from app.identity.schemas import (
    DepartmentCreateRequest,
    DepartmentResponse,
    DepartmentUpdateRequest,
    DirectoryResponse,
    EmployeeResponse,
    OrganizationCreateRequest,
    OrganizationResponse,
    OrganizationUpdateRequest,
    PageResponse,
    PaginationRequest,
    PreferenceUpdateRequest,
    ProfileUpdateRequest,
    TeamCreateRequest,
    TeamResponse,
    TeamUpdateRequest,
    TenantCreateRequest,
    TenantResponse,
    TenantUpdateRequest,
    UserCreateRequest,
    UserPreferenceResponse,
    UserProfileResponse,
    UserResponse,
    UserUpdateRequest,
)


@dataclass(slots=True)
class IdentityService:
    repository: IdentityRepository
    redis_client: Redis
    settings: AppSettings
    logger: logging.Logger
    audit_logger: logging.Logger

    async def list_tenants(self) -> list[TenantResponse]:
        return [TenantResponse.model_validate(tenant, from_attributes=True) for tenant in await self.repository.list_tenants()]

    async def create_tenant(self, request: TenantCreateRequest, actor: AuthContext | None = None) -> TenantResponse:
        if await self.repository.get_tenant_by_code(request.code) is not None:
            raise BaseApplicationException("Tenant already exists", status_code=409, error_code="tenant_conflict")
        tenant = Tenant(code=request.code, name=request.name, configuration=request.configuration, tenant_metadata=request.tenant_metadata, status="active", activated_at=datetime.now(UTC))
        tenant = await self.repository.create_tenant(tenant)
        await self._audit("tenant_create", "Tenant", str(tenant.id), actor, after=self._snapshot_tenant(tenant))
        await self._invalidate_cache("tenant")
        return TenantResponse.model_validate(tenant, from_attributes=True)

    async def update_tenant(self, tenant_id: UUID, request: TenantUpdateRequest, actor: AuthContext | None = None) -> TenantResponse:
        tenant = await self._get_tenant_or_raise(tenant_id)
        before = self._snapshot_tenant(tenant)
        tenant = await self.repository.update_tenant(tenant, request.model_dump(exclude_none=True))
        await self._audit("tenant_update", "Tenant", str(tenant.id), actor, before=before, after=self._snapshot_tenant(tenant))
        await self._invalidate_cache("tenant")
        return TenantResponse.model_validate(tenant, from_attributes=True)

    async def activate_tenant(self, tenant_id: UUID, actor: AuthContext | None = None) -> TenantResponse:
        return await self.update_tenant(tenant_id, TenantUpdateRequest(status="active"), actor)

    async def suspend_tenant(self, tenant_id: UUID, actor: AuthContext | None = None) -> TenantResponse:
        tenant = await self._get_tenant_or_raise(tenant_id)
        tenant = await self.repository.update_tenant(tenant, {"status": "suspended", "suspended_at": datetime.now(UTC)})
        await self._audit("tenant_suspend", "Tenant", str(tenant.id), actor, after=self._snapshot_tenant(tenant))
        await self._invalidate_cache("tenant")
        return TenantResponse.model_validate(tenant, from_attributes=True)

    async def list_organizations(self, auth_context: AuthContext, request: PaginationRequest) -> PageResponse:
        tenant_id = await self._tenant_for_actor(auth_context)
        organizations = await self.repository.list_organizations(tenant_id, request.model_dump())
        return PageResponse(items=[OrganizationResponse.model_validate(item, from_attributes=True).model_dump() for item in self._page_slice(organizations, request)], total=len(organizations), page=request.page, page_size=request.page_size)

    async def create_organization(self, auth_context: AuthContext, request: OrganizationCreateRequest) -> OrganizationResponse:
        tenant_id = await self._tenant_for_actor(auth_context)
        if await self.repository.get_organization_by_code(tenant_id, request.code) is not None:
            raise BaseApplicationException("Organization already exists", status_code=409, error_code="organization_conflict")
        organization = OrganizationModel(tenant_id=tenant_id, code=request.code, name=request.name, legal_name=request.legal_name, description=request.description, logo_url=request.logo_url, contact_email=request.contact_email, contact_phone=request.contact_phone, organization_metadata=request.organization_metadata, organization_settings=request.organization_settings, status="active")
        organization = await self.repository.create_organization(organization)
        await self._upsert_organization_settings(organization.id, request.organization_settings)
        await self._sync_directory("organization", organization.id, tenant_id, organization.name, None, None, None, organization.status, [])
        await self._audit("organization_create", "Organization", str(organization.id), auth_context, after=self._snapshot_organization(organization))
        await self._invalidate_cache("organization")
        return OrganizationResponse.model_validate(organization, from_attributes=True)

    async def update_organization(self, auth_context: AuthContext, organization_id: UUID, request: OrganizationUpdateRequest) -> OrganizationResponse:
        organization = await self._get_organization_or_raise(auth_context, organization_id)
        before = self._snapshot_organization(organization)
        organization = await self.repository.update_organization(organization, request.model_dump(exclude_none=True))
        if request.organization_settings is not None:
            await self._upsert_organization_settings(organization.id, request.organization_settings)
        await self._sync_directory("organization", organization.id, organization.tenant_id, organization.name, None, None, None, organization.status, [])
        await self._audit("organization_update", "Organization", str(organization.id), auth_context, before=before, after=self._snapshot_organization(organization))
        await self._invalidate_cache("organization")
        return OrganizationResponse.model_validate(organization, from_attributes=True)

    async def delete_organization(self, auth_context: AuthContext, organization_id: UUID) -> None:
        organization = await self._get_organization_or_raise(auth_context, organization_id)
        await self._audit("organization_delete", "Organization", str(organization.id), auth_context, before=self._snapshot_organization(organization))
        await self.repository.delete_organization(organization)
        await self.repository.delete_directory_entry(organization.tenant_id, "organization", organization.id)
        await self._invalidate_cache("organization")

    async def list_departments(self, auth_context: AuthContext, request: PaginationRequest) -> PageResponse:
        tenant_id = await self._tenant_for_actor(auth_context)
        departments = await self.repository.list_departments(tenant_id, request.model_dump())
        return PageResponse(items=[DepartmentResponse.model_validate(item, from_attributes=True).model_dump() for item in self._page_slice(departments, request)], total=len(departments), page=request.page, page_size=request.page_size)

    async def create_department(self, auth_context: AuthContext, request: DepartmentCreateRequest) -> DepartmentResponse:
        organization = await self._get_organization_or_raise(auth_context, request.organization_id)
        tenant_id = await self._tenant_for_actor(auth_context)
        if organization.tenant_id != tenant_id:
            raise AuthorizationApplicationException("Cross-tenant access denied", status_code=403, error_code="tenant_isolation")
        if await self.repository.get_department_by_code(organization.id, request.code) is not None:
            raise BaseApplicationException("Department already exists", status_code=409, error_code="department_conflict")
        department = DepartmentModel(tenant_id=tenant_id, organization_id=organization.id, code=request.code, name=request.name, status=request.status, manager_user_id=request.manager_user_id, department_metadata=request.department_metadata)
        department = await self.repository.create_department(department)
        await self._upsert_department_settings(department.id, request.department_settings)
        await self._sync_directory("department", department.id, tenant_id, department.name, organization.name, None, None, department.status, [])
        await self._audit("department_create", "Department", str(department.id), auth_context, after=self._snapshot_department(department))
        await self._invalidate_cache("department")
        return DepartmentResponse.model_validate(department, from_attributes=True)

    async def update_department(self, auth_context: AuthContext, department_id: UUID, request: DepartmentUpdateRequest) -> DepartmentResponse:
        department = await self._get_department_or_raise(auth_context, department_id)
        before = self._snapshot_department(department)
        department = await self.repository.update_department(department, request.model_dump(exclude_none=True))
        if request.department_settings is not None:
            await self._upsert_department_settings(department.id, request.department_settings)
        organization = await self._get_organization_or_raise(auth_context, department.organization_id)
        await self._sync_directory("department", department.id, department.tenant_id, department.name, organization.name, None, None, department.status, [])
        await self._audit("department_update", "Department", str(department.id), auth_context, before=before, after=self._snapshot_department(department))
        await self._invalidate_cache("department")
        return DepartmentResponse.model_validate(department, from_attributes=True)

    async def delete_department(self, auth_context: AuthContext, department_id: UUID) -> None:
        department = await self._get_department_or_raise(auth_context, department_id)
        await self._audit("department_delete", "Department", str(department.id), auth_context, before=self._snapshot_department(department))
        await self.repository.delete_department(department)
        await self.repository.delete_directory_entry(department.tenant_id, "department", department.id)
        await self._invalidate_cache("department")

    async def list_teams(self, auth_context: AuthContext, request: PaginationRequest) -> PageResponse:
        tenant_id = await self._tenant_for_actor(auth_context)
        teams = await self.repository.list_teams(tenant_id, request.model_dump())
        return PageResponse(items=[TeamResponse.model_validate(item, from_attributes=True).model_dump() for item in self._page_slice(teams, request)], total=len(teams), page=request.page, page_size=request.page_size)

    async def create_team(self, auth_context: AuthContext, request: TeamCreateRequest) -> TeamResponse:
        department = await self._get_department_or_raise(auth_context, request.department_id)
        tenant_id = await self._tenant_for_actor(auth_context)
        if department.tenant_id != tenant_id:
            raise AuthorizationApplicationException("Cross-tenant access denied", status_code=403, error_code="tenant_isolation")
        if await self.repository.get_team_by_code(department.id, request.code) is not None:
            raise BaseApplicationException("Team already exists", status_code=409, error_code="team_conflict")
        team = TeamModel(tenant_id=tenant_id, department_id=department.id, code=request.code, name=request.name, status=request.status, lead_user_id=request.lead_user_id, team_metadata=request.team_metadata)
        team = await self.repository.create_team(team)
        await self._upsert_team_settings(team.id, request.team_settings)
        organization = await self._get_organization_or_raise(auth_context, department.organization_id)
        await self._sync_directory("team", team.id, tenant_id, team.name, organization.name, department.name, None, team.status, [])
        await self._audit("team_create", "Team", str(team.id), auth_context, after=self._snapshot_team(team))
        await self._invalidate_cache("team")
        return TeamResponse.model_validate(team, from_attributes=True)

    async def update_team(self, auth_context: AuthContext, team_id: UUID, request: TeamUpdateRequest) -> TeamResponse:
        team = await self._get_team_or_raise(auth_context, team_id)
        before = self._snapshot_team(team)
        team = await self.repository.update_team(team, request.model_dump(exclude_none=True))
        if request.team_settings is not None:
            await self._upsert_team_settings(team.id, request.team_settings)
        department = await self._get_department_or_raise(auth_context, team.department_id)
        organization = await self._get_organization_or_raise(auth_context, department.organization_id)
        await self._sync_directory("team", team.id, team.tenant_id, team.name, organization.name, department.name, None, team.status, [])
        await self._audit("team_update", "Team", str(team.id), auth_context, before=before, after=self._snapshot_team(team))
        await self._invalidate_cache("team")
        return TeamResponse.model_validate(team, from_attributes=True)

    async def delete_team(self, auth_context: AuthContext, team_id: UUID) -> None:
        team = await self._get_team_or_raise(auth_context, team_id)
        await self._audit("team_delete", "Team", str(team.id), auth_context, before=self._snapshot_team(team))
        await self.repository.delete_team(team)
        await self.repository.delete_directory_entry(team.tenant_id, "team", team.id)
        await self._invalidate_cache("team")

    async def list_users(self, auth_context: AuthContext, request: PaginationRequest) -> PageResponse:
        tenant_id = await self._tenant_for_actor(auth_context)
        users = await self.repository.list_users(tenant_id, request.model_dump())
        return PageResponse(items=[UserResponse.model_validate(item, from_attributes=True).model_dump() for item in self._page_slice(users, request)], total=len(users), page=request.page, page_size=request.page_size)

    async def create_user(self, auth_context: AuthContext, request: UserCreateRequest) -> UserResponse:
        tenant_id = await self._tenant_for_actor(auth_context)
        if request.tenant_id is not None and request.tenant_id != tenant_id:
            raise AuthorizationApplicationException("Cross-tenant access denied", status_code=403, error_code="tenant_isolation")
        if await self.repository.get_user_by_email(tenant_id, request.email) is not None:
            raise BaseApplicationException("Email already exists", status_code=409, error_code="user_conflict")
        if await self.repository.get_user_by_username(tenant_id, request.username) is not None:
            raise BaseApplicationException("Username already exists", status_code=409, error_code="user_conflict")
        if request.employee_id and await self.repository.get_user_by_employee_id(tenant_id, request.employee_id) is not None:
            raise BaseApplicationException("Employee ID already exists", status_code=409, error_code="user_conflict")
        user = User(tenant_id=tenant_id, organization_id=request.organization_id, department_id=request.department_id, team_id=request.team_id, email=request.email, username=request.username, employee_id=request.employee_id, designation=request.designation, display_name=request.display_name, phone_number=request.phone_number, status=request.status, profile_picture_url=request.profile_picture_url, password_hash="", profile={}, authentication_metadata={})
        user = await self.repository.create_user(user)
        await self._ensure_profile_and_preferences(user)
        await self._sync_directory("user", user.id, tenant_id, user.display_name, await self._organization_name(user.organization_id), await self._department_name(user.department_id), await self._team_name(user.team_id), user.status, [role.code for role in await self.repository.list_user_roles(user.id)])
        await self._audit("user_create", "User", str(user.id), auth_context, after=self._snapshot_user(user))
        await self._invalidate_cache("user")
        return UserResponse.model_validate(user, from_attributes=True)

    async def update_user(self, auth_context: AuthContext, user_id: UUID, request: UserUpdateRequest) -> UserResponse:
        user = await self._get_user_or_raise(auth_context, user_id)
        tenant_id = await self._tenant_for_actor(auth_context)
        if user.tenant_id != tenant_id:
            raise AuthorizationApplicationException("Cross-tenant access denied", status_code=403, error_code="tenant_isolation")
        before = self._snapshot_user(user)
        if request.email and request.email != user.email and await self.repository.get_user_by_email(tenant_id, request.email) is not None:
            raise BaseApplicationException("Email already exists", status_code=409, error_code="user_conflict")
        if request.username and request.username != user.username and await self.repository.get_user_by_username(tenant_id, request.username) is not None:
            raise BaseApplicationException("Username already exists", status_code=409, error_code="user_conflict")
        if request.employee_id and request.employee_id != user.employee_id and await self.repository.get_user_by_employee_id(tenant_id, request.employee_id) is not None:
            raise BaseApplicationException("Employee ID already exists", status_code=409, error_code="user_conflict")
        user = await self.repository.update_user(user, request.model_dump(exclude_none=True))
        await self._sync_directory("user", user.id, tenant_id, user.display_name, await self._organization_name(user.organization_id), await self._department_name(user.department_id), await self._team_name(user.team_id), user.status, [role.code for role in await self.repository.list_user_roles(user.id)])
        await self._audit("user_update", "User", str(user.id), auth_context, before=before, after=self._snapshot_user(user))
        await self._invalidate_cache("user")
        return UserResponse.model_validate(user, from_attributes=True)

    async def delete_user(self, auth_context: AuthContext, user_id: UUID) -> None:
        user = await self._get_user_or_raise(auth_context, user_id)
        await self._audit("user_delete", "User", str(user.id), auth_context, before=self._snapshot_user(user))
        await self.repository.delete_user(user)
        await self.repository.delete_directory_entry(user.tenant_id, "user", user.id)
        await self._invalidate_cache("user")

    async def get_profile(self, auth_context: AuthContext, user_id: UUID) -> UserProfileResponse:
        await self._validate_tenant_scope(auth_context, user_id)
        profile = await self.repository.get_profile(user_id)
        if profile is None:
            raise ValidationApplicationException("Profile not found")
        return UserProfileResponse.model_validate(profile, from_attributes=True)

    async def update_profile(self, auth_context: AuthContext, user_id: UUID, request: ProfileUpdateRequest) -> UserProfileResponse:
        user = await self._get_user_or_raise(auth_context, user_id)
        await self._validate_tenant_scope(auth_context, user_id)
        profile = await self.repository.get_profile(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id)
        before = self._snapshot_profile(profile)
        for key, value in request.model_dump(exclude_none=True).items():
            setattr(profile, key, value)
        profile = await self.repository.upsert_profile(profile)
        user.last_activity_at = datetime.now(UTC)
        await self.repository.update_user(user, {"last_activity_at": user.last_activity_at})
        await self._audit("profile_update", "UserProfile", str(user_id), auth_context, before=before, after=self._snapshot_profile(profile))
        await self._invalidate_cache("profile")
        return UserProfileResponse.model_validate(profile, from_attributes=True)

    async def get_preferences(self, auth_context: AuthContext, user_id: UUID) -> UserPreferenceResponse:
        await self._validate_tenant_scope(auth_context, user_id)
        preferences = await self.repository.get_preferences(user_id)
        if preferences is None:
            raise ValidationApplicationException("Preferences not found")
        return UserPreferenceResponse.model_validate(preferences, from_attributes=True)

    async def update_preferences(self, auth_context: AuthContext, user_id: UUID, request: PreferenceUpdateRequest) -> UserPreferenceResponse:
        await self._validate_tenant_scope(auth_context, user_id)
        preferences = await self.repository.get_preferences(user_id)
        if preferences is None:
            preferences = UserPreference(user_id=user_id)
        before = self._snapshot_preferences(preferences)
        for key, value in request.model_dump(exclude_none=True).items():
            setattr(preferences, key, value)
        preferences = await self.repository.upsert_preferences(preferences)
        await self._audit("preference_update", "UserPreference", str(user_id), auth_context, before=before, after=self._snapshot_preferences(preferences))
        await self._invalidate_cache("preference")
        return UserPreferenceResponse.model_validate(preferences, from_attributes=True)

    async def get_employee(self, auth_context: AuthContext, user_id: UUID) -> EmployeeResponse:
        await self._validate_tenant_scope(auth_context, user_id)
        employee = await self.repository.get_employee(user_id)
        if employee is None:
            raise ValidationApplicationException("Employee record not found")
        return EmployeeResponse.model_validate(employee, from_attributes=True)

    async def search_directory(self, auth_context: AuthContext, request: PaginationRequest, entity_type: str | None = None) -> PageResponse:
        tenant_id = await self._tenant_for_actor(auth_context)
        cache_key = self._cache_key("directory", tenant_id, request.search or "", entity_type or "all", request.page, request.page_size)
        cached = await self._read_cache(cache_key)
        if cached is not None:
            return cached
        entries = await self.repository.search_directory(tenant_id, {"search": request.search, "status": request.status, "entity_type": entity_type})
        payload = PageResponse(items=[DirectoryResponse.model_validate(item, from_attributes=True).model_dump() for item in self._page_slice(entries, request)], total=len(entries), page=request.page, page_size=request.page_size)
        await self._write_cache(cache_key, payload)
        await self._audit("directory_search", "Directory", str(tenant_id), auth_context, after={"search": request.search, "entity_type": entity_type})
        return payload

    async def lookup_directory(self, auth_context: AuthContext, entity_type: str, entity_id: UUID) -> DirectoryResponse:
        tenant_id = await self._tenant_for_actor(auth_context)
        entry = await self.repository.get_directory_entry(tenant_id, entity_type, entity_id)
        if entry is None:
            raise ValidationApplicationException("Directory entry not found")
        return DirectoryResponse.model_validate(entry, from_attributes=True)

    async def bootstrap_defaults(self, auth_context: AuthContext) -> TenantResponse | None:
        return None

    async def _tenant_for_actor(self, auth_context: AuthContext) -> UUID:
        user = await self.repository.get_user(auth_context.user_id)
        if user is None:
            raise ValidationApplicationException("Current user not found")
        if user.status not in {"active", "pending_verification", "pending_approval"}:
            raise AuthorizationApplicationException("Account status does not permit access", status_code=403, error_code="account_status")
        return user.tenant_id

    async def _validate_tenant_scope(self, auth_context: AuthContext, user_id: UUID) -> None:
        current_tenant_id = await self._tenant_for_actor(auth_context)
        target_user = await self._get_user_or_raise(auth_context, user_id)
        if target_user.tenant_id != current_tenant_id:
            raise AuthorizationApplicationException("Cross-tenant access denied", status_code=403, error_code="tenant_isolation")

    async def _get_tenant_or_raise(self, tenant_id: UUID) -> Tenant:
        tenant = await self.repository.get_tenant(tenant_id)
        if tenant is None:
            raise ValidationApplicationException("Tenant not found")
        return tenant

    async def _get_organization_or_raise(self, auth_context: AuthContext, organization_id: UUID) -> OrganizationModel:
        organization = await self.repository.get_organization(organization_id)
        if organization is None:
            raise ValidationApplicationException("Organization not found")
        if organization.tenant_id != await self._tenant_for_actor(auth_context):
            raise AuthorizationApplicationException("Cross-tenant access denied", status_code=403, error_code="tenant_isolation")
        return organization

    async def _get_department_or_raise(self, auth_context: AuthContext, department_id: UUID) -> DepartmentModel:
        department = await self.repository.get_department(department_id)
        if department is None:
            raise ValidationApplicationException("Department not found")
        if department.tenant_id != await self._tenant_for_actor(auth_context):
            raise AuthorizationApplicationException("Cross-tenant access denied", status_code=403, error_code="tenant_isolation")
        return department

    async def _get_team_or_raise(self, auth_context: AuthContext, team_id: UUID) -> TeamModel:
        team = await self.repository.get_team(team_id)
        if team is None:
            raise ValidationApplicationException("Team not found")
        if team.tenant_id != await self._tenant_for_actor(auth_context):
            raise AuthorizationApplicationException("Cross-tenant access denied", status_code=403, error_code="tenant_isolation")
        return team

    async def _get_user_or_raise(self, auth_context: AuthContext, user_id: UUID) -> User:
        user = await self.repository.get_user(user_id)
        if user is None:
            raise ValidationApplicationException("User not found")
        if user.tenant_id != await self._tenant_for_actor(auth_context):
            raise AuthorizationApplicationException("Cross-tenant access denied", status_code=403, error_code="tenant_isolation")
        return user

    async def _ensure_profile_and_preferences(self, user: User) -> None:
        if await self.repository.get_profile(user.id) is None:
            await self.repository.upsert_profile(UserProfile(user_id=user.id, phone_number=user.phone_number, profile_picture_url=user.profile_picture_url))
        if await self.repository.get_preferences(user.id) is None:
            await self.repository.upsert_preferences(UserPreference(user_id=user.id, theme="light", language="en", timezone="UTC", dashboard_layout="default"))
        if await self.repository.get_employee(user.id) is None and user.employee_id:
            await self.repository.upsert_employee(Employee(tenant_id=user.tenant_id, user_id=user.id, employee_id=user.employee_id, designation=user.designation, department_id=user.department_id, team_id=user.team_id, employment_status=user.status))

    async def _upsert_organization_settings(self, organization_id: UUID, settings: dict[str, object]) -> None:
        existing = (await self.repository.session.execute(select(OrganizationSettings).where(OrganizationSettings.organization_id == organization_id))).scalar_one_or_none()
        if existing is None:
            existing = OrganizationSettings(organization_id=organization_id, settings=settings)
        else:
            existing.settings = settings
        self.repository.session.add(existing)
        await self.repository.session.flush()

    async def _upsert_department_settings(self, department_id: UUID, settings: dict[str, object]) -> None:
        existing = (await self.repository.session.execute(select(DepartmentSettings).where(DepartmentSettings.department_id == department_id))).scalar_one_or_none()
        if existing is None:
            existing = DepartmentSettings(department_id=department_id, settings=settings)
        else:
            existing.settings = settings
        self.repository.session.add(existing)
        await self.repository.session.flush()

    async def _upsert_team_settings(self, team_id: UUID, settings: dict[str, object]) -> None:
        existing = (await self.repository.session.execute(select(TeamSettings).where(TeamSettings.team_id == team_id))).scalar_one_or_none()
        if existing is None:
            existing = TeamSettings(team_id=team_id, settings=settings)
        else:
            existing.settings = settings
        self.repository.session.add(existing)
        await self.repository.session.flush()

    async def _sync_directory(self, entity_type: str, entity_id: UUID, tenant_id: UUID, display_name: str, organization_name: str | None, department_name: str | None, team_name: str | None, status: str, role_codes: list[str]) -> None:
        entry = await self.repository.get_directory_entry(tenant_id, entity_type, entity_id)
        if entry is None:
            entry = Directory(tenant_id=tenant_id, entity_type=entity_type, entity_id=entity_id, display_name=display_name, organization_name=organization_name, department_name=department_name, team_name=team_name, status=status, role_codes=role_codes)
        else:
            entry.display_name = display_name
            entry.organization_name = organization_name
            entry.department_name = department_name
            entry.team_name = team_name
            entry.status = status
            entry.role_codes = role_codes
        await self.repository.upsert_directory_entry(entry)

    async def _organization_name(self, organization_id: UUID | None) -> str | None:
        if organization_id is None:
            return None
        organization = await self.repository.get_organization(organization_id)
        return organization.name if organization else None

    async def _department_name(self, department_id: UUID | None) -> str | None:
        if department_id is None:
            return None
        department = await self.repository.get_department(department_id)
        return department.name if department else None

    async def _team_name(self, team_id: UUID | None) -> str | None:
        if team_id is None:
            return None
        team = await self.repository.get_team(team_id)
        return team.name if team else None

    def _page_slice(self, items: Sequence[Any], request: PaginationRequest) -> Sequence[Any]:
        start = (request.page - 1) * request.page_size
        return items[start : start + request.page_size]

    async def _invalidate_cache(self, prefix: str) -> None:
        async for key in self.redis_client.scan_iter(match=f"identity:{prefix}:*"):
            await self.redis_client.delete(key)

    def _cache_key(self, *parts: object) -> str:
        return "identity:" + ":".join(str(part) for part in parts)

    async def _write_cache(self, key: str, payload: PageResponse) -> None:
        await self.redis_client.setex(key, 300, payload.model_dump_json())

    async def _read_cache(self, key: str) -> PageResponse | None:
        value = await self.redis_client.get(key)
        if value is None:
            return None
        if isinstance(value, bytes):
            value = value.decode("utf-8")
        return PageResponse.model_validate_json(value)

    async def _audit(self, action: str, entity_type: str, entity_id: str, actor: AuthContext | None, *, before: dict[str, object] | None = None, after: dict[str, object] | None = None) -> None:
        self.audit_logger.info(action, extra={"entity_type": entity_type, "entity_id": entity_id})

    def _snapshot_tenant(self, tenant: Tenant) -> dict[str, object]:
        return {"id": str(tenant.id), "code": tenant.code, "name": tenant.name, "status": tenant.status, "configuration": tenant.configuration, "tenant_metadata": tenant.tenant_metadata}

    def _snapshot_organization(self, organization: OrganizationModel) -> dict[str, object]:
        return {"id": str(organization.id), "tenant_id": str(organization.tenant_id), "code": organization.code, "name": organization.name, "status": organization.status}

    def _snapshot_department(self, department: DepartmentModel) -> dict[str, object]:
        return {"id": str(department.id), "tenant_id": str(department.tenant_id), "organization_id": str(department.organization_id), "code": department.code, "name": department.name, "status": department.status}

    def _snapshot_team(self, team: TeamModel) -> dict[str, object]:
        return {"id": str(team.id), "tenant_id": str(team.tenant_id), "department_id": str(team.department_id), "code": team.code, "name": team.name, "status": team.status}

    def _snapshot_user(self, user: User) -> dict[str, object]:
        return {"id": str(user.id), "tenant_id": str(user.tenant_id), "email": user.email, "username": user.username, "employee_id": user.employee_id, "designation": user.designation, "display_name": user.display_name, "status": user.status}

    def _snapshot_profile(self, profile: UserProfile) -> dict[str, object]:
        return {"user_id": str(profile.user_id), "first_name": profile.first_name, "last_name": profile.last_name, "full_name": profile.full_name, "country": profile.country, "phone_number": profile.phone_number}

    def _snapshot_preferences(self, preferences: UserPreference) -> dict[str, object]:
        return {"user_id": str(preferences.user_id), "theme": preferences.theme, "language": preferences.language, "timezone": preferences.timezone, "dashboard_layout": preferences.dashboard_layout}

