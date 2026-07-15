from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from app.core.settings import AppSettings, get_settings


@dataclass(slots=True)
class BackupService:
    """Builds and optionally executes PostgreSQL backup commands."""

    settings: AppSettings = field(default_factory=get_settings)

    def build_command(self, output_path: Path) -> list[str]:
        return [
            "pg_dump",
            "--format=custom",
            "--no-owner",
            "--no-privileges",
            f"--file={output_path}",
            self.settings.database_url,
        ]

    def backup(self, output_path: Path, execute: bool = False) -> list[str]:
        command = self.build_command(output_path)
        if execute:
            subprocess.run(command, check=True)
        return command
