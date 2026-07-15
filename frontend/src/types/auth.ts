export type AuthTokens = {
  accessToken: string;
  refreshToken: string;
  tokenType: string;
  accessExpiresIn: number;
  refreshExpiresIn: number;
};

export type AuthUser = {
  id: string;
  email: string;
  username: string;
  displayName: string;
  phoneNumber?: string | null;
  status: string;
  emailVerifiedAt?: string | null;
  lastLoginAt?: string | null;
};

export type AuthRole = {
  id: string;
  key: string;
  name: string;
  description?: string | null;
  color?: string | null;
};

export type AuthPermission = {
  id: string;
  key: string;
  name: string;
  category: string;
  description?: string | null;
};

export type AuthContextScope = {
  tenantId?: string | null;
  organizationId?: string | null;
  workspaceId?: string | null;
  departmentId?: string | null;
  teamId?: string | null;
};

export type AuthSessionContext = AuthContextScope & {
  roles: AuthRole[];
  permissions: AuthPermission[];
  rememberMe?: boolean;
  deviceTrust?: "trusted" | "untrusted" | "pending";
  mfaRequired?: boolean;
  authMode?: "jwt" | "cookie" | "session" | "oauth" | "oidc" | "saml";
};

export type AuthSession = {
  id: string;
  status: string;
  sessionToken: string;
  expiresAt: string;
  lastSeenAt?: string | null;
  lastActivityAt?: string | null;
  ipAddress?: string | null;
  userAgent?: string | null;
  deviceId?: string | null;
  deviceName?: string | null;
};

export type AuthCapabilities = {
  canAccess: (permissionOrPermissions: string | string[]) => boolean;
  hasRole: (roleKey: string) => boolean;
  canManageTenant: boolean;
  canManageWorkspace: boolean;
};

export type AuthResponse = {
  user: AuthUser;
  session: AuthSession;
  tokens: AuthTokens;
  message: string;
};

export type RegistrationResponse = {
  user: AuthUser;
  verificationEmailSent: boolean;
  message: string;
};
