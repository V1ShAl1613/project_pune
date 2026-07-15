from __future__ import annotations

from uuid import uuid4


def create_correlation_id() -> str:
    return str(uuid4())
