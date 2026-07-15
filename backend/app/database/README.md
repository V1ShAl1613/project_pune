# Database Foundation

Phase 2 adds the enterprise persistence layer for Sentinel Fusion AI.

## Contents

- `base.py` defines the declarative base and naming conventions.
- `connection.py`, `engine.py`, and `session.py` provide engine and session creation.
- `models/` contains the reusable mixins and production tables.
- `repositories/` contains the reusable async repository pattern.
- `services/` contains database lifecycle, migration, seed, backup, restore, and health services.
- `migrations/` contains helper orchestration for seed-on-migrate workflows.
- `seed/` and `fixtures/` contain deterministic data loading assets.

## Design notes

- All tables are defined with explicit constraints and indexes.
- Relationships use ORM back-population and cascade settings where safe.
- Seed data uses natural keys so foreign keys can be resolved deterministically.
- Backup and restore services build PostgreSQL-native commands without embedding credentials.
# Database

This package contains the SQLAlchemy engine, session factory, base model, Redis manager, and health checks.
