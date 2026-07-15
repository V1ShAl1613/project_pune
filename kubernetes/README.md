# Kubernetes Platform Manifests

This directory contains the standalone Kubernetes manifests for the shared platform services behind Sentinel Fusion AI.

The Helm chart under `helm/sentinel-fusion-ai` deploys the application tier. These manifests provide the backing services and reusable platform primitives:

- PostgreSQL
- Redis
- Qdrant
- Neo4j
- Ollama
- Backup jobs
- Node-level telemetry
