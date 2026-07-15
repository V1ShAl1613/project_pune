# Enterprise RBAC & Authorization

This document describes the Phase 4 authorization layer for Sentinel Fusion AI.

## Overview

The authorization layer extends the existing authentication system with:

- Role-based access control
- Permission management
- Role hierarchy and inheritance
- Policy evaluation with deny overrides
- Redis-backed authorization caching
- Audit logging for role, permission, and policy events

The implementation lives under `app/authorization/` and reuses the identity models from `app/database/models/identity.py` plus the new authorization tables in `app/database/models/authorization.py`.

## Core Components

- `AuthorizationService` orchestrates role CRUD, permission CRUD, role assignments, permission assignments, policy CRUD, cache invalidation, and audit writes.
- `PermissionEngine` resolves effective permissions for a user by traversing the role hierarchy.
- `PolicyEngine` evaluates active policies and applies deny-overrides before allow decisions.
- `AuthorizationMiddleware` hydrates cached authorization context when a request already has an authenticated user.
- Route decorators enforce access at the endpoint boundary with `RequireRole`, `RequirePermission`, `RequireAnyRole`, `RequireAnyPermission`, and `RequireOwnership`.

## Default Roles

The seeded roles are:

- Super Admin
- Security Admin
- SOC Manager
- SOC Analyst
- Fraud Analyst
- Security Engineer
- Compliance Officer
- Executive
- Auditor
- Read Only

## Permission Matrix

| Permission | Purpose |
|---|---|
| `User.Read` / `User.Write` / `User.Delete` | User administration |
| `Role.Read` / `Role.Write` / `Role.Delete` | Role administration |
| `Audit.Read` / `Audit.Export` | Audit review and export |
| `Dashboard.Read` | Dashboard visibility |
| `Threat.Read` / `Threat.Write` | Threat workflow access |
| `Fraud.Read` / `Fraud.Write` | Fraud workflow access |
| `Report.Read` / `Report.Export` | Reporting access |
| `AI.Read` / `AI.Execute` | Future AI surfaces |
| `Settings.Read` / `Settings.Write` | Platform settings |
| `System.Admin` | Platform administration |

## Role Hierarchy

The inheritance chain is:

```text
Super Admin
  ↓
Security Admin
  ↓
SOC Manager
  ↓
SOC Analyst
  ↓
Read Only
```

Inheritance is resolved automatically during permission evaluation.

## API Endpoints

- `GET /roles`
- `POST /roles`
- `PUT /roles/{id}`
- `DELETE /roles/{id}`
- `GET /permissions`
- `POST /permissions`
- `PUT /permissions/{id}`
- `DELETE /permissions/{id}`
- `POST /users/{id}/roles`
- `DELETE /users/{id}/roles`
- `POST /roles/{id}/permissions`
- `DELETE /roles/{id}/permissions`
- `POST /roles/hierarchy`
- `DELETE /roles/hierarchy`
- `GET /policies`
- `POST /policies`
- `PUT /policies/{id}`
- `DELETE /policies/{id}`
- `GET /permission-groups`
- `POST /permission-groups`
- `PUT /permission-groups/{id}`
- `DELETE /permission-groups/{id}`
- `POST /permission-groups/{id}/permissions`
- `DELETE /permission-groups/{id}/permissions`
- `POST /authorization/evaluate`

## Policy Guide

Policies are stored in PostgreSQL and cached in Redis.

Policy evaluation rules:

1. Policies are sorted by priority.
2. Deny policies override allow policies.
3. Role, permission, user, and any-subject scopes are supported.
4. Authorization decisions are audited.

## Redis Caching

Redis stores:

- effective roles per user
- effective permissions per user
- authorization context snapshots
- policy snapshots

Cache entries are invalidated whenever roles, permissions, hierarchy, or policies change.

## Testing

The RBAC layer is covered by focused tests for:

- role and permission bootstrap
- hierarchy inheritance
- deny-overrides in policy evaluation
- role and permission CRUD
- route protection and decorator enforcement
