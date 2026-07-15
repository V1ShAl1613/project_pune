from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.threat.dependencies import provide_threat_service
from app.threat.schemas import (
    AttackPathAnalyzeRequest,
    AttackPathResponse,
    GraphPathRequest,
    GraphQueryRequest,
    GraphQueryResponse,
    IOCResponse,
    IOCSearchRequest,
    MITREMatrixResponse,
    ThreatAnalysisRequest,
    ThreatAnalysisResponse,
    ThreatCampaignResponse,
    ThreatCorrelateRequest,
    ThreatHuntRequest,
    ThreatHuntResponse,
    ThreatMetricsResponse,
    ThreatActorResponse,
)
from app.threat.services.threat_service import ThreatService


router = APIRouter(tags=["threat-intelligence"])


@router.post("/threats/analyze", response_model=ThreatAnalysisResponse)
async def analyze(payload: ThreatAnalysisRequest, threat_service: ThreatService = Depends(provide_threat_service)) -> ThreatAnalysisResponse:
    return await threat_service.analyze(payload)


@router.post("/threats/correlate", response_model=ThreatAnalysisResponse)
async def correlate(payload: ThreatCorrelateRequest, threat_service: ThreatService = Depends(provide_threat_service)) -> ThreatAnalysisResponse:
    return await threat_service.correlate(payload)


@router.post("/threats/hunt", response_model=ThreatHuntResponse)
async def hunt(payload: ThreatHuntRequest, threat_service: ThreatService = Depends(provide_threat_service)) -> ThreatHuntResponse:
    return await threat_service.hunt(payload)


@router.get("/threats/actors", response_model=list[ThreatActorResponse])
async def actors(threat_service: ThreatService = Depends(provide_threat_service)) -> list[ThreatActorResponse]:
    return await threat_service.list_actors()


@router.get("/threats/campaigns", response_model=list[ThreatCampaignResponse])
async def campaigns(threat_service: ThreatService = Depends(provide_threat_service)) -> list[ThreatCampaignResponse]:
    return await threat_service.list_campaigns()


@router.get("/mitre/matrix", response_model=MITREMatrixResponse)
async def mitre_matrix(query: str | None = None, threat_service: ThreatService = Depends(provide_threat_service)) -> MITREMatrixResponse:
    return await threat_service.mitre_matrix(query=query)


@router.post("/graph/query", response_model=GraphQueryResponse)
async def graph_query(payload: GraphQueryRequest, threat_service: ThreatService = Depends(provide_threat_service)) -> GraphQueryResponse:
    return await threat_service.graph_query(payload)


@router.get("/graph/path")
async def graph_path(source: str = Query(..., min_length=1), target: str = Query(..., min_length=1), threat_service: ThreatService = Depends(provide_threat_service)) -> dict[str, object]:
    return await threat_service.graph_path(GraphPathRequest(source=source, target=target))


@router.get("/iocs", response_model=list[IOCResponse])
async def iocs(threat_service: ThreatService = Depends(provide_threat_service)) -> list[IOCResponse]:
    return await threat_service.list_iocs()


@router.post("/iocs/search", response_model=list[IOCResponse])
async def search_iocs(payload: IOCSearchRequest, threat_service: ThreatService = Depends(provide_threat_service)) -> list[IOCResponse]:
    return await threat_service.search_iocs(payload)


@router.post("/attack-paths/analyze", response_model=AttackPathResponse)
async def analyze_attack_path(payload: AttackPathAnalyzeRequest, threat_service: ThreatService = Depends(provide_threat_service)) -> AttackPathResponse:
    return await threat_service.attack_paths(payload)


@router.get("/threats/metrics", response_model=ThreatMetricsResponse)
async def metrics(threat_service: ThreatService = Depends(provide_threat_service)) -> ThreatMetricsResponse:
    return await threat_service.metrics()
