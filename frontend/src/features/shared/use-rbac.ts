"use client";

// Client hook for reading the current identity context and computing UI-only access gates.
import { useMemo } from "react";

import { sessionStore } from "@/store/session-store";

export function useRBAC() {
  const roles = sessionStore((state) => state.roles);
  const permissions = sessionStore((state) => state.permissions);
  const tenantId = sessionStore((state) => state.tenantId);
  const organizationId = sessionStore((state) => state.organizationId);
  const workspaceId = sessionStore((state) => state.workspaceId);
  const departmentId = sessionStore((state) => state.departmentId);
  const teamId = sessionStore((state) => state.teamId);
  const canAccess = sessionStore((state) => state.canAccess);
  const hasRole = sessionStore((state) => state.hasRole);

  return useMemo(
    () => ({
      roles,
      permissions,
      context: { tenantId, organizationId, workspaceId, departmentId, teamId },
      canAccess,
      hasRole,
      isTenantScoped: Boolean(tenantId),
      isWorkspaceScoped: Boolean(workspaceId),
    }),
    [roles, permissions, tenantId, organizationId, workspaceId, departmentId, teamId, canAccess, hasRole],
  );
}