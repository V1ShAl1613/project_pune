from __future__ import annotations

from pathlib import Path

from app.database.services.migration_service import MigrationService


def test_migration_service_builds_alembic_config() -> None:
    project_root = Path(__file__).resolve().parents[1]
    service = MigrationService(project_root)

    config = service.build_config()
    assert config.get_main_option("script_location").endswith("alembic")
    assert (project_root / "alembic" / "versions" / "0001_enterprise_database_foundation.py").exists()
