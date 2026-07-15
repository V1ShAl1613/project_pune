from __future__ import annotations

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse

from app.core.settings import AppSettings
from app.database import health as db_health
from app.database.redis import RedisManager
from app.dependencies.providers import provide_redis_manager, provide_session_factory, provide_settings


router = APIRouter(tags=["health"])


@router.get("/health")
async def health(settings: AppSettings = Depends(provide_settings)) -> dict[str, object]:
    return {
        "status": "healthy",
        "service": settings.app_name,
        "environment": settings.environment.value,
    }


@router.get("/ready")
async def ready(
    settings: AppSettings = Depends(provide_settings),
    session_factory=Depends(provide_session_factory),
    redis_manager: RedisManager = Depends(provide_redis_manager),
) -> JSONResponse:
    db_result = await db_health.check_database_health(session_factory)
    redis_result = await db_health.check_redis_health(redis_manager.get_client())
    overall = "ready" if db_result["status"] == "healthy" and redis_result["status"] == "healthy" else "degraded"
    payload = {
        "status": overall,
        "service": settings.app_name,
        "environment": settings.environment.value,
        "checks": {
            "database": db_result,
            "redis": redis_result,
        },
    }
    return JSONResponse(payload, status_code=status.HTTP_200_OK if overall == "ready" else status.HTTP_503_SERVICE_UNAVAILABLE)
