from __future__ import annotations

import logging

from app.core.settings import TestingSettings
from app.grc.controllers.router import router as grc_router
from app.grc.dependencies import provide_grc_service
from app.grc.repositories.grc_repository import GRCRepository
from app.grc.schemas import (
    AssessmentRunRequest,
    AuditCreateRequest,
    AuditType,
    ComplianceAnalyzeRequest,
    ControlCreateRequest,
    ControlType,
    EvidenceType,
    FrameworkName,
    PolicyCategory,
    PolicyCreateRequest,
    ReportType,
    RiskCategory,
)
from app.grc.services.grc_service import GRCService


class _FakeGRCService:
    def __init__(self) -> None:
        self.service = GRCService(repository=GRCRepository(), settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))

    async def frameworks(self):
        return await self.service.frameworks()

    async def policies(self):
        return await self.service.policies()

    async def create_policy(self, payload):
        return await self.service.create_policy(payload)

    async def update_policy(self, policy_id, payload):
        return await self.service.update_policy(policy_id, payload)

    async def controls(self):
        return await self.service.controls()

    async def create_control(self, payload):
        return await self.service.create_control(payload)

    async def run_assessment(self, payload):
        return await self.service.run_assessment(payload)

    async def analyze_compliance(self, payload):
        return await self.service.analyze_compliance(payload)

    async def reports(self):
        return await self.service.reports()

    async def risks(self):
        return await self.service.risks()

    async def upload_evidence(self, payload):
        return await self.service.upload_evidence(payload)

    async def audits(self):
        return await self.service.audits()

    async def create_audit(self, payload):
        return await self.service.create_audit(payload)


def test_grc_routes_are_registered(client, app) -> None:
    app.dependency_overrides[provide_grc_service] = lambda: _FakeGRCService()
    try:
        frameworks_response = client.get("/frameworks")
        policy_response = client.post(
            "/policies",
            json={
                "code": "GRC-POL-TEST",
                "name": "Test Governance Policy",
                "category": PolicyCategory.SECURITY.value,
                "description": "Controls security baseline expectations.",
                "frameworks": [FrameworkName.NIST_CSF_2_0.value],
                "rules": {"minimum_approval": "director"},
            },
        )
        control_response = client.post(
            "/controls",
            json={
                "code": "GRC-CTL-TEST",
                "name": "Test Control",
                "category": PolicyCategory.SECURITY.value,
                "control_type": ControlType.TECHNICAL.value,
                "frameworks": [FrameworkName.NIST_SP_800_53.value],
                "evidence_requirements": ["test-evidence"],
            },
        )
        evidence_response = client.post(
            "/evidence/upload",
            json={
                "evidence_code": "GRC-EVD-TEST",
                "evidence_type": EvidenceType.REPORT.value,
                "title": "Quarterly Control Report",
                "source": "grc-suite",
                "classification": "internal",
                "storage_ref": "s3://grc/evidence/report.pdf",
                "framework_codes": [FrameworkName.NIST_CSF_2_0.value],
                "control_codes": ["GRC-CTL-TEST"],
            },
        )
        assessment_response = client.post(
            "/assessments/run",
            json={
                "assessment_code": "GRC-ASSESS-TEST",
                "assessment_type": "compliance",
                "subject_type": "organization",
                "subject_id": "org-1",
                "frameworks": [FrameworkName.NIST_CSF_2_0.value],
                "policy_codes": ["GRC-POL-TEST"],
                "control_codes": ["GRC-CTL-TEST"],
                "evidence_codes": ["GRC-EVD-TEST"],
                "risk_codes": [],
            },
        )
        compliance_response = client.post(
            "/compliance/analyze",
            json={
                "report_code": "GRC-RPT-TEST",
                "report_type": ReportType.EXECUTIVE.value,
                "subject_type": "organization",
                "subject_id": "org-1",
                "frameworks": [FrameworkName.NIST_CSF_2_0.value],
                "policy_codes": ["GRC-POL-TEST"],
                "control_codes": ["GRC-CTL-TEST"],
                "evidence_codes": ["GRC-EVD-TEST"],
                "risk_codes": [],
                "ai_model_names": ["nvidia/nemotron-mini"],
            },
        )
        audit_response = client.post(
            "/audits",
            json={
                "audit_code": "GRC-AUD-TEST",
                "audit_type": AuditType.COMPLIANCE.value,
                "scope": "enterprise-governance",
                "subject_type": "organization",
                "subject_id": "org-1",
                "checklist": ["policy", "control", "evidence"],
            },
        )
    finally:
        app.dependency_overrides.clear()

    assert frameworks_response.status_code == 200
    assert policy_response.status_code == 200
    assert control_response.status_code == 200
    assert evidence_response.status_code == 200
    assert assessment_response.status_code == 200
    assert compliance_response.status_code == 200
    assert audit_response.status_code == 200
    assert frameworks_response.json()[0]["code"]
    assert policy_response.json()["code"] == "GRC-POL-TEST"
    assert control_response.json()["code"] == "GRC-CTL-TEST"
    assert assessment_response.json()["score"] >= 0
    assert compliance_response.json()["score"] >= 0
    assert audit_response.json()["audit_code"] == "GRC-AUD-TEST"


def test_grc_service_end_to_end_flow() -> None:
    service = GRCService(repository=GRCRepository(), settings=TestingSettings(), redis_client=None, logger=logging.getLogger("test"))
    policy = __import__("asyncio").run(
        service.create_policy(
            PolicyCreateRequest(
                code="GRC-POL-0001",
                name="Enterprise Governance Policy",
                category=PolicyCategory.COMPLIANCE,
                frameworks=[FrameworkName.NIST_CSF_2_0.value, FrameworkName.ISO_27001.value],
            )
        )
    )
    control = __import__("asyncio").run(
        service.create_control(
            ControlCreateRequest(
                code="GRC-CTL-0001",
                name="Approval Control",
                category=PolicyCategory.COMPLIANCE,
                control_type=ControlType.ADMINISTRATIVE,
                frameworks=[FrameworkName.NIST_CSF_2_0.value],
                evidence_requirements=["approval trail"],
            )
        )
    )
    evidence = __import__("asyncio").run(
        service.upload_evidence(
            __import__("app.grc.schemas", fromlist=["EvidenceUploadRequest"]).EvidenceUploadRequest(
                evidence_code="GRC-EVD-0001",
                evidence_type=EvidenceType.DOCUMENT,
                title="Board approval memo",
                source="governance",
                storage_ref="memory://board-memo",
                framework_codes=[FrameworkName.ISO_27001.value],
                control_codes=[control.code],
            )
        )
    )
    assessment = __import__("asyncio").run(
        service.run_assessment(
            AssessmentRunRequest(
                assessment_code="GRC-ASSESS-0001",
                subject_type="business_unit",
                subject_id="finance",
                frameworks=[FrameworkName.NIST_CSF_2_0.value, FrameworkName.ISO_27001.value],
                policy_codes=[policy.code],
                control_codes=[control.code],
                evidence_codes=[evidence.evidence_code],
                risk_codes=[],
            )
        )
    )
    compliance = __import__("asyncio").run(
        service.analyze_compliance(
            ComplianceAnalyzeRequest(
                report_code="GRC-RPT-0001",
                report_type=ReportType.REGULATORY_SCORECARD,
                subject_type="business_unit",
                subject_id="finance",
                frameworks=[FrameworkName.NIST_CSF_2_0.value, FrameworkName.ISO_27001.value],
                policy_codes=[policy.code],
                control_codes=[control.code],
                evidence_codes=[evidence.evidence_code],
                ai_model_names=["nvidia/nemotron-mini"],
            )
        )
    )
    audit = __import__("asyncio").run(
        service.create_audit(
            AuditCreateRequest(
                audit_code="GRC-AUD-0001",
                scope="finance-controls",
                subject_type="business_unit",
                subject_id="finance",
            )
        )
    )
    risks = __import__("asyncio").run(service.risks())

    assert policy.code == "GRC-POL-0001"
    assert control.code == "GRC-CTL-0001"
    assert evidence.evidence_code == "GRC-EVD-0001"
    assert assessment.score >= 0
    assert compliance.score >= 0
    assert audit.audit_code == "GRC-AUD-0001"
    assert risks
