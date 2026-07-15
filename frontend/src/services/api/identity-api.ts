import { httpClient } from "@/services/api/http-client";
import type { ApiKey, AuditEvent, Department, Group, Invitation, Organization, PageResult, Permission, Role, ServiceAccount, SessionDevice, SsoProvider, Team, Tenant, TenantWorkspace, User } from "@/types/identity";

type PageParams = {
  page?: number;
  pageSize?: number;
  search?: string;
  status?: string;
  organizationId?: string;
  departmentId?: string;
  teamId?: string;
};

function buildQuery(params: PageParams): string {
  const searchParams = new URLSearchParams();
  if (params.page) searchParams.set("page", String(params.page));
  if (params.pageSize) searchParams.set("page_size", String(params.pageSize));
  if (params.search) searchParams.set("search", params.search);
  if (params.status) searchParams.set("status", params.status);
  if (params.organizationId) searchParams.set("organization_id", params.organizationId);
  if (params.departmentId) searchParams.set("department_id", params.departmentId);
  if (params.teamId) searchParams.set("team_id", params.teamId);
  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

export async function listTenants(): Promise<Tenant[]> {
  const { data } = await httpClient.get("/identity/tenants");
  return data;
}

export async function listOrganizations(params: PageParams = {}): Promise<PageResult<Organization>> {
  const { data } = await httpClient.get(`/identity/organizations${buildQuery(params)}`);
  return data;
}

export async function createOrganization(payload: {
  code: string;
  name: string;
  legalName?: string | null;
  description?: string | null;
  logoUrl?: string | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  organizationMetadata?: Record<string, unknown>;
  organizationSettings?: Record<string, unknown>;
}): Promise<Organization> {
  const { data } = await httpClient.post("/identity/organizations", {
    code: payload.code,
    name: payload.name,
    legal_name: payload.legalName,
    description: payload.description,
    logo_url: payload.logoUrl,
    contact_email: payload.contactEmail,
    contact_phone: payload.contactPhone,
    organization_metadata: payload.organizationMetadata ?? {},
    organization_settings: payload.organizationSettings ?? {},
  });
  return data;
}

export async function listDepartments(params: PageParams = {}): Promise<PageResult<Department>> {
  const { data } = await httpClient.get(`/identity/departments${buildQuery(params)}`);
  return data;
}

export async function createDepartment(payload: {
  organizationId: string;
  code: string;
  name: string;
  status?: string;
  managerUserId?: string | null;
  departmentMetadata?: Record<string, unknown>;
  departmentSettings?: Record<string, unknown>;
}): Promise<Department> {
  const { data } = await httpClient.post("/identity/departments", {
    organization_id: payload.organizationId,
    code: payload.code,
    name: payload.name,
    status: payload.status ?? "active",
    manager_user_id: payload.managerUserId,
    department_metadata: payload.departmentMetadata ?? {},
    department_settings: payload.departmentSettings ?? {},
  });
  return data;
}

export async function listTeams(params: PageParams = {}): Promise<PageResult<Team>> {
  const { data } = await httpClient.get(`/identity/teams${buildQuery(params)}`);
  return data;
}

export async function createTeam(payload: {
  departmentId: string;
  code: string;
  name: string;
  status?: string;
  leadUserId?: string | null;
  teamMetadata?: Record<string, unknown>;
  teamSettings?: Record<string, unknown>;
}): Promise<Team> {
  const { data } = await httpClient.post("/identity/teams", {
    department_id: payload.departmentId,
    code: payload.code,
    name: payload.name,
    status: payload.status ?? "active",
    lead_user_id: payload.leadUserId,
    team_metadata: payload.teamMetadata ?? {},
    team_settings: payload.teamSettings ?? {},
  });
  return data;
}

export async function listUsers(params: PageParams = {}): Promise<PageResult<User>> {
  const { data } = await httpClient.get(`/identity/users${buildQuery(params)}`);
  return data;
}

export async function listRoles(params: PageParams = {}): Promise<PageResult<Role>> {
  const { data } = await httpClient.get(`/identity/roles${buildQuery(params)}`);
  return data;
}

export async function listPermissions(params: PageParams = {}): Promise<PageResult<Permission>> {
  const { data } = await httpClient.get(`/identity/permissions${buildQuery(params)}`);
  return data;
}

export async function listGroups(params: PageParams = {}): Promise<PageResult<Group>> {
  const { data } = await httpClient.get(`/identity/groups${buildQuery(params)}`);
  return data;
}

export async function listInvitations(params: PageParams = {}): Promise<PageResult<Invitation>> {
  const { data } = await httpClient.get(`/identity/invitations${buildQuery(params)}`);
  return data;
}

export async function listSessions(params: PageParams = {}): Promise<PageResult<SessionDevice>> {
  const { data } = await httpClient.get(`/identity/sessions${buildQuery(params)}`);
  return data;
}

export async function listApiKeys(params: PageParams = {}): Promise<PageResult<ApiKey>> {
  const { data } = await httpClient.get(`/identity/api-keys${buildQuery(params)}`);
  return data;
}

export async function listServiceAccounts(params: PageParams = {}): Promise<PageResult<ServiceAccount>> {
  const { data } = await httpClient.get(`/identity/service-accounts${buildQuery(params)}`);
  return data;
}

export async function listSsoProviders(params: PageParams = {}): Promise<PageResult<SsoProvider>> {
  const { data } = await httpClient.get(`/identity/sso/providers${buildQuery(params)}`);
  return data;
}

export async function listAuditEvents(params: PageParams = {}): Promise<PageResult<AuditEvent>> {
  const { data } = await httpClient.get(`/identity/audit${buildQuery(params)}`);
  return data;
}

export async function listTenantWorkspaces(params: PageParams = {}): Promise<PageResult<TenantWorkspace>> {
  const { data } = await httpClient.get(`/identity/workspaces${buildQuery(params)}`);
  return data;
}

export async function createUser(payload: {
  email: string;
  username: string;
  displayName: string;
  status?: string;
  tenantId?: string;
  organizationId?: string | null;
  departmentId?: string | null;
  teamId?: string | null;
  employeeId?: string | null;
  designation?: string | null;
  phoneNumber?: string | null;
  profilePictureUrl?: string | null;
}): Promise<User> {
  const { data } = await httpClient.post("/identity/users", {
    email: payload.email,
    username: payload.username,
    display_name: payload.displayName,
    status: payload.status ?? "active",
    tenant_id: payload.tenantId,
    organization_id: payload.organizationId,
    department_id: payload.departmentId,
    team_id: payload.teamId,
    employee_id: payload.employeeId,
    designation: payload.designation,
    phone_number: payload.phoneNumber,
    profile_picture_url: payload.profilePictureUrl,
  });
  return data;
}

export async function getProfile(userId: string): Promise<unknown> {
  const { data } = await httpClient.get(`/identity/profiles/${userId}`);
  return data;
}

export async function updateProfile(userId: string, payload: Record<string, unknown>): Promise<unknown> {
  const { data } = await httpClient.put(`/identity/profiles/${userId}`, payload);
  return data;
}

export async function getPreferences(userId: string): Promise<unknown> {
  const { data } = await httpClient.get(`/identity/preferences/${userId}`);
  return data;
}

export async function updatePreferences(userId: string, payload: Record<string, unknown>): Promise<unknown> {
  const { data } = await httpClient.put(`/identity/preferences/${userId}`, payload);
  return data;
}

export async function listTenantSettings(): Promise<{ tenants: Tenant[]; organizations: Organization[]; workspaces: TenantWorkspace[] }> {
  const { data } = await httpClient.get("/identity/settings/tenants");
  return data;
}
