from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from app.core.settings import AppSettings, get_settings


@dataclass(slots=True)
class RestoreService:
    """Builds and optionally executes PostgreSQL restore commands."""

    settings: AppSettings = field(default_factory=get_settings)

    def build_command(self, input_path: Path) -> list[str]:
        return [
            "pg_restore",
            "--clean",
            "--if-exists",
            f"--dbname={self.settings.database_url}",
            str(input_path),
        ]

    def restore(self, input_path: Path, execute: bool = False) -> list[str]:
        command = self.build_command(input_path)
        if execute:
            subprocess.run(command, check=True)
        return command
