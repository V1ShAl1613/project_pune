"use client";

// Client guard that hides UI when the current session lacks a required permission or role.
import type { ReactNode } from "react";

import type { AuthCapabilities } from "@/types/auth";
import { useRBAC } from "@/features/shared/use-rbac";

type PermissionGuardProps = {
  permission?: string | string[];
  role?: string | string[];
  fallback?: ReactNode;
  children: ReactNode;
};

export function PermissionGuard({ permission, role, fallback = null, children }: PermissionGuardProps): ReactNode {
  const rbac = useRBAC();
  const allowedByPermission = permission ? rbac.canAccess(permission) : true;
  const allowedByRole = role ? (Array.isArray(role) ? role.some((value) => rbac.hasRole(value)) : rbac.hasRole(role)) : true;

  if (!allowedByPermission || !allowedByRole) {
    return fallback;
  }

  return children;
}

export type { PermissionGuardProps, AuthCapabilities };