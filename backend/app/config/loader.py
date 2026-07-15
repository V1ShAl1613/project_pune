from __future__ import annotations

import os
from pathlib import Path


def load_environment_file(project_root: Path) -> None:
    env_file = os.environ.get("SENTINEL_ENV_FILE")
    candidates = []
    if env_file:
        candidates.append(Path(env_file))
    candidates.append(project_root / ".env")
    candidates.append(project_root / ".env.local")
    for candidate in candidates:
        if candidate.exists():
            _load_key_value_file(candidate)
            break


def _load_key_value_file(path: Path) -> None:
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
