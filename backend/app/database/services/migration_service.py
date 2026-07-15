from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from alembic import command
from alembic.config import Config


@dataclass(slots=True)
class MigrationService:
    """Wraps Alembic commands for local and automated workflows."""

    project_root: Path

    def build_config(self) -> Config:
        config = Config(str(self.project_root / "alembic.ini"))
        config.set_main_option("script_location", str(self.project_root / "alembic"))
        return config

    def upgrade(self, revision: str = "head") -> None:
        command.upgrade(self.build_config(), revision)

    def downgrade(self, revision: str = "-1") -> None:
        command.downgrade(self.build_config(), revision)

    def current(self) -> None:
        command.current(self.build_config())

    def history(self) -> None:
        command.history(self.build_config(), verbose=True)

    def stamp(self, revision: str = "head") -> None:
        command.stamp(self.build_config(), revision)
