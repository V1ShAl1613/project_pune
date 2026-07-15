# Security Hardening Baseline

Security controls for the production release:

- TLS termination at the edge and internal-only service exposure
- Security headers at NGINX and application layer
- Non-root containers with runtime default seccomp
- Network policies with deny-by-default ingress and egress
- Secret values supplied by environment or secret manager, never in source control
- Dependency, secret, and container scanning in CI
- Readiness and liveness probes for all runtime services
- Least-privilege service accounts for workloads
- Backup encryption and restore verification

Secrets must be rotated before production use. The repository only contains templates and operational defaults.
