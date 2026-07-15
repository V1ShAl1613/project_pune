from __future__ import annotations

from fastapi import APIRouter

from app.core.settings import get_settings


router = APIRouter(tags=["root"])


@router.get("/")
async def root() -> dict[str, object]:
    settings = get_settings()
    return {
        "service": settings.app_name,
        "environment": settings.environment.value,
        "status": "running",
        "docs": "/docs" if settings.enable_docs else None,
        "openapi": "/openapi.json",
    }
