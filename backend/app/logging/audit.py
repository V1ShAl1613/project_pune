from __future__ import annotations

import logging
from typing import Any


def log_audit_event(
    logger: logging.Logger,
    *,
    event_name: str,
    subject: str,
    outcome: str,
    details: dict[str, Any] | None = None,
) -> None:
    logger.info(
        "audit_event",
        extra={
            "event_name": event_name,
            "subject": subject,
            "outcome": outcome,
            "details": details or {},
        },
    )
