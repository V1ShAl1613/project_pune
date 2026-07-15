# Security Guide

## Controls

- TLS at the ingress layer
- Security headers at the edge proxy
- Non-root containers
- Deny-by-default network policies
- Secret management through environment and secret objects
- CI secret scanning and dependency scanning
- Runtime health probes and least-privilege service accounts

## Operational requirements

- Rotate secrets before production cutover.
- Enable external certificate management.
- Review container image provenance before deployment.
- Keep database, Redis, Qdrant, Neo4j, and Ollama isolated on private networks.
