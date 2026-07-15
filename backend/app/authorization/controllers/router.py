from uuid import UUID

from fastapi import APIRouter, Depends, Request

from app.auth.dependencies import provide_auth_context
from app.auth.models import AuthContext
from app.authorization.decorators import RequireAnyPermission, RequirePermission, RequireRole
from app.authorization.dependencies import provide_authorization_service
from app.authorization.schemas.authorization import (
    AuthorizationDecisionResponse,
    PermissionAssignmentRequest,
    PermissionCreateRequest,
    PermissionGroupAssignmentRequest,
    PermissionGroupCreateRequest,
    PermissionGroupResponse,
    PermissionGroupUpdateRequest,
    PermissionResponse,
    PermissionUpdateRequest,
    PolicyCreateRequest,
    PolicyResponse,
    PolicyUpdateRequest,
    RoleAssignmentRequest,
    RoleCreateRequest,
    RoleHierarchyRequest,
    RoleResponse,
    RoleUpdateRequest,
)
from app.authorization.services.authorization_service import AuthorizationService


router = APIRouter(tags=["authorization"])


@router.get("/roles", response_model=list[RoleResponse])
@RequirePermission("Role.Read")
async def list_roles(request: Request, authorization_service: AuthorizationService = Depends(provide_authorization_service)):
    return await authorization_service.list_roles()


@router.post("/roles", response_model=RoleResponse)
@RequirePermission("Role.Write")
async def create_role(request: Request, payload: RoleCreateRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await authorization_service.create_role(payload, auth_context)


@router.put("/roles/{role_id}", response_model=RoleResponse)
@RequirePermission("Role.Write")
async def update_role(request: Request, role_id: str, payload: RoleUpdateRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await authorization_service.update_role(UUID(role_id), payload, auth_context)


@router.delete("/roles/{role_id}")
@RequirePermission("Role.Delete")
async def delete_role(request: Request, role_id: str, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.delete_role(UUID(role_id), auth_context)
    return {"message": "Role deleted"}


@router.get("/permissions", response_model=list[PermissionResponse])
@RequirePermission("Role.Read")
async def list_permissions(request: Request, authorization_service: AuthorizationService = Depends(provide_authorization_service)):
    return await authorization_service.list_permissions()


@router.post("/permissions", response_model=PermissionResponse)
@RequirePermission("System.Admin")
async def create_permission(request: Request, payload: PermissionCreateRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await authorization_service.create_permission(payload, auth_context)


@router.put("/permissions/{permission_id}", response_model=PermissionResponse)
@RequirePermission("System.Admin")
async def update_permission(request: Request, permission_id: str, payload: PermissionUpdateRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await authorization_service.update_permission(UUID(permission_id), payload, auth_context)


@router.delete("/permissions/{permission_id}")
@RequirePermission("System.Admin")
async def delete_permission(request: Request, permission_id: str, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.delete_permission(UUID(permission_id), auth_context)
    return {"message": "Permission deleted"}


@router.get("/permission-groups", response_model=list[PermissionGroupResponse])
@RequirePermission("Role.Read")
async def list_permission_groups(request: Request, authorization_service: AuthorizationService = Depends(provide_authorization_service)):
    return await authorization_service.list_permission_groups()


@router.post("/permission-groups", response_model=PermissionGroupResponse)
@RequirePermission("System.Admin")
async def create_permission_group(request: Request, payload: PermissionGroupCreateRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await authorization_service.create_permission_group(payload, auth_context)


@router.put("/permission-groups/{group_id}", response_model=PermissionGroupResponse)
@RequirePermission("System.Admin")
async def update_permission_group(request: Request, group_id: str, payload: PermissionGroupUpdateRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await authorization_service.update_permission_group(UUID(group_id), payload, auth_context)


@router.delete("/permission-groups/{group_id}")
@RequirePermission("System.Admin")
async def delete_permission_group(request: Request, group_id: str, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.delete_permission_group(UUID(group_id), auth_context)
    return {"message": "Permission group deleted"}


@router.post("/permission-groups/{group_id}/permissions")
@RequirePermission("System.Admin")
async def assign_permission_to_group(request: Request, group_id: str, payload: PermissionGroupAssignmentRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.assign_permission_to_group(UUID(group_id), payload, auth_context)
    return {"message": "Permission assigned to group"}


@router.delete("/permission-groups/{group_id}/permissions")
@RequirePermission("System.Admin")
async def revoke_permission_from_group(request: Request, group_id: str, payload: PermissionGroupAssignmentRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.revoke_permission_from_group(UUID(group_id), payload, auth_context)
    return {"message": "Permission removed from group"}


@router.post("/users/{user_id}/roles")
@RequirePermission("Role.Write")
async def assign_role_to_user(request: Request, user_id: str, payload: RoleAssignmentRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.assign_role_to_user(UUID(user_id), payload, auth_context)
    return {"message": "Role assigned to user"}


@router.delete("/users/{user_id}/roles")
@RequirePermission("Role.Delete")
async def revoke_role_from_user(request: Request, user_id: str, payload: RoleAssignmentRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.revoke_role_from_user(UUID(user_id), payload, auth_context)
    return {"message": "Role removed from user"}


@router.post("/roles/{role_id}/permissions")
@RequirePermission("Role.Write")
async def assign_permission_to_role(request: Request, role_id: str, payload: PermissionAssignmentRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.assign_permission_to_role(UUID(role_id), payload, auth_context)
    return {"message": "Permission assigned to role"}


@router.delete("/roles/{role_id}/permissions")
@RequirePermission("Role.Delete")
async def revoke_permission_from_role(request: Request, role_id: str, payload: PermissionAssignmentRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.revoke_permission_from_role(UUID(role_id), payload, auth_context)
    return {"message": "Permission removed from role"}


@router.post("/roles/hierarchy")
@RequirePermission("System.Admin")
async def add_role_hierarchy(request: Request, payload: RoleHierarchyRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.add_role_hierarchy(payload, auth_context)
    return {"message": "Role hierarchy added"}


@router.delete("/roles/hierarchy")
@RequirePermission("System.Admin")
async def remove_role_hierarchy(request: Request, payload: RoleHierarchyRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.remove_role_hierarchy(payload, auth_context)
    return {"message": "Role hierarchy removed"}


@router.get("/policies", response_model=list[PolicyResponse])
@RequirePermission("System.Admin")
async def list_policies(request: Request, authorization_service: AuthorizationService = Depends(provide_authorization_service)):
    return await authorization_service.list_policies()


@router.post("/policies", response_model=PolicyResponse)
@RequirePermission("System.Admin")
async def create_policy(request: Request, payload: PolicyCreateRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await authorization_service.create_policy(payload, auth_context)


@router.put("/policies/{policy_id}", response_model=PolicyResponse)
@RequirePermission("System.Admin")
async def update_policy(request: Request, policy_id: str, payload: PolicyUpdateRequest, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    return await authorization_service.update_policy(UUID(policy_id), payload, auth_context)


@router.delete("/policies/{policy_id}")
@RequirePermission("System.Admin")
async def delete_policy(request: Request, policy_id: str, authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    await authorization_service.delete_policy(UUID(policy_id), auth_context)
    return {"message": "Policy deleted"}


@router.post("/authorization/evaluate", response_model=AuthorizationDecisionResponse)
@RequireAnyPermission("Role.Read", "System.Admin")
async def evaluate_authorization(request: Request, payload: dict[str, str], authorization_service: AuthorizationService = Depends(provide_authorization_service), auth_context: AuthContext = Depends(provide_auth_context)):
    decision = await authorization_service.authorize(
        auth_context,
        resource=payload["resource"],
        action=payload["action"],
        permission_code=payload.get("permission_code"),
    )
    return AuthorizationDecisionResponse(**decision.__dict__)

