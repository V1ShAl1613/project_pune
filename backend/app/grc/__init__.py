"""Governance, risk, and compliance platform package."""

from app.grc.dependencies import provide_grc_service
from app.grc.services.grc_service import GRCService

__all__ = ["GRCService", "provide_grc_service"]
