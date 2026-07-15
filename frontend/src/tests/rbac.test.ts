import { beforeEach, describe, expect, it } from "vitest";

import { sessionStore } from "@/store/session-store";

describe("sessionStore RBAC helpers", () => {
  beforeEach(() => {
    sessionStore.getState().clearSession();
    sessionStore.getState().setRoles([]);
    sessionStore.getState().setPermissions([]);
  });

  it("evaluates access from permission keys", () => {
    sessionStore.getState().setPermissions([{ id: "perm-1", key: "identity:read:users", name: "Read Users", category: "Identity" }]);

    expect(sessionStore.getState().canAccess("identity:read:users")).toBe(true);
    expect(sessionStore.getState().canAccess(["identity:read:users", "identity:write:roles"])).toBe(false);
  });

  it("evaluates roles by key", () => {
    sessionStore.getState().setRoles([{ id: "role-1", key: "tenant-admin", name: "Tenant Admin" }]);

    expect(sessionStore.getState().hasRole("tenant-admin")).toBe(true);
    expect(sessionStore.getState().hasRole("auditor")).toBe(false);
  });
});