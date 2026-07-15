from __future__ import annotations

from fastapi import APIRouter, Depends

from app.reasoning.dependencies import provide_reasoning_service
from app.reasoning.schemas import (
    ConfidenceResponse,
    DecisionValidationResponse,
    EvaluationRunResponse,
    QuantumRiskProjectionResponse,
    ReasoningAnalysisResponse,
    ReasoningEvaluateRequest,
    ReasoningMetricsResponse,
    ReasoningRequest,
    ReasoningValidateRequest,
    RecommendationResponse,
    RiskAnalyzeRequest,
    RiskAssessmentResponse,
    RiskProjectRequest,
    TrustResponse,
)
from app.reasoning.services.reasoning_service import ReasoningService


router = APIRouter(prefix="/reasoning", tags=["reasoning"])


@router.post("/analyze", response_model=ReasoningAnalysisResponse)
async def analyze(payload: ReasoningRequest, reasoning_service: ReasoningService = Depends(provide_reasoning_service)) -> ReasoningAnalysisResponse:
    return await reasoning_service.analyze(payload)


@router.post("/validate", response_model=DecisionValidationResponse)
async def validate(payload: ReasoningValidateRequest, reasoning_service: ReasoningService = Depends(provide_reasoning_service)) -> DecisionValidationResponse:
    return await reasoning_service.validate(payload)


@router.post("/explain", response_model=ReasoningAnalysisResponse)
async def explain(payload: ReasoningRequest, reasoning_service: ReasoningService = Depends(provide_reasoning_service)) -> ReasoningAnalysisResponse:
    return await reasoning_service.explain(payload)


@router.post("/evaluate", response_model=EvaluationRunResponse)
async def evaluate(payload: ReasoningEvaluateRequest, reasoning_service: ReasoningService = Depends(provide_reasoning_service)) -> EvaluationRunResponse:
    return await reasoning_service.evaluate(payload)


@router.post("/risk/analyze", response_model=RiskAssessmentResponse)
async def risk_analyze(payload: RiskAnalyzeRequest, reasoning_service: ReasoningService = Depends(provide_reasoning_service)) -> RiskAssessmentResponse:
    return await reasoning_service.risk_analyze(payload)


@router.post("/risk/project", response_model=QuantumRiskProjectionResponse)
async def risk_project(payload: RiskProjectRequest, reasoning_service: ReasoningService = Depends(provide_reasoning_service)) -> QuantumRiskProjectionResponse:
    return await reasoning_service.risk_project(payload)


@router.get("/recommendations", response_model=list[RecommendationResponse])
async def recommendations(reasoning_service: ReasoningService = Depends(provide_reasoning_service)) -> list[RecommendationResponse]:
    return await reasoning_service.recommendations()


@router.get("/confidence", response_model=list[ConfidenceResponse])
async def confidence(reasoning_service: ReasoningService = Depends(provide_reasoning_service)) -> list[ConfidenceResponse]:
    return await reasoning_service.confidence()


@router.get("/trust", response_model=list[TrustResponse])
async def trust(reasoning_service: ReasoningService = Depends(provide_reasoning_service)) -> list[TrustResponse]:
    return await reasoning_service.trust()


@router.get("/evaluations", response_model=list[EvaluationRunResponse])
async def evaluations(reasoning_service: ReasoningService = Depends(provide_reasoning_service)) -> list[EvaluationRunResponse]:
    return await reasoning_service.evaluations()


@router.get("/metrics", response_model=ReasoningMetricsResponse)
async def metrics(reasoning_service: ReasoningService = Depends(provide_reasoning_service)) -> ReasoningMetricsResponse:
    return await reasoning_service.metrics()
