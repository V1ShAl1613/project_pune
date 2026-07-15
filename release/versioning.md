# Release Management

Sentinel Fusion AI uses semantic versioning for platform releases.

Rules:

- `MAJOR` for incompatible platform changes
- `MINOR` for new modules or production capabilities
- `PATCH` for hardening, fixes, and operational updates

Release checklist:

- Backend and frontend tests pass
- Container images are built and scanned
- Helm release is rendered successfully
- Smoke tests pass after deployment
- Release notes and deployment metadata are published
