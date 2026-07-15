from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any


def to_json(value: Any) -> str:
    return json.dumps(value, default=_default, separators=(",", ":"))


def from_json(value: str | bytes | None) -> Any:
    if value is None:
        return None
    if isinstance(value, bytes):
        value = value.decode("utf-8")
    return json.loads(value)


def _default(value: Any) -> str:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat()
    raise TypeError(f"Unsupported value: {type(value)!r}")
