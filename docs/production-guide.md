# Production Deployment Guide

## Architecture

Sentinel Fusion AI deploys as a hardened Next.js frontend, a FastAPI backend, and backing services for PostgreSQL, Redis, Qdrant, Neo4j, and Ollama.

## Deployment order

1. Provision the cluster and storage.
2. Apply the backing platform manifests.
3. Deploy the Helm chart for the app tier.
4. Validate health, readiness, and smoke tests.
5. Enable observability, alerting, and backups.

## Runtime checks

- Backend: `/health`, `/ready`, `/metrics`
- Frontend: `/`
- Executive: `/api/v1/executive/overview`

## Rollback

Rollback by reverting the Helm release to the previous image tags and re-running the smoke test suite.
