from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import uuid4

from redis.asyncio import Redis

from app.core.settings import AppSettings
from app.knowledge.vectorstore.qdrant_store import QdrantVectorStore, VectorPoint
from app.grc.engine import GRCGraphBackend, GRCIntelligenceEngine
from app.grc.models import AIGovernanceRecord, Assessment, Audit, ComplianceReport, Control, Evidence, Finding, Framework, Policy, PolicyVersion, RiskRegister
from app.grc.repositories.grc_repository import GRCRepository
from app.grc.schemas import (
    AIGovernanceResponse,
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
    FrameworkCreateRequest,
    FrameworkResponse,
    PolicyCreateRequest,
    PolicyResponse,
    PolicyUpdateRequest,
    RiskRegisterResponse,
    RiskCategory,
)
from app.grc.validators import clamp_score, normalize_codes


def _now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class GRCService:
    repository: GRCRepository
    settings: AppSettings
    redis_client: Redis | None = None
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger("grc"))
    engine: GRCIntelligenceEngine = field(init=False, repr=False)
    graph_backend: GRCGraphBackend = field(init=False, repr=False)
    vector_store: QdrantVectorStore = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.engine = GRCIntelligenceEngine(self.settings)
        self.graph_backend = GRCGraphBackend()
        self.vector_store = QdrantVectorStore(self.settings)
        self._seed_reference_data()

    async def frameworks(self) -> list[FrameworkResponse]:
        cached = await self._cache_get("frameworks")
        if cached:
            return [FrameworkResponse.model_validate(item) for item in cached]
        frameworks = await self.repository.list_frameworks()
        if not frameworks:
            frameworks = [await self.repository.add_framework(self._framework_model(item)) for item in self.engine.framework_catalog()]
        response = [self._framework_response(framework) for framework in frameworks]
        await self._cache_set("frameworks", [item.model_dump(mode="json") for item in response], self.settings.grc_cache_ttl_seconds)
        return response

    async def policies(self) -> list[PolicyResponse]:
        cached = await self._cache_get("policies")
        if cached:
            return [PolicyResponse.model_validate(item) for item in cached]
        response = [self._policy_response(policy) for policy in await self.repository.list_policies()]
        await self._cache_set("policies", [item.model_dump(mode="json") for item in response], self.settings.grc_cache_ttl_seconds)
        return response

    async def create_policy(self, request: PolicyCreateRequest) -> PolicyResponse:
        policy = Policy(
            code=request.code,
            name=request.name,
            category=request.category.value,
            description=request.description,
            status=request.status,
            version_label=request.version_label,
            owner=request.owner,
            approval_status=request.approval_status.value,
            frameworks=normalize_codes(request.frameworks),
            rules=request.rules,
            exceptions=request.exceptions,
            enforcement_metadata=request.enforcement_metadata,
            policy_metadata=request.metadata,
        )
        await self.repository.add_policy(policy)
        await self.repository.add_policy_version(PolicyVersion(policy_code=policy.code, version_label=policy.version_label, change_summary="Initial policy version", status=policy.status, approved_by=policy.owner, version_metadata={"frameworks": policy.frameworks}))
        self._graph_policy(policy)
        await self._cache_delete("policies")
        return self._policy_response(policy)

    async def update_policy(self, policy_id: str, request: PolicyUpdateRequest) -> PolicyResponse:
        policy = await self._get_policy_or_raise(policy_id)
        before = self._policy_response(policy)
        if request.name is not None:
            policy.name = request.name
        if request.category is not None:
            policy.category = request.category.value
        if request.description is not None:
            policy.description = request.description
        if request.status is not None:
            policy.status = request.status
        if request.version_label is not None:
            policy.version_label = request.version_label
        if request.owner is not None:
            policy.owner = request.owner
        if request.approval_status is not None:
            policy.approval_status = request.approval_status.value
        if request.frameworks is not None:
            policy.frameworks = normalize_codes(request.frameworks)
        if request.rules is not None:
            policy.rules = request.rules
        if request.exceptions is not None:
            policy.exceptions = request.exceptions
        if request.enforcement_metadata is not None:
            policy.enforcement_metadata = request.enforcement_metadata
        if request.metadata is not None:
            policy.policy_metadata = request.metadata
        await self.repository.add_policy_version(PolicyVersion(policy_code=policy.code, version_label=policy.version_label, change_summary="Policy updated", status=policy.status, approved_by=policy.owner, version_metadata={"before": before.model_dump(mode="json")}))
        await self._cache_delete("policies")
        return self._policy_response(policy)

    async def controls(self) -> list[ControlResponse]:
        response = [self._control_response(control) for control in await self.repository.list_controls()]
        return response

    async def create_control(self, request: ControlCreateRequest) -> ControlResponse:
        control = Control(
            code=request.code,
            name=request.name,
            category=request.category.value,
            control_type=request.control_type.value,
            owner=request.owner,
            maturity=request.maturity,
            status=request.status,
            version_label=request.version_label,
            frameworks=normalize_codes(request.frameworks),
            dependencies=normalize_codes(request.dependencies),
            evidence_requirements=request.evidence_requirements,
            testing=request.testing,
            control_metadata=request.metadata,
        )
        await self.repository.add_control(control)
        self._graph_control(control)
        return self._control_response(control)

    async def run_assessment(self, request: AssessmentRunRequest) -> AssessmentResponse:
        frameworks = await self._framework_models(request.frameworks)
        policies = await self._policy_models(request.policy_codes)
        controls = await self._control_models(request.control_codes)
        evidence = await self._evidence_models(request.evidence_codes)
        risks = await self._risk_models(request.risk_codes)
        bundle = self.engine.assessment_bundle(request, [self._framework_snapshot(item) for item in frameworks], [self._policy_snapshot(item) for item in policies], [self._control_snapshot(item) for item in controls], [self._evidence_snapshot(item) for item in evidence], [self._risk_snapshot(item) for item in risks])
        assessment = Assessment(
            assessment_code=request.assessment_code,
            assessment_type=request.assessment_type.value,
            subject_type=request.subject_type,
            subject_id=request.subject_id,
            frameworks=bundle["frameworks"],
            score=bundle["score"],
            confidence=bundle["confidence"],
            coverage=bundle["coverage"],
            evidence_coverage=bundle["coverage"]["evidence"],
            gap_analysis=bundle["gap_analysis"],
            findings=bundle["findings"],
            recommendations=bundle["recommendations"],
            explainability={
                "framework": bundle["framework"],
                "control_mapping": bundle["control_mapping"],
                "evidence": bundle["evidence"],
                "confidence": bundle["confidence"],
                "coverage": bundle["coverage"],
                "gap_analysis": bundle["gap_analysis"],
                "recommendations": bundle["recommendations"],
                "business_impact": bundle["business_impact"],
                "regulatory_impact": bundle["regulatory_impact"],
                "risk_summary": bundle["risk_summary"],
            },
            status="completed",
            assessment_metadata=request.metadata,
        )
        await self.repository.add_assessment(assessment)
        for finding_payload in bundle["findings"]:
            await self.repository.add_finding(Finding(finding_code=finding_payload["finding_code"], severity=finding_payload["severity"], status="open", framework_code=request.frameworks[0] if request.frameworks else None, control_code=request.control_codes[0] if request.control_codes else None, evidence=bundle["evidence"], remediation=bundle["recommendations"], finding_metadata={"gap": finding_payload["gap"]}))
        self._graph_assessment(assessment)
        await self._cache_delete("assessments")
        return self._assessment_response(assessment)

    async def analyze_compliance(self, request: ComplianceAnalyzeRequest) -> ComplianceAnalysisResponse:
        assessment_request = AssessmentRunRequest(
            assessment_code=f"assess-{request.report_code}",
            assessment_type="compliance",
            subject_type=request.subject_type,
            subject_id=request.subject_id,
            frameworks=request.frameworks,
            policy_codes=request.policy_codes,
            control_codes=request.control_codes,
            evidence_codes=request.evidence_codes,
            risk_codes=request.risk_codes,
            ai_model_names=request.ai_model_names,
            metadata=request.metadata,
        )
        assessment_response = await self.run_assessment(assessment_request)
        risks = await self._risk_models(request.risk_codes)
        ai_records = await self.repository.list_ai_governance()
        assessment_payload = assessment_response.model_dump(mode="json")
        assessment_payload["framework"] = assessment_payload["explainability"].get("framework", {})
        assessment_payload["control_mapping"] = assessment_payload["explainability"].get("control_mapping", [])
        assessment_payload["evidence"] = assessment_payload["explainability"].get("evidence", [])
        assessment_payload["business_impact"] = assessment_payload["explainability"].get("business_impact", "")
        assessment_payload["regulatory_impact"] = assessment_payload["explainability"].get("regulatory_impact", "")
        assessment_payload["risk_summary"] = assessment_payload["explainability"].get("risk_summary", {})
        assessment_payload["scorecard"] = {
            "policy_coverage": assessment_payload["coverage"]["policy"]["coverage_score"],
            "framework_coverage": assessment_payload["coverage"]["framework"]["coverage_score"],
            "control_coverage": assessment_payload["coverage"]["control"]["coverage_score"],
            "evidence_coverage": assessment_payload["coverage"]["evidence"]["coverage_score"],
        }
        assessment_payload["open_findings"] = assessment_payload.get("findings", [])
        bundle = self.engine.compliance_bundle(request, assessment_payload, [self._risk_snapshot(item) for item in risks], [self._ai_snapshot(item) for item in ai_records])
        report_bundle = self.engine.report_bundle(request, bundle, assessment_payload, [self._risk_snapshot(item) for item in risks])
        report = ComplianceReport(
            report_code=request.report_code,
            report_type=request.report_type.value,
            subject_type=request.subject_type,
            subject_id=request.subject_id,
            status=report_bundle["status"],
            scorecard=report_bundle["scorecard"],
            framework_coverage=report_bundle["framework_coverage"],
            control_coverage=report_bundle["control_coverage"],
            evidence_summary=report_bundle["evidence_summary"],
            open_findings=report_bundle["open_findings"],
            recommendations=report_bundle["recommendations"],
            report_metadata=request.metadata,
        )
        await self.repository.add_report(report)
        await self.repository.add_risk(RiskRegister(risk_code=f"risk-{request.report_code}", risk_category=RiskCategory.COMPLIANCE.value, owner=request.subject_id, inherent_risk=clamp_score(assessment_response.score), residual_risk=clamp_score(100.0 - bundle["score"]), risk_treatment="mitigate", acceptance_status="open", trend=[{"timestamp": _now(), "risk": bundle["score"]}], history=[{"timestamp": _now(), "event": "compliance-analysis"}], risk_metadata={"frameworks": request.frameworks, "subject_type": request.subject_type}))
        self._graph_report(report)
        await self._cache_delete("reports")
        return ComplianceAnalysisResponse(
            id=report.id or uuid4(),
            report_code=report.report_code,
            report_type=report.report_type,
            subject_type=report.subject_type,
            subject_id=report.subject_id,
            score=bundle["score"],
            confidence=bundle["confidence"],
            frameworks=bundle["frameworks"],
            control_mapping=bundle["control_mapping"],
            evidence=bundle["evidence"],
            coverage=bundle["coverage"],
            gap_analysis=bundle["gap_analysis"],
            recommendations=bundle["recommendations"],
            business_impact=bundle["business_impact"],
            regulatory_impact=bundle["regulatory_impact"],
            open_findings=bundle["open_findings"],
            ai_governance_score=bundle["ai_governance_score"],
            report_id=report.id or uuid4(),
            explainability=assessment_response.explainability,
            created_at=report.created_at or _now(),
            updated_at=report.updated_at or _now(),
        )

    async def reports(self) -> list[ComplianceReportResponse]:
        return [self._report_response(report) for report in await self.repository.list_reports()]

    async def risks(self) -> list[RiskRegisterResponse]:
        return [self._risk_response(risk) for risk in await self.repository.list_risks()]

    async def upload_evidence(self, request: EvidenceUploadRequest) -> EvidenceResponse:
        evidence = Evidence(
            evidence_code=request.evidence_code,
            evidence_type=request.evidence_type.value,
            title=request.title,
            source=request.source,
            classification=request.classification,
            status=request.status,
            storage_ref=request.storage_ref,
            version_number=request.version_number,
            framework_codes=normalize_codes(request.framework_codes),
            control_codes=normalize_codes(request.control_codes),
            expires_at=request.expires_at,
            evidence_metadata=request.metadata,
            validation={"approved": request.status in {"approved", "validated"}, "uploaded_at": _now().isoformat()},
        )
        await self.repository.add_evidence(evidence)
        self._graph_evidence(evidence)
        self._upsert_evidence_vector(evidence)
        await self._cache_delete("evidence")
        return self._evidence_response(evidence)

    async def audits(self) -> list[AuditResponse]:
        return [self._audit_response(audit) for audit in await self.repository.list_audits()]

    async def create_audit(self, request: AuditCreateRequest) -> AuditResponse:
        audit = Audit(audit_code=request.audit_code, audit_type=request.audit_type.value, scope=request.scope, subject_type=request.subject_type, subject_id=request.subject_id, status="planned", checklist=request.checklist, timeline=request.timeline, tasks=request.tasks, findings=request.findings, audit_metadata=request.metadata)
        await self.repository.add_audit(audit)
        self._graph_audit(audit)
        return self._audit_response(audit)

    async def ai_governance(self, model_name: str, provider: str = "ollama", metadata: dict[str, object] | None = None) -> AIGovernanceResponse:
        bundle = self.engine.ai_governance_bundle(model_name, provider, metadata)
        record = AIGovernanceRecord(model_name=bundle["model_name"], model_provider=bundle["model_provider"], approval_status=bundle["approval_status"], prompt_governance=bundle["prompt_governance"], dataset_governance=bundle["dataset_governance"], inference_governance=bundle["inference_governance"], bias_score=bundle["bias_score"], fairness_score=bundle["fairness_score"], transparency_score=bundle["transparency_score"], lifecycle_stage=bundle["lifecycle_stage"], ai_metadata=bundle["metadata"])
        await self.repository.add_ai_governance(record)
        return self._ai_response(record, bundle["explainability"])

    async def _framework_models(self, requested: list[str]) -> list[Framework]:
        frameworks = await self.repository.list_frameworks()
        if not frameworks:
            frameworks = [await self.repository.add_framework(self._framework_model(item)) for item in self.engine.framework_catalog()]
        if not requested:
            return frameworks
        requested_set = set(normalize_codes(requested))
        return [framework for framework in frameworks if framework.code in requested_set]

    async def _policy_models(self, requested: list[str]) -> list[Policy]:
        policies = await self.repository.list_policies()
        if not policies:
            policies = [await self.repository.add_policy(self._policy_model(item)) for item in self.engine.policy_catalog()]
        if not requested:
            return policies
        requested_set = set(normalize_codes(requested))
        return [policy for policy in policies if policy.code in requested_set]

    async def _control_models(self, requested: list[str]) -> list[Control]:
        controls = await self.repository.list_controls()
        if not controls:
            controls = [await self.repository.add_control(self._control_model(item)) for item in self.engine.control_catalog()]
        if not requested:
            return controls
        requested_set = set(normalize_codes(requested))
        return [control for control in controls if control.code in requested_set]

    async def _evidence_models(self, requested: list[str]) -> list[Evidence]:
        evidence = await self.repository.list_evidence()
        if not requested:
            return evidence
        requested_set = set(normalize_codes(requested))
        return [item for item in evidence if item.evidence_code in requested_set]

    async def _risk_models(self, requested: list[str]) -> list[RiskRegister]:
        risks = await self.repository.list_risks()
        if not requested:
            return risks
        requested_set = set(normalize_codes(requested))
        return [item for item in risks if item.risk_code in requested_set]

    def _seed_reference_data(self) -> None:
        if self.repository.frameworks:
            return
        for item in self.engine.framework_catalog():
            self.repository.frameworks.append(self._framework_model(item))
        for item in self.engine.control_catalog():
            self.repository.controls.append(self._control_model(item))
        for item in self.engine.policy_catalog():
            self.repository.policies.append(self._policy_model(item))

    def _framework_model(self, item: dict[str, object]) -> Framework:
        return Framework(code=str(item["code"]), name=str(item["name"]), family=str(item["family"]), version=str(item["version"]), description=str(item["description"]), status=str(item["status"]), control_objectives=list(item["control_objectives"]), regulatory_scope=list(item["regulatory_scope"]), framework_metadata=dict(item["metadata"]))

    def _policy_model(self, item: dict[str, object]) -> Policy:
        return Policy(code=str(item["code"]), name=str(item["name"]), category=str(item["category"]), description=str(item["description"]), status=str(item["status"]), version_label=str(item["version_label"]), owner=str(item["owner"]), approval_status=str(item["approval_status"]), frameworks=list(item["frameworks"]), rules=dict(item["rules"]), exceptions=list(item["exceptions"]), enforcement_metadata=dict(item["enforcement_metadata"]), policy_metadata=dict(item["metadata"]))

    def _control_model(self, item: dict[str, object]) -> Control:
        return Control(code=str(item["code"]), name=str(item["name"]), category=str(item["category"]), control_type=str(item["control_type"]), owner=str(item["owner"]), maturity=int(item["maturity"]), status=str(item["status"]), version_label=str(item["version_label"]), frameworks=list(item["frameworks"]), dependencies=list(item["dependencies"]), evidence_requirements=list(item["evidence_requirements"]), testing=dict(item["testing"]), control_metadata=dict(item["metadata"]))

    def _framework_response(self, framework: Framework) -> FrameworkResponse:
        return FrameworkResponse(id=framework.id or uuid4(), code=framework.code, name=framework.name, family=framework.family, version=framework.version, description=framework.description, status=framework.status, control_objectives=framework.control_objectives, regulatory_scope=framework.regulatory_scope, metadata=framework.framework_metadata, created_at=framework.created_at or _now(), updated_at=framework.updated_at or _now())

    def _policy_response(self, policy: Policy) -> PolicyResponse:
        return PolicyResponse(id=policy.id or uuid4(), code=policy.code, name=policy.name, category=policy.category, description=policy.description, status=policy.status, version_label=policy.version_label, owner=policy.owner, approval_status=policy.approval_status, frameworks=policy.frameworks, rules=policy.rules, exceptions=policy.exceptions, enforcement_metadata=policy.enforcement_metadata, metadata=policy.policy_metadata, created_at=policy.created_at or _now(), updated_at=policy.updated_at or _now())

    def _control_response(self, control: Control) -> ControlResponse:
        return ControlResponse(id=control.id or uuid4(), code=control.code, name=control.name, category=control.category, control_type=control.control_type, owner=control.owner, maturity=control.maturity, status=control.status, version_label=control.version_label, frameworks=control.frameworks, dependencies=control.dependencies, evidence_requirements=control.evidence_requirements, testing=control.testing, metadata=control.control_metadata, created_at=control.created_at or _now(), updated_at=control.updated_at or _now())

    def _assessment_response(self, assessment: Assessment) -> AssessmentResponse:
        return AssessmentResponse(id=assessment.id or uuid4(), assessment_code=assessment.assessment_code, assessment_type=assessment.assessment_type, subject_type=assessment.subject_type, subject_id=assessment.subject_id, frameworks=assessment.frameworks, score=assessment.score, confidence=assessment.confidence, coverage=assessment.coverage, evidence_coverage=assessment.evidence_coverage, gap_analysis=assessment.gap_analysis, findings=assessment.findings, recommendations=assessment.recommendations, explainability=assessment.explainability, status=assessment.status, metadata=assessment.assessment_metadata, created_at=assessment.created_at or _now(), updated_at=assessment.updated_at or _now())

    def _report_response(self, report: ComplianceReport) -> ComplianceReportResponse:
        return ComplianceReportResponse(id=report.id or uuid4(), report_code=report.report_code, report_type=report.report_type, subject_type=report.subject_type, subject_id=report.subject_id, status=report.status, scorecard=report.scorecard, framework_coverage=report.framework_coverage, control_coverage=report.control_coverage, evidence_summary=report.evidence_summary, open_findings=report.open_findings, recommendations=report.recommendations, metadata=report.report_metadata, created_at=report.created_at or _now(), updated_at=report.updated_at or _now())

    def _risk_response(self, risk: RiskRegister) -> RiskRegisterResponse:
        return RiskRegisterResponse(id=risk.id or uuid4(), risk_code=risk.risk_code, risk_category=risk.risk_category, owner=risk.owner, inherent_risk=risk.inherent_risk, residual_risk=risk.residual_risk, risk_treatment=risk.risk_treatment, acceptance_status=risk.acceptance_status, trend=risk.trend, history=risk.history, metadata=risk.risk_metadata, created_at=risk.created_at or _now(), updated_at=risk.updated_at or _now())

    def _evidence_response(self, evidence: Evidence) -> EvidenceResponse:
        return EvidenceResponse(id=evidence.id or uuid4(), evidence_code=evidence.evidence_code, evidence_type=evidence.evidence_type, title=evidence.title, source=evidence.source, classification=evidence.classification, status=evidence.status, storage_ref=evidence.storage_ref, version_number=evidence.version_number, framework_codes=evidence.framework_codes, control_codes=evidence.control_codes, validation=evidence.validation, expires_at=evidence.expires_at, metadata=evidence.evidence_metadata, created_at=evidence.created_at or _now(), updated_at=evidence.updated_at or _now())

    def _audit_response(self, audit: Audit) -> AuditResponse:
        return AuditResponse(id=audit.id or uuid4(), audit_code=audit.audit_code, audit_type=audit.audit_type, scope=audit.scope, subject_type=audit.subject_type, subject_id=audit.subject_id, status=audit.status, checklist=audit.checklist, timeline=audit.timeline, tasks=audit.tasks, findings=audit.findings, metadata=audit.audit_metadata, created_at=audit.created_at or _now(), updated_at=audit.updated_at or _now())

    def _ai_response(self, record: AIGovernanceRecord, explainability: dict[str, object]) -> AIGovernanceResponse:
        return AIGovernanceResponse(id=record.id or uuid4(), model_name=record.model_name, model_provider=record.model_provider, approval_status=record.approval_status, prompt_governance=record.prompt_governance, dataset_governance=record.dataset_governance, inference_governance=record.inference_governance, bias_score=record.bias_score, fairness_score=record.fairness_score, transparency_score=record.transparency_score, lifecycle_stage=record.lifecycle_stage, explainability=explainability, metadata=record.ai_metadata, created_at=record.created_at or _now(), updated_at=record.updated_at or _now())

    def _framework_snapshot(self, framework: Framework) -> dict[str, object]:
        return {"code": framework.code, "name": framework.name, "family": framework.family, "status": framework.status, "metadata": framework.framework_metadata}

    def _policy_snapshot(self, policy: Policy) -> dict[str, object]:
        return {"code": policy.code, "category": policy.category, "status": policy.status, "frameworks": policy.frameworks, "metadata": policy.policy_metadata}

    def _control_snapshot(self, control: Control) -> dict[str, object]:
        return {"code": control.code, "category": control.category, "control_type": control.control_type, "status": control.status, "frameworks": control.frameworks, "metadata": control.control_metadata}

    def _evidence_snapshot(self, evidence: Evidence) -> dict[str, object]:
        return {"evidence_code": evidence.evidence_code, "evidence_type": evidence.evidence_type, "classification": evidence.classification, "status": evidence.status, "framework_codes": evidence.framework_codes, "control_codes": evidence.control_codes, "metadata": evidence.evidence_metadata}

    def _risk_snapshot(self, risk: RiskRegister) -> dict[str, object]:
        return {"risk_code": risk.risk_code, "risk_category": risk.risk_category, "owner": risk.owner, "residual_risk": risk.residual_risk, "trend": risk.trend, "metadata": risk.risk_metadata}

    def _ai_snapshot(self, record: AIGovernanceRecord) -> dict[str, object]:
        return {"model_name": record.model_name, "model_provider": record.model_provider, "approval_status": record.approval_status, "bias_score": record.bias_score, "fairness_score": record.fairness_score, "transparency_score": record.transparency_score, "metadata": record.ai_metadata}

    def _graph_policy(self, policy: Policy) -> None:
        self.graph_backend.add_node(f"policy:{policy.code}", "policy", policy.name, category=policy.category, status=policy.status)
        for framework in policy.frameworks:
            self.graph_backend.add_edge(f"policy:{policy.code}", f"framework:{framework}", "maps_to", 88.0)

    def _graph_control(self, control: Control) -> None:
        self.graph_backend.add_node(f"control:{control.code}", "control", control.name, category=control.category, control_type=control.control_type)
        for framework in control.frameworks:
            self.graph_backend.add_edge(f"control:{control.code}", f"framework:{framework}", "maps_to", 90.0)

    def _graph_assessment(self, assessment: Assessment) -> None:
        self.graph_backend.add_node(f"assessment:{assessment.assessment_code}", "assessment", assessment.assessment_code, subject_id=assessment.subject_id, score=assessment.score)
        self.graph_backend.add_edge(f"assessment:{assessment.assessment_code}", f"subject:{assessment.subject_type}:{assessment.subject_id}", "evaluated_by", 92.0)

    def _graph_report(self, report: ComplianceReport) -> None:
        self.graph_backend.add_node(f"report:{report.report_code}", "report", report.report_code, status=report.status)
        self.graph_backend.add_edge(f"report:{report.report_code}", f"subject:{report.subject_type}:{report.subject_id}", "references", 85.0)

    def _graph_evidence(self, evidence: Evidence) -> None:
        self.graph_backend.add_node(f"evidence:{evidence.evidence_code}", "evidence", evidence.title, evidence_type=evidence.evidence_type, status=evidence.status)
        for control in evidence.control_codes:
            self.graph_backend.add_edge(f"evidence:{evidence.evidence_code}", f"control:{control}", "supports", 84.0)

    def _graph_audit(self, audit: Audit) -> None:
        self.graph_backend.add_node(f"audit:{audit.audit_code}", "audit", audit.audit_code, status=audit.status)
        self.graph_backend.add_edge(f"audit:{audit.audit_code}", f"subject:{audit.subject_type}:{audit.subject_id}", "evaluated_by", 80.0)

    def _upsert_evidence_vector(self, evidence: Evidence) -> None:
        text = " ".join([evidence.title, evidence.source, evidence.classification, evidence.evidence_type])
        vector = [float((sum(ord(char) for char in text) % 97) / 97.0) for _ in range(16)]
        payload = {"evidence_code": evidence.evidence_code, "title": evidence.title, "classification": evidence.classification, "namespace": "grc"}
        self.vector_store.upsert_points("grc-evidence", [VectorPoint(id=evidence.evidence_code, vector=vector, payload=payload)])

    async def _cache_get(self, key: str) -> list[dict[str, object]] | None:
        if self.redis_client is None:
            return None
        cached = await self.redis_client.get(self._cache_key(key))
        return json.loads(cached) if cached else None

    async def _cache_set(self, key: str, payload: list[dict[str, object]], ttl: int) -> None:
        if self.redis_client is None:
            return
        await self.redis_client.set(self._cache_key(key), json.dumps(payload, default=str), ex=ttl)

    async def _cache_delete(self, key: str) -> None:
        if self.redis_client is None:
            return
        await self.redis_client.delete(self._cache_key(key))

    def _cache_key(self, key: str) -> str:
        return f"{self.settings.grc_redis_cache_prefix}:{key}"

    async def _get_policy_or_raise(self, policy_id: str) -> Policy:
        for policy in await self.repository.list_policies():
            if str(policy.id) == str(policy_id) or policy.code == policy_id:
                return policy
        raise ValueError("Policy not found")
