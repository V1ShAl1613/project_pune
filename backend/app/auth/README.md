# Authentication

This package implements enterprise authentication, identity management, token handling, session tracking, password security, and email notification support for Phase 3.

## Major areas

- `controllers/` exposes the `/auth/*` API surface.
- `services/` contains the authentication workflow orchestration.
- `repositories/` provides identity and token persistence operations.
- `schemas/` contains request and response models.
- `security/` implements password hashing and CSRF helpers.
- `tokens/` handles JWT creation, validation, and Redis-backed tracking.
- `emails/` contains notification templates and SMTP wiring.
- `utils/` contains validation, sanitization, serialization, and device metadata helpers.
