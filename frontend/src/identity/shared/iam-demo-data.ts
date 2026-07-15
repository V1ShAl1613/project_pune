// Static enterprise IAM demo data used by the frontend-only identity framework.
import type { ApiKey, AuditEvent, Group, Invitation, Organization, Permission, Role, ServiceAccount, SessionDevice, SsoProvider, Tenant, TenantWorkspace, User } from "@/types/identity";

export const demoTenants: Tenant[] = [
  { id: "tenant-01", code: "northstar", name: "Northstar Financial", status: "active", configuration: { mfaRequired: true, ssoEnabled: true }, tenantMetadata: { tier: "enterprise" }, activatedAt: "2026-07-01T10:00:00.000Z" },
  { id: "tenant-02", code: "avalon", name: "Avalon Retail", status: "active", configuration: { mfaRequired: true, ssoEnabled: false }, tenantMetadata: { tier: "growth" }, activatedAt: "2026-06-18T10:00:00.000Z" },
];

export const demoOrganizations: Organization[] = [
  { id: "org-01", tenantId: "tenant-01", code: "corp-finance", name: "Corporate Finance", legalName: "Northstar Corporate Finance LLC", description: "Finance and treasury workspace", logoUrl: null, contactEmail: "finance@northstar.example", contactPhone: "+1 (555) 100-2000", status: "active", organizationMetadata: { region: "NA" }, organizationSettings: { billing: "placeholder" } },
  { id: "org-02", tenantId: "tenant-01", code: "global-ops", name: "Global Operations", legalName: "Northstar Global Operations", description: "Operations and procurement", logoUrl: null, contactEmail: "ops@northstar.example", contactPhone: "+1 (555) 100-3000", status: "active", organizationMetadata: { region: "EU" }, organizationSettings: { billing: "placeholder" } },
];

export const demoWorkspaces: TenantWorkspace[] = [
  { id: "ws-01", tenantId: "tenant-01", organizationId: "org-01", name: "Finance Control Plane", code: "finance-cp", status: "active", description: "Executive finance workspace", color: "#0b4458" },
  { id: "ws-02", tenantId: "tenant-01", organizationId: "org-02", name: "Operations Hub", code: "ops-hub", status: "active", description: "Operations and vendors workspace", color: "#2563eb" },
];

export const demoUsers: User[] = [
  { id: "user-01", tenantId: "tenant-01", organizationId: "org-01", departmentId: null, teamId: null, email: "alex@northstar.example", username: "alex.hale", employeeId: "E-1042", designation: "CISO", displayName: "Alex Hale", phoneNumber: "+1 (555) 201-3000", status: "active", profilePictureUrl: null, lastLoginAt: "2026-07-14T08:15:00.000Z", lastActivityAt: "2026-07-14T09:10:00.000Z" },
  { id: "user-02", tenantId: "tenant-01", organizationId: "org-02", departmentId: null, teamId: null, email: "maya@northstar.example", username: "maya.rosen", employeeId: "E-2088", designation: "Workspace Admin", displayName: "Maya Rosen", phoneNumber: "+1 (555) 201-3222", status: "active", profilePictureUrl: null, lastLoginAt: "2026-07-13T15:25:00.000Z", lastActivityAt: "2026-07-14T08:40:00.000Z" },
];

export const demoRoles: Role[] = [
  { id: "role-01", tenantId: "tenant-01", key: "tenant-admin", name: "Tenant Admin", description: "Full tenant administration", color: "#0b4458", priority: 1, status: "active", metadata: { default: true } },
  { id: "role-02", tenantId: "tenant-01", key: "workspace-admin", name: "Workspace Admin", description: "Manages workspace-level access", color: "#2563eb", priority: 2, status: "active", metadata: { default: false } },
  { id: "role-03", tenantId: "tenant-01", key: "auditor", name: "Auditor", description: "Read-only oversight access", color: "#475569", priority: 4, status: "active", metadata: { default: false } },
];

export const demoPermissions: Permission[] = [
  { id: "perm-01", tenantId: "tenant-01", key: "identity:read:users", name: "Read Users", category: "Identity", description: "View user records", effect: "allow" },
  { id: "perm-02", tenantId: "tenant-01", key: "identity:write:roles", name: "Manage Roles", category: "RBAC", description: "Create and edit roles", effect: "allow" },
  { id: "perm-03", tenantId: "tenant-01", key: "identity:read:audit", name: "Read Audit Log", category: "Audit", description: "View audit timeline", effect: "allow" },
  { id: "perm-04", tenantId: "tenant-01", key: "identity:write:apikeys", name: "Manage API Keys", category: "Secrets", description: "Rotate and revoke keys", effect: "allow" },
];

export const demoGroups: Group[] = [
  { id: "group-01", tenantId: "tenant-01", organizationId: "org-01", name: "Finance Leadership", description: "Nested group placeholder", status: "active", isDynamic: false, metadata: { members: 4 } },
  { id: "group-02", tenantId: "tenant-01", organizationId: "org-02", name: "Operations Admins", description: "Dynamic group placeholder", status: "active", isDynamic: true, metadata: { rule: "department == ops" } },
];

export const demoInvitations: Invitation[] = [
  { id: "invite-01", tenantId: "tenant-01", email: "new-analyst@northstar.example", roleName: "Auditor", organizationName: "Corporate Finance", workspaceName: "Finance Control Plane", status: "pending", expiresAt: "2026-07-20T00:00:00.000Z", sentAt: "2026-07-14T07:00:00.000Z" },
  { id: "invite-02", tenantId: "tenant-01", email: "ops-admin@northstar.example", roleName: "Workspace Admin", organizationName: "Global Operations", workspaceName: "Operations Hub", status: "expired", expiresAt: "2026-07-10T00:00:00.000Z", sentAt: "2026-07-03T00:00:00.000Z" },
];

export const demoSessions: SessionDevice[] = [
  { id: "session-01", userId: "user-01", deviceName: "MacBook Pro", browser: "Safari 18", os: "macOS 15", ipAddress: "10.0.1.20", location: "New York, US", status: "current" },
  { id: "session-02", userId: "user-01", deviceName: "iPhone 16", browser: "Safari 18", os: "iOS 18", ipAddress: "10.0.1.21", location: "New York, US", status: "trusted" },
];

export const demoApiKeys: ApiKey[] = [
  { id: "key-01", tenantId: "tenant-01", name: "Finance Reporting", prefix: "sfk_live_1A2B", scopes: ["read:reports", "read:users"], status: "active", expiresAt: "2026-09-01T00:00:00.000Z", lastUsedAt: "2026-07-14T08:00:00.000Z" },
  { id: "key-02", tenantId: "tenant-01", name: "Workspace Sync", prefix: "sfk_live_9Z8Y", scopes: ["read:organizations", "write:workspaces"], status: "rotating", expiresAt: "2026-08-15T00:00:00.000Z", lastUsedAt: "2026-07-13T18:10:00.000Z" },
];

export const demoServiceAccounts: ServiceAccount[] = [
  { id: "svc-01", tenantId: "tenant-01", name: "Automation Runner", description: "Scheduled automation account", status: "active", scopes: ["identity:read", "identity:write:invites"], secretRotation: "Quarterly" },
  { id: "svc-02", tenantId: "tenant-01", name: "Audit Exporter", description: "Read-only export account", status: "active", scopes: ["identity:read:audit"], secretRotation: "Monthly" },
];

export const demoSsoProviders: SsoProvider[] = [
  { id: "sso-01", tenantId: "tenant-01", provider: "Azure AD", connectionName: "northstar-aad", status: "connected", metadataUrl: "https://login.microsoftonline.com/common/federationmetadata/2007-06/federationmetadata.xml", certificateStatus: "valid" },
  { id: "sso-02", tenantId: "tenant-01", provider: "Okta", connectionName: "northstar-okta", status: "testing", metadataUrl: null, certificateStatus: "pending" },
];

export const demoAuditEvents: AuditEvent[] = [
  { id: "audit-01", tenantId: "tenant-01", actor: "Alex Hale", resource: "Role: Tenant Admin", action: "assigned", category: "RBAC", severity: "medium", timestamp: "2026-07-14T08:18:00.000Z", details: "Assigned tenant admin role to Maya Rosen." },
  { id: "audit-02", tenantId: "tenant-01", actor: "System", resource: "API Key: Finance Reporting", action: "rotated", category: "Secrets", severity: "low", timestamp: "2026-07-14T07:55:00.000Z", details: "Rotated key in preparation for expiry." },
];