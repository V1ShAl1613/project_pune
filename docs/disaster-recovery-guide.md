# Disaster Recovery Guide

## Recovery objectives

- Backend and frontend can be restored independently.
- Backing services can be restored from automated backups.
- Executive reporting and decision history can be rebuilt from the latest database snapshot.

## Recovery steps

1. Restore PostgreSQL from the latest backup archive.
2. Restore Redis if session state or caches are part of the recovery objective.
3. Restore Qdrant snapshots for knowledge and vector data.
4. Restore Neo4j and verify graph relationships.
5. Re-deploy the Helm release or manifests.
6. Run smoke tests and confirm readiness checks.

## Validation

- `/health` returns healthy
- `/ready` returns ready
- Executive dashboard loads without errors
- AI and RAG services can reach their backends
