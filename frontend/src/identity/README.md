# Identity and Access Management Frontend

This folder contains the UI-only enterprise IAM framework for Sentinel Fusion AI.

## What lives here

- Shared identity page shells
- Permission and role guard helpers
- IAM demo data for static UI states
- Reusable table and list-page primitives
- Icon mappings for authentication, RBAC, sessions, SSO, API keys, and audit surfaces

## Design notes

- Keep all business logic in the backend.
- Use the shared IAM shells for new auth, RBAC, workspace, and administration pages.
- Treat the demo data as presentation-only content.
- Prefer `IdentityTable` for list views and `IdentityPageShell` for detail or dashboard views.