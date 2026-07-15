export type PageResult<T> = {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
};

export type Tenant = {
  id: string;
  code: string;
  name: string;
  status: string;
  configuration: Record<string, unknown>;
  tenantMetadata: Record<string, unknown>;
  activatedAt?: string | null;
  suspendedAt?: string | null;
};

export type Organization = {
  id: string;
  tenantId: string;
  code: string;
  name: string;
  legalName?: string | null;
  description?: string | null;
  logoUrl?: string | null;
  contactEmail?: string | null;
  contactPhone?: string | null;
  status: string;
  organizationMetadata: Record<string, unknown>;
  organizationSettings: Record<string, unknown>;
};

export type Department = {
  id: string;
  tenantId: string;
  organizationId: string;
  code: string;
  name: string;
  status: string;
  managerUserId?: string | null;
  departmentMetadata: Record<string, unknown>;
};

export type Team = {
  id: string;
  tenantId: string;
  departmentId: string;
  code: string;
  name: string;
  status: string;
  leadUserId?: string | null;
  teamMetadata: Record<string, unknown>;
};

export type User = {
  id: string;
  tenantId: string;
  organizationId?: string | null;
  departmentId?: string | null;
  teamId?: string | null;
  email: string;
  username: string;
  employeeId?: string | null;
  designation?: string | null;
  displayName: string;
  phoneNumber?: string | null;
  status: string;
  profilePictureUrl?: string | null;
  lastLoginAt?: string | null;
  lastActivityAt?: string | null;
};

export type Role = {
  id: string;
  tenantId: string;
  key: string;
  name: string;
  description?: string | null;
  color?: string | null;
  priority?: number;
  status: string;
  metadata?: Record<string, unknown>;
};

export type Permission = {
  id: string;
  tenantId: string;
  key: string;
  name: string;
  category: string;
  description?: string | null;
  effect?: "allow" | "deny";
  metadata?: Record<string, unknown>;
};

export type Group = {
  id: string;
  tenantId: string;
  organizationId?: string | null;
  name: string;
  description?: string | null;
  status: string;
  isDynamic?: boolean;
  metadata?: Record<string, unknown>;
};

export type Invitation = {
  id: string;
  tenantId: string;
  email: string;
  roleName: string;
  organizationName?: string | null;
  workspaceName?: string | null;
  status: string;
  expiresAt: string;
  sentAt?: string | null;
};

export type SessionDevice = {
  id: string;
  userId: string;
  deviceName: string;
  browser: string;
  os: string;
  ipAddress: string;
  location?: string | null;
  status: string;
};

export type ApiKey = {
  id: string;
  tenantId: string;
  name: string;
  prefix: string;
  scopes: string[];
  status: string;
  expiresAt?: string | null;
  lastUsedAt?: string | null;
};

export type ServiceAccount = {
  id: string;
  tenantId: string;
  name: string;
  description?: string | null;
  status: string;
  scopes: string[];
  secretRotation: string;
};

export type SsoProvider = {
  id: string;
  tenantId: string;
  provider: string;
  connectionName: string;
  status: string;
  metadataUrl?: string | null;
  certificateStatus?: string | null;
};

export type AuditEvent = {
  id: string;
  tenantId: string;
  actor: string;
  resource: string;
  action: string;
  category: string;
  severity: "low" | "medium" | "high" | "critical";
  timestamp: string;
  details?: string | null;
};

export type TenantWorkspace = {
  id: string;
  tenantId: string;
  organizationId?: string | null;
  name: string;
  code: string;
  status: string;
  description?: string | null;
  color?: string | null;
};
