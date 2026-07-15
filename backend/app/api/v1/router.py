from __future__ import annotations

from fastapi import APIRouter

from app.executive.controllers.router import router as executive_router
from app.core.settings import get_settings


router = APIRouter(prefix="/api/v1", tags=["api-v1"])


@router.get("/status")
async def version_status() -> dict[str, object]:
    settings = get_settings()
    return {
        "service": settings.app_name,
        "version": "1.0.0",
        "environment": settings.environment.value,
        "status": "ok",
    }


router.include_router(executive_router)
