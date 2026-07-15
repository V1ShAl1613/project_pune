from __future__ import annotations

from fastapi import APIRouter

from app.metrics.collector import metrics_collector


router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def metrics() -> dict[str, object]:
    return metrics_collector.snapshot()
