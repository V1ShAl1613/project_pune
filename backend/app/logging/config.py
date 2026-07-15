from __future__ import annotations

import logging

from app.core.settings import AppSettings
from app.logging.formatters import JsonLogFormatter


def configure_logging(settings: AppSettings) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonLogFormatter())

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(settings.log_level.upper())

    logging.getLogger("uvicorn.error").handlers.clear()
    logging.getLogger("uvicorn.access").handlers.clear()


def get_application_logger() -> logging.Logger:
    return logging.getLogger("sentinel.app")


def get_audit_logger() -> logging.Logger:
    return logging.getLogger("sentinel.audit")
