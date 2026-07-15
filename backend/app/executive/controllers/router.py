from __future__ import annotations

from fastapi import APIRouter, Depends

from app.executive.dependencies import provide_executive_service
from app.executive.schemas import (
    ExecutiveDecisionResponse,
    ExecutiveForecastResponse,
    ExecutiveKPIResponse,
    ExecutiveOverviewResponse,
    ExecutiveRecommendationResponse,
    ExecutiveReportResponse,
    ExecutiveTrendResponse,
)
from app.executive.services.executive_service import ExecutiveService


router = APIRouter(prefix="/executive", tags=["executive"])


@router.get("/overview", response_model=ExecutiveOverviewResponse)
async def overview(executive_service: ExecutiveService = Depends(provide_executive_service)) -> ExecutiveOverviewResponse:
    return await executive_service.overview()


@router.get("/analytics", response_model=ExecutiveOverviewResponse)
async def analytics(executive_service: ExecutiveService = Depends(provide_executive_service)) -> ExecutiveOverviewResponse:
    return await executive_service.overview()


@router.get("/kpis", response_model=list[ExecutiveKPIResponse])
async def kpis(executive_service: ExecutiveService = Depends(provide_executive_service)) -> list[ExecutiveKPIResponse]:
    return await executive_service.kpis()


@router.get("/trends", response_model=list[ExecutiveTrendResponse])
async def trends(executive_service: ExecutiveService = Depends(provide_executive_service)) -> list[ExecutiveTrendResponse]:
    return await executive_service.trends()


@router.get("/reports", response_model=list[ExecutiveReportResponse])
async def reports(executive_service: ExecutiveService = Depends(provide_executive_service)) -> list[ExecutiveReportResponse]:
    return await executive_service.reports()


@router.get("/reports/{report_code}", response_model=ExecutiveReportResponse)
async def report(report_code: str, executive_service: ExecutiveService = Depends(provide_executive_service)) -> ExecutiveReportResponse:
    return await executive_service.report(report_code)


@router.get("/forecasts", response_model=list[ExecutiveForecastResponse])
async def forecasts(executive_service: ExecutiveService = Depends(provide_executive_service)) -> list[ExecutiveForecastResponse]:
    return await executive_service.forecasts()


@router.get("/recommendations", response_model=list[ExecutiveRecommendationResponse])
async def recommendations(executive_service: ExecutiveService = Depends(provide_executive_service)) -> list[ExecutiveRecommendationResponse]:
    return await executive_service.recommendations()


@router.get("/decisions", response_model=list[ExecutiveDecisionResponse])
async def decisions(executive_service: ExecutiveService = Depends(provide_executive_service)) -> list[ExecutiveDecisionResponse]:
    return await executive_service.decisions()
