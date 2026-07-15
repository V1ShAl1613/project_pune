from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PolicyCategory(StrEnum):
    SECURITY = "security"
    PRIVACY = "privacy"
    AI_GOVERNANCE = "ai_governance"
    CYBERSECURITY = "cybersecurity"
    IDENTITY = "identity"
    INFRASTRUCTURE = "infrastructure"
    CLOUD = "cloud"
    APPLICATION = "application"
    NETWORK = "network"
    DATA_PROTECTION = "data_protection"
    BUSINESS_CONTINUITY = "business_continuity"
    VENDOR_RISK = "vendor_risk"
    INCIDENT_RESPONSE = "incident_response"
    FRAUD = "fraud"
    COMPLIANCE = "compliance"


class ControlType(StrEnum):
    PREVENTIVE = "preventive"
    DETECTIVE = "detective"
    CORRECTIVE = "corrective"
    COMPENSATING = "compensating"
    ADMINISTRATIVE = "administrative"
    TECHNICAL = "technical"
    PHYSICAL = "physical"
    OPERATIONAL = "operational"


class RiskCategory(StrEnum):
    CYBER = "cyber"
    FINANCIAL = "financial"
    OPERATIONAL = "operational"
    CLOUD = "cloud"
    IDENTITY = "identity"
    VENDOR = "vendor"
    AI = "ai"
    INFRASTRUCTURE = "infrastructure"
    DATA = "data"
    COMPLIANCE = "compliance"
    LEGAL = "legal"
    REPUTATIONAL = "reputational"


class FrameworkName(StrEnum):
    NIST_CSF_2_0 = "nist_csf_2_0"
    NIST_SP_800_53 = "nist_sp_800_53"
    NIST_AI_RMF = "nist_ai_rmf"
    OWASP_ASVS = "owasp_asvs"
    OWASP_API_TOP_10 = "owasp_api_top_10"
    OWASP_LLM_TOP_10 = "owasp_llm_top_10"
    MITRE_ATTACK = "mitre_attack"
    MITRE_ATLAS = "mitre_atlas"
    ISO_27001 = "iso_27001"
    ISO_27002 = "iso_27002"
    ISO_42001 = "iso_42001"
    SOC_2 = "soc_2"
    PCI_DSS = "pci_dss"
    CIS_CONTROLS_V8 = "cis_controls_v8"
    COBIT = "cobit"
    GDPR = "gdpr"
    HIPAA = "hipaa"


class ApprovalStatus(StrEnum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class RecordStatus(StrEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    PUBLISHED = "published"
    RETIRED = "retired"
    OPEN = "open"
    CLOSED = "closed"
    MITIGATED = "mitigated"
    ACCEPTED = "accepted"
    OVERDUE = "overdue"


class AssessmentType(StrEnum):
    SECURITY = "security"
    COMPLIANCE = "compliance"
    CONTROL = "control"
    RISK = "risk"
    AI = "ai"
    CLOUD = "cloud"
    IDENTITY = "identity"
    VENDOR = "vendor"


class AuditType(StrEnum):
    PLANNING = "planning"
    OPERATIONS = "operations"
    COMPLIANCE = "compliance"
    AI_GOVERNANCE = "ai_governance"


class EvidenceType(StrEnum):
    POLICY = "policy"
    CONTROL = "control"
    LOG = "log"
    REPORT = "report"
    SCREENSHOT = "screenshot"
    ATTESTATION = "attestation"
    DOCUMENT = "document"
    REVIEW = "review"


class ReportType(StrEnum):
    EXECUTIVE = "executive"
    CONTROL_COVERAGE = "control_coverage"
    FRAMEWORK_COVERAGE = "framework_coverage"
    RISK_SUMMARY = "risk_summary"
    AI_GOVERNANCE = "ai_governance"
    REGULATORY_SCORECARD = "regulatory_scorecard"


class AIApprovalStatus(StrEnum):
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class ExplainabilityBlock(BaseModel):
    model_config = ConfigDict(extra="forbid")

    framework: dict[str, object]
    control_mapping: list[dict[str, object]]
    evidence: list[dict[str, object]]
    confidence: float
    coverage: dict[str, object]
    gap_analysis: dict[str, object]
    recommendations: list[str]
    business_impact: str
    regulatory_impact: str


class FrameworkCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    family: FrameworkName
    version: str = "1.0"
    description: str = ""
    status: str = "active"
    control_objectives: list[dict[str, object]] = Field(default_factory=list)
    regulatory_scope: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class PolicyCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    category: PolicyCategory
    description: str = ""
    status: str = "draft"
    version_label: str = "v1"
    owner: str = "governance"
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    frameworks: list[str] = Field(default_factory=list)
    rules: dict[str, object] = Field(default_factory=dict)
    exceptions: list[dict[str, object]] = Field(default_factory=list)
    enforcement_metadata: dict[str, object] = Field(default_factory=dict)
    metadata: dict[str, object] = Field(default_factory=dict)


class PolicyUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    category: PolicyCategory | None = None
    description: str | None = None
    status: str | None = None
    version_label: str | None = None
    owner: str | None = None
    approval_status: ApprovalStatus | None = None
    frameworks: list[str] | None = None
    rules: dict[str, object] | None = None
    exceptions: list[dict[str, object]] | None = None
    enforcement_metadata: dict[str, object] | None = None
    metadata: dict[str, object] | None = None


class ControlCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    name: str
    category: PolicyCategory
    control_type: ControlType
    owner: str = "control-owner"
    maturity: int = Field(default=1, ge=0, le=5)
    status: str = "draft"
    version_label: str = "v1"
    frameworks: list[str] = Field(default_factory=list)
    dependencies: list[str] = Field(default_factory=list)
    evidence_requirements: list[str] = Field(default_factory=list)
    testing: dict[str, object] = Field(default_factory=dict)
    metadata: dict[str, object] = Field(default_factory=dict)


class AssessmentRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    assessment_code: str
    assessment_type: AssessmentType = AssessmentType.COMPLIANCE
    subject_type: str
    subject_id: str
    frameworks: list[str] = Field(default_factory=list)
    policy_codes: list[str] = Field(default_factory=list)
    control_codes: list[str] = Field(default_factory=list)
    evidence_codes: list[str] = Field(default_factory=list)
    risk_codes: list[str] = Field(default_factory=list)
    ai_model_names: list[str] = Field(default_factory=list)
    business_unit: str | None = None
    owner: str = "governance"
    metadata: dict[str, object] = Field(default_factory=dict)


class ComplianceAnalyzeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    report_code: str
    report_type: ReportType = ReportType.EXECUTIVE
    subject_type: str
    subject_id: str
    frameworks: list[str] = Field(default_factory=list)
    policy_codes: list[str] = Field(default_factory=list)
    control_codes: list[str] = Field(default_factory=list)
    evidence_codes: list[str] = Field(default_factory=list)
    risk_codes: list[str] = Field(default_factory=list)
    ai_model_names: list[str] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class EvidenceUploadRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evidence_code: str
    evidence_type: EvidenceType = EvidenceType.DOCUMENT
    title: str
    source: str
    classification: str = "internal"
    status: str = "pending"
    storage_ref: str = ""
    version_number: int = Field(default=1, ge=1)
    framework_codes: list[str] = Field(default_factory=list)
    control_codes: list[str] = Field(default_factory=list)
    expires_at: datetime | None = None
    metadata: dict[str, object] = Field(default_factory=dict)


class AuditCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audit_code: str
    audit_type: AuditType = AuditType.COMPLIANCE
    scope: str
    subject_type: str
    subject_id: str
    checklist: list[str] = Field(default_factory=list)
    timeline: list[dict[str, object]] = Field(default_factory=list)
    tasks: list[dict[str, object]] = Field(default_factory=list)
    findings: list[dict[str, object]] = Field(default_factory=list)
    metadata: dict[str, object] = Field(default_factory=dict)


class FrameworkResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    code: str
    name: str
    family: str
    version: str
    description: str
    status: str
    control_objectives: list[dict[str, object]]
    regulatory_scope: list[str]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class PolicyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    code: str
    name: str
    category: str
    description: str
    status: str
    version_label: str
    owner: str
    approval_status: str
    frameworks: list[str]
    rules: dict[str, object]
    exceptions: list[dict[str, object]]
    enforcement_metadata: dict[str, object]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class ControlResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    code: str
    name: str
    category: str
    control_type: str
    owner: str
    maturity: int
    status: str
    version_label: str
    frameworks: list[str]
    dependencies: list[str]
    evidence_requirements: list[str]
    testing: dict[str, object]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class AssessmentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    assessment_code: str
    assessment_type: str
    subject_type: str
    subject_id: str
    frameworks: list[str]
    score: float
    confidence: float
    coverage: dict[str, object]
    evidence_coverage: dict[str, object]
    gap_analysis: dict[str, object]
    findings: list[dict[str, object]]
    recommendations: list[str]
    explainability: dict[str, object]
    status: str
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class ComplianceAnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    report_code: str
    report_type: str
    subject_type: str
    subject_id: str
    score: float
    confidence: float
    frameworks: list[str]
    control_mapping: list[dict[str, object]]
    evidence: list[dict[str, object]]
    coverage: dict[str, object]
    gap_analysis: dict[str, object]
    recommendations: list[str]
    business_impact: str
    regulatory_impact: str
    open_findings: list[dict[str, object]]
    ai_governance_score: float
    report_id: UUID
    explainability: dict[str, object]
    created_at: datetime
    updated_at: datetime


class ComplianceReportResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    report_code: str
    report_type: str
    subject_type: str
    subject_id: str
    status: str
    scorecard: dict[str, object]
    framework_coverage: dict[str, object]
    control_coverage: dict[str, object]
    evidence_summary: dict[str, object]
    open_findings: list[dict[str, object]]
    recommendations: list[str]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class RiskRegisterResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    risk_code: str
    risk_category: str
    owner: str
    inherent_risk: float
    residual_risk: float
    risk_treatment: str
    acceptance_status: str
    trend: list[dict[str, object]]
    history: list[dict[str, object]]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class EvidenceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    evidence_code: str
    evidence_type: str
    title: str
    source: str
    classification: str
    status: str
    storage_ref: str
    version_number: int
    framework_codes: list[str]
    control_codes: list[str]
    validation: dict[str, object]
    expires_at: datetime | None
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class AuditResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True)

    id: UUID
    audit_code: str
    audit_type: str
    scope: str
    subject_type: str
    subject_id: str
    status: str
    checklist: list[str]
    timeline: list[dict[str, object]]
    tasks: list[dict[str, object]]
    findings: list[dict[str, object]]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class AIGovernanceResponse(BaseModel):
    model_config = ConfigDict(extra="forbid", from_attributes=True, protected_namespaces=())

    id: UUID
    model_name: str
    model_provider: str
    approval_status: str
    prompt_governance: dict[str, object]
    dataset_governance: dict[str, object]
    inference_governance: dict[str, object]
    bias_score: float
    fairness_score: float
    transparency_score: float
    lifecycle_stage: str
    explainability: dict[str, object]
    metadata: dict[str, object]
    created_at: datetime
    updated_at: datetime


class GovernanceCatalogResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    frameworks: list[FrameworkResponse]
    policies: list[PolicyResponse]
    controls: list[ControlResponse]
    reports: list[ComplianceReportResponse]
    risks: list[RiskRegisterResponse]
