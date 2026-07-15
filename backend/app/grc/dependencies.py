from __future__ import annotations

from functools import lru_cache

from fastapi import Request

from app.core.settings import AppSettings, get_settings
from app.grc.repositories.grc_repository import GRCRepository
from app.grc.services.grc_service import GRCService


@lru_cache(maxsize=1)
def _default_repository() -> GRCRepository:
    return GRCRepository()


def provide_grc_service(request: Request) -> GRCService:
    settings = get_settings()
    app_state = getattr(getattr(request, "app", None), "state", None)
    redis_client = getattr(app_state, "redis_client", None) if app_state is not None else None
    return GRCService(repository=_default_repository(), settings=settings, redis_client=redis_client)
