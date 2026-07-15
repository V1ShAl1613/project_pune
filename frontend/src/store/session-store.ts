import { create } from "zustand";
import { persist } from "zustand/middleware";

import type { AuthCapabilities, AuthContextScope, AuthPermission, AuthRole, AuthSessionContext, AuthUser, AuthTokens } from "@/types/auth";

type SessionState = {
  isAuthenticated: boolean;
  accessToken: string | null;
  refreshToken: string | null;
  user: AuthUser | null;
  sessionContext: AuthSessionContext | null;
  roles: AuthRole[];
  permissions: AuthPermission[];
  tenantId: string | null;
  organizationId: string | null;
  workspaceId: string | null;
  departmentId: string | null;
  teamId: string | null;
  setTokens: (tokens: AuthTokens) => void;
  setSession: (user: AuthUser, tokens: AuthTokens) => void;
  setSessionContext: (context: AuthSessionContext | null) => void;
  setContext: (context: AuthContextScope) => void;
  setUser: (user: AuthUser | null) => void;
  setRoles: (roles: AuthRole[]) => void;
  setPermissions: (permissions: AuthPermission[]) => void;
  clearSession: () => void;
  canAccess: AuthCapabilities["canAccess"];
  hasRole: AuthCapabilities["hasRole"];
};

export const sessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      isAuthenticated: false,
      accessToken: null,
      refreshToken: null,
      user: null,
      sessionContext: null,
      roles: [],
      permissions: [],
      tenantId: null,
      organizationId: null,
      workspaceId: null,
      departmentId: null,
      teamId: null,
      setTokens: (tokens) =>
        set({
          isAuthenticated: true,
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken,
        }),
      setSession: (user, tokens) =>
        set({
          isAuthenticated: true,
          user,
          accessToken: tokens.accessToken,
          refreshToken: tokens.refreshToken,
        }),
      setSessionContext: (context) =>
        set({
          sessionContext: context,
          tenantId: context?.tenantId ?? null,
          organizationId: context?.organizationId ?? null,
          workspaceId: context?.workspaceId ?? null,
          departmentId: context?.departmentId ?? null,
          teamId: context?.teamId ?? null,
          roles: context?.roles ?? [],
          permissions: context?.permissions ?? [],
        }),
      setContext: (context) =>
        set({
          tenantId: context.tenantId ?? get().tenantId,
          organizationId: context.organizationId ?? get().organizationId,
          workspaceId: context.workspaceId ?? get().workspaceId,
          departmentId: context.departmentId ?? get().departmentId,
          teamId: context.teamId ?? get().teamId,
        }),
      setUser: (user) => set({ user, isAuthenticated: Boolean(user) }),
      setRoles: (roles) => set({ roles }),
      setPermissions: (permissions) => set({ permissions }),
      clearSession: () =>
        set({
          isAuthenticated: false,
          accessToken: null,
          refreshToken: null,
          user: null,
          sessionContext: null,
          roles: [],
          permissions: [],
          tenantId: null,
          organizationId: null,
          workspaceId: null,
          departmentId: null,
          teamId: null,
        }),
      canAccess: (permissionOrPermissions) => {
        const permissions = get().permissions.map((permission: AuthPermission) => permission.key);
        const requested = Array.isArray(permissionOrPermissions) ? permissionOrPermissions : [permissionOrPermissions];
        return requested.every((permission) => permissions.includes(permission));
      },
      hasRole: (roleKey) => get().roles.some((role: AuthRole) => role.key === roleKey),
    }),
    { name: "sentinel-session" },
  ),
);
