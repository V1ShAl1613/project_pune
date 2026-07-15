from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends

from app.auth.dependencies import provide_auth_context
from app.auth.models import AuthContext
from app.identity.dependencies import provide_identity_service
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
from app.identity.services import IdentityService


router = APIRouter(tags=["identity"])


@router.get("/tenants", response_model=list[TenantResponse])
async def list_tenants(identity_service: IdentityService = Depends(provide_identity_service)):
    return await identity_service.list_tenants()


@router.post("/tenants", response_model=TenantResponse)
async def create_tenant(payload: TenantCreateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.create_tenant(payload, auth_context)


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(tenant_id: UUID, payload: TenantUpdateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.update_tenant(tenant_id, payload, auth_context)


@router.post("/tenants/{tenant_id}/activate", response_model=TenantResponse)
async def activate_tenant(tenant_id: UUID, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.activate_tenant(tenant_id, auth_context)


@router.post("/tenants/{tenant_id}/suspend", response_model=TenantResponse)
async def suspend_tenant(tenant_id: UUID, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.suspend_tenant(tenant_id, auth_context)


@router.get("/organizations", response_model=PageResponse)
async def list_organizations(request: PaginationRequest = Depends(), identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.list_organizations(auth_context, request)


@router.post("/organizations", response_model=OrganizationResponse)
async def create_organization(payload: OrganizationCreateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.create_organization(auth_context, payload)


@router.put("/organizations/{organization_id}", response_model=OrganizationResponse)
async def update_organization(organization_id: UUID, payload: OrganizationUpdateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.update_organization(auth_context, organization_id, payload)


@router.delete("/organizations/{organization_id}")
async def delete_organization(organization_id: UUID, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await identity_service.delete_organization(auth_context, organization_id)
    return {"message": "Organization deleted"}


@router.get("/departments", response_model=PageResponse)
async def list_departments(request: PaginationRequest = Depends(), identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.list_departments(auth_context, request)


@router.post("/departments", response_model=DepartmentResponse)
async def create_department(payload: DepartmentCreateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.create_department(auth_context, payload)


@router.put("/departments/{department_id}", response_model=DepartmentResponse)
async def update_department(department_id: UUID, payload: DepartmentUpdateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.update_department(auth_context, department_id, payload)


@router.delete("/departments/{department_id}")
async def delete_department(department_id: UUID, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await identity_service.delete_department(auth_context, department_id)
    return {"message": "Department deleted"}


@router.get("/teams", response_model=PageResponse)
async def list_teams(request: PaginationRequest = Depends(), identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.list_teams(auth_context, request)


@router.post("/teams", response_model=TeamResponse)
async def create_team(payload: TeamCreateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.create_team(auth_context, payload)


@router.put("/teams/{team_id}", response_model=TeamResponse)
async def update_team(team_id: UUID, payload: TeamUpdateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.update_team(auth_context, team_id, payload)


@router.delete("/teams/{team_id}")
async def delete_team(team_id: UUID, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await identity_service.delete_team(auth_context, team_id)
    return {"message": "Team deleted"}


@router.get("/users", response_model=PageResponse)
async def list_users(request: PaginationRequest = Depends(), identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.list_users(auth_context, request)


@router.post("/users", response_model=UserResponse)
async def create_user(payload: UserCreateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.create_user(auth_context, payload)


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: UUID, payload: UserUpdateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.update_user(auth_context, user_id, payload)


@router.delete("/users/{user_id}")
async def delete_user(user_id: UUID, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await identity_service.delete_user(auth_context, user_id)
    return {"message": "User deleted"}


@router.get("/profiles/{user_id}", response_model=UserProfileResponse)
async def get_profile(user_id: UUID, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.get_profile(auth_context, user_id)


@router.put("/profiles/{user_id}", response_model=UserProfileResponse)
async def update_profile(user_id: UUID, payload: ProfileUpdateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.update_profile(auth_context, user_id, payload)


@router.get("/preferences/{user_id}", response_model=UserPreferenceResponse)
async def get_preferences(user_id: UUID, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.get_preferences(auth_context, user_id)


@router.put("/preferences/{user_id}", response_model=UserPreferenceResponse)
async def update_preferences(user_id: UUID, payload: PreferenceUpdateRequest, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.update_preferences(auth_context, user_id, payload)


@router.get("/employees/{user_id}", response_model=EmployeeResponse)
async def get_employee(user_id: UUID, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.get_employee(auth_context, user_id)


@router.get("/directory/search", response_model=PageResponse)
async def search_directory(request: PaginationRequest = Depends(), entity_type: str | None = None, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.search_directory(auth_context, request, entity_type)


@router.get("/directory/lookup", response_model=DirectoryResponse)
async def lookup_directory(entity_type: str, entity_id: UUID, identity_service: IdentityService = Depends(provide_identity_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await identity_service.lookup_directory(auth_context, entity_type, entity_id)
