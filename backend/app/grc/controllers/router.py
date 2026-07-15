from __future__ import annotations

from fastapi import APIRouter, Depends

from app.grc.dependencies import provide_grc_service
from app.grc.schemas import (
    AssessmentResponse,
    AssessmentRunRequest,
    AuditCreateRequest,
    AuditResponse,
    ComplianceAnalyzeRequest,
    ComplianceAnalysisResponse,
    ComplianceReportResponse,
    ControlCreateRequest,
    ControlResponse,
    EvidenceResponse,
    EvidenceUploadRequest,
    FrameworkResponse,
    PolicyCreateRequest,
    PolicyResponse,
    PolicyUpdateRequest,
    RiskRegisterResponse,
)
from app.grc.services.grc_service import GRCService


router = APIRouter(tags=["grc"])


@router.get("/frameworks", response_model=list[FrameworkResponse])
async def list_frameworks(grc_service: GRCService = Depends(provide_grc_service)) -> list[FrameworkResponse]:
    return await grc_service.frameworks()


@router.get("/policies", response_model=list[PolicyResponse])
async def list_policies(grc_service: GRCService = Depends(provide_grc_service)) -> list[PolicyResponse]:
    return await grc_service.policies()


@router.post("/policies", response_model=PolicyResponse)
async def create_policy(payload: PolicyCreateRequest, grc_service: GRCService = Depends(provide_grc_service)) -> PolicyResponse:
    return await grc_service.create_policy(payload)


@router.put("/policies/{policy_id}", response_model=PolicyResponse)
async def update_policy(policy_id: str, payload: PolicyUpdateRequest, grc_service: GRCService = Depends(provide_grc_service)) -> PolicyResponse:
    return await grc_service.update_policy(policy_id, payload)


@router.get("/controls", response_model=list[ControlResponse])
async def list_controls(grc_service: GRCService = Depends(provide_grc_service)) -> list[ControlResponse]:
    return await grc_service.controls()


@router.post("/controls", response_model=ControlResponse)
async def create_control(payload: ControlCreateRequest, grc_service: GRCService = Depends(provide_grc_service)) -> ControlResponse:
    return await grc_service.create_control(payload)


@router.post("/assessments/run", response_model=AssessmentResponse)
async def run_assessment(payload: AssessmentRunRequest, grc_service: GRCService = Depends(provide_grc_service)) -> AssessmentResponse:
    return await grc_service.run_assessment(payload)


@router.post("/compliance/analyze", response_model=ComplianceAnalysisResponse)
async def analyze_compliance(payload: ComplianceAnalyzeRequest, grc_service: GRCService = Depends(provide_grc_service)) -> ComplianceAnalysisResponse:
    return await grc_service.analyze_compliance(payload)


@router.get("/compliance/reports", response_model=list[ComplianceReportResponse])
async def compliance_reports(grc_service: GRCService = Depends(provide_grc_service)) -> list[ComplianceReportResponse]:
    return await grc_service.reports()


@router.get("/risks", response_model=list[RiskRegisterResponse])
async def list_risks(grc_service: GRCService = Depends(provide_grc_service)) -> list[RiskRegisterResponse]:
    return await grc_service.risks()


@router.post("/evidence/upload", response_model=EvidenceResponse)
async def upload_evidence(payload: EvidenceUploadRequest, grc_service: GRCService = Depends(provide_grc_service)) -> EvidenceResponse:
    return await grc_service.upload_evidence(payload)


@router.get("/audits", response_model=list[AuditResponse])
async def list_audits(grc_service: GRCService = Depends(provide_grc_service)) -> list[AuditResponse]:
    return await grc_service.audits()


@router.post("/audits", response_model=AuditResponse)
async def create_audit(payload: AuditCreateRequest, grc_service: GRCService = Depends(provide_grc_service)) -> AuditResponse:
    return await grc_service.create_audit(payload)
