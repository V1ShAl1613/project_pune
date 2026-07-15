# Sentinel Fusion AI Backend

Phase 1 establishes the FastAPI backend foundation for Sentinel Fusion AI.

## What is included

- Typed FastAPI application factory
- Pydantic v2 settings and environment loading
- SQLAlchemy 2 async database foundation with Alembic
- Redis connection management and health checks
- Middleware for correlation IDs, logging, timing, security headers, compression, and trusted hosts
- Structured JSON logging and audit logging skeleton
- Root, health, readiness, metrics, and versioned API endpoints
- Pytest scaffolding for configuration and health checks

## Run locally

1. Install dependencies with Poetry.
2. Copy `.env.example` to `.env` and set environment values.
3. Start the API with `uvicorn app.main:app --reload` from the `backend/` directory.

## Documentation layout

- `app/` contains the application package.
- `alembic/` contains migration configuration.
- `tests/` contains backend verification tests.
- `scripts/` contains local helper scripts.
