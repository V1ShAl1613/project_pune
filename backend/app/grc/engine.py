from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from statistics import mean
from typing import Any

try:
    import networkx as nx  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    nx = None

from app.core.settings import AppSettings
from app.grc.schemas import AssessmentRunRequest, ComplianceAnalyzeRequest, EvidenceUploadRequest, FrameworkName, PolicyCategory, RiskCategory, AuditCreateRequest, ControlType, AssessmentType, ReportType


def _now() -> datetime:
    return datetime.now(UTC)


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


@dataclass(slots=True)
class GRCGraphBackend:
    _nodes: dict[str, dict[str, object]] = field(init=False, default_factory=dict)
    _edges: list[dict[str, object]] = field(init=False, default_factory=list)
    _graph: Any | None = field(init=False, default=None)

    def __post_init__(self) -> None:
        self._graph = nx.MultiDiGraph() if nx is not None else None

    def add_node(self, node_key: str, node_type: str, label: str, **properties: object) -> None:
        payload = {"node_type": node_type, "label": label, "properties": properties}
        self._nodes[node_key] = payload
        if self._graph is not None:
            self._graph.add_node(node_key, **payload)

    def add_edge(self, source: str, target: str, relation_type: str, confidence: float = 50.0, **metadata: object) -> None:
        payload = {"source": source, "target": target, "relation_type": relation_type, "confidence": confidence, "metadata": metadata}
        self._edges.append(payload)
        if self._graph is not None:
            self._graph.add_edge(source, target, **payload)

    def graph(self) -> dict[str, object]:
        return {"nodes": self._nodes, "edges": self._edges}


@dataclass(slots=True)
class GRCIntelligenceEngine:
    settings: AppSettings

    def framework_catalog(self) -> list[dict[str, object]]:
        return [
            self._framework("NIST-CSF-2.0", "NIST CSF 2.0", FrameworkName.NIST_CSF_2_0.value, "Cybersecurity framework", ["Identify", "Protect", "Detect", "Respond", "Recover"], ["cyber", "resilience"]),
            self._framework("NIST-800-53", "NIST SP 800-53", FrameworkName.NIST_SP_800_53.value, "Security and privacy controls", ["AC", "AU", "CM", "IA", "IR", "RA", "SC"], ["security", "privacy"]),
            self._framework("NIST-AI-RMF", "NIST AI RMF", FrameworkName.NIST_AI_RMF.value, "AI risk management", ["Govern", "Map", "Measure", "Manage"], ["ai", "governance"]),
            self._framework("OWASP-ASVS", "OWASP ASVS", FrameworkName.OWASP_ASVS.value, "Application security verification", ["V1", "V2", "V3", "V4", "V5", "V6"], ["application", "security"]),
            self._framework("OWASP-API-TOP-10", "OWASP API Top 10", FrameworkName.OWASP_API_TOP_10.value, "API risk controls", ["API1", "API2", "API3", "API4"], ["application", "network"]),
            self._framework("OWASP-LLM-TOP-10", "OWASP LLM Top 10", FrameworkName.OWASP_LLM_TOP_10.value, "LLM risk controls", ["prompt injection", "data leakage", "model theft"], ["ai", "privacy"]),
            self._framework("MITRE-ATTACK", "MITRE ATT&CK", FrameworkName.MITRE_ATTACK.value, "Adversary tactics and techniques", ["Initial Access", "Execution", "Persistence", "Impact"], ["cyber", "threat"]),
            self._framework("MITRE-ATLAS", "MITRE ATLAS", FrameworkName.MITRE_ATLAS.value, "Adversarial ML tactics", ["Evasion", "Poisoning", "Model Inversion"], ["ai", "threat"]),
            self._framework("ISO-27001", "ISO 27001", FrameworkName.ISO_27001.value, "ISMS requirements", ["Context", "Leadership", "Planning", "Support", "Operation", "Performance", "Improvement"], ["security", "compliance"]),
            self._framework("ISO-27002", "ISO 27002", FrameworkName.ISO_27002.value, "Security controls", ["Access", "Asset", "Logging", "Supplier"], ["security", "vendor"]),
            self._framework("ISO-42001", "ISO 42001", FrameworkName.ISO_42001.value, "AI management system", ["AI governance", "AI lifecycle", "AI risk"], ["ai", "compliance"]),
            self._framework("SOC2", "SOC 2", FrameworkName.SOC_2.value, "Trust services criteria", ["Security", "Availability", "Confidentiality", "Processing Integrity", "Privacy"], ["security", "privacy", "operations"]),
            self._framework("PCI-DSS", "PCI DSS", FrameworkName.PCI_DSS.value, "Payment card security", ["Protect cardholder data", "Secure systems", "Monitor access"], ["financial", "security"]),
            self._framework("CIS-V8", "CIS Controls v8", FrameworkName.CIS_CONTROLS_V8.value, "Critical security controls", ["Inventory", "Protect", "Detect", "Respond"], ["cyber", "cloud"]),
            self._framework("COBIT", "COBIT", FrameworkName.COBIT.value, "Governance and management objectives", ["Evaluate", "Direct", "Monitor"], ["governance", "compliance"]),
            self._framework("GDPR", "GDPR", FrameworkName.GDPR.value, "Data protection regulation", ["Lawful basis", "Data minimization", "Rights", "Retention"], ["privacy", "data"]),
            self._framework("HIPAA", "HIPAA", FrameworkName.HIPAA.value, "Health information safeguards", ["Privacy", "Security", "Breach response"], ["privacy", "compliance"]),
        ]

    def control_catalog(self) -> list[dict[str, object]]:
        catalog = [
            ("GRC-SEC-001", "Access Control Review", PolicyCategory.SECURITY.value, ControlType.PREVENTIVE.value, ["NIST-800-53", "ISO-27001", "SOC2"], ["access recertification", "least privilege"]),
            ("GRC-PRV-001", "Privacy Notice Validation", PolicyCategory.PRIVACY.value, ControlType.ADMINISTRATIVE.value, ["GDPR", "ISO-27002"], ["privacy notice", "consent"]),
            ("GRC-AI-001", "Model Approval Workflow", PolicyCategory.AI_GOVERNANCE.value, ControlType.ADMINISTRATIVE.value, ["NIST-AI-RMF", "ISO-42001"], ["model review", "approval"]),
            ("GRC-CYB-001", "Threat Detection Logging", PolicyCategory.CYBERSECURITY.value, ControlType.DETECTIVE.value, ["NIST-CSF-2.0", "CIS-V8"], ["log review", "alerting"]),
            ("GRC-ID-001", "Identity Lifecycle Control", PolicyCategory.IDENTITY.value, ControlType.OPERATIONAL.value, ["NIST-800-53", "ISO-27002"], ["joiner mover leaver", "MFA"]),
            ("GRC-INF-001", "Infrastructure Baseline", PolicyCategory.INFRASTRUCTURE.value, ControlType.TECHNICAL.value, ["CIS-V8", "ISO-27002"], ["hardened baseline", "patching"]),
            ("GRC-CLO-001", "Cloud Configuration Monitoring", PolicyCategory.CLOUD.value, ControlType.DETECTIVE.value, ["NIST-CSF-2.0", "SOC2"], ["drift", "misconfiguration"]),
            ("GRC-DATA-001", "Data Retention Enforcement", PolicyCategory.DATA_PROTECTION.value, ControlType.ADMINISTRATIVE.value, ["GDPR", "HIPAA"], ["retention", "purge"]),
            ("GRC-BCP-001", "Business Continuity Test", PolicyCategory.BUSINESS_CONTINUITY.value, ControlType.OPERATIONAL.value, ["ISO-27001", "SOC2"], ["tabletop", "failover"]),
            ("GRC-VND-001", "Vendor Due Diligence", PolicyCategory.VENDOR_RISK.value, ControlType.ADMINISTRATIVE.value, ["COBIT", "SOC2"], ["due diligence", "contract review"]),
            ("GRC-INC-001", "Incident Response Playbook", PolicyCategory.INCIDENT_RESPONSE.value, ControlType.CORRECTIVE.value, ["NIST-CSF-2.0", "ISO-27001"], ["playbook", "containment"]),
            ("GRC-FRD-001", "Fraud Control Monitoring", PolicyCategory.FRAUD.value, ControlType.DETECTIVE.value, ["PCI-DSS", "NIST-800-53"], ["fraud signals", "alerts"]),
            ("GRC-CMP-001", "Compliance Evidence Review", PolicyCategory.COMPLIANCE.value, ControlType.ADMINISTRATIVE.value, ["COBIT", "SOC2"], ["evidence review", "attestation"]),
        ]
        controls: list[dict[str, object]] = []
        for code, name, category, control_type, frameworks, evidence in catalog:
            controls.append(
                {
                    "code": code,
                    "name": name,
                    "category": category,
                    "control_type": control_type,
                    "owner": f"owner:{category}",
                    "maturity": 3,
                    "status": "active",
                    "version_label": "v1",
                    "frameworks": frameworks,
                    "dependencies": [],
                    "evidence_requirements": evidence,
                    "testing": {"frequency": "quarterly", "method": "sample-test"},
                    "metadata": {"seeded": True},
                }
            )
        return controls

    def policy_catalog(self) -> list[dict[str, object]]:
        policies = [
            ("GRC-POL-SEC", "Security Governance Policy", PolicyCategory.SECURITY.value, ["NIST-800-53", "ISO-27001"], "deny", ["risk acceptance requires approval"]),
            ("GRC-POL-PRIV", "Privacy Governance Policy", PolicyCategory.PRIVACY.value, ["GDPR", "HIPAA"], "allow", ["data minimization", "retention limits"]),
            ("GRC-POL-AI", "AI Governance Policy", PolicyCategory.AI_GOVERNANCE.value, ["NIST-AI-RMF", "ISO-42001"], "allow", ["human oversight", "model approval"]),
            ("GRC-POL-CYB", "Cybersecurity Policy", PolicyCategory.CYBERSECURITY.value, ["NIST-CSF-2.0", "CIS-V8"], "deny", ["logging", "incident response"]),
            ("GRC-POL-DATA", "Data Protection Policy", PolicyCategory.DATA_PROTECTION.value, ["GDPR", "SOC2"], "allow", ["encryption", "retention"]),
            ("GRC-POL-FRD", "Fraud Risk Policy", PolicyCategory.FRAUD.value, ["PCI-DSS", "NIST-800-53"], "deny", ["monitor suspicious activity"]),
        ]
        return [
            {
                "code": code,
                "name": name,
                "category": category,
                "description": name,
                "status": "published",
                "version_label": "v1",
                "owner": "governance",
                "approval_status": "approved",
                "frameworks": frameworks,
                "rules": {"effect": effect},
                "exceptions": [],
                "enforcement_metadata": {"seeded": True, "requirements": requirements},
                "metadata": {"seeded": True},
            }
            for code, name, category, frameworks, effect, requirements in policies
        ]

    def assessment_bundle(self, request: AssessmentRunRequest, frameworks: list[dict[str, object]], policies: list[dict[str, object]], controls: list[dict[str, object]], evidence: list[dict[str, object]], risks: list[dict[str, object]]) -> dict[str, object]:
        framework_codes = request.frameworks or [framework["code"] for framework in frameworks]
        framework_coverage = self._coverage(framework_codes, frameworks, "code")
        control_coverage = self._coverage(request.control_codes or [control["code"] for control in controls], controls, "code")
        evidence_coverage = self._coverage(request.evidence_codes or [item["evidence_code"] for item in evidence], evidence, "evidence_code")
        policy_coverage = self._coverage(request.policy_codes or [item["code"] for item in policies], policies, "code")
        score = _clamp(mean([framework_coverage["coverage_score"], control_coverage["coverage_score"], evidence_coverage["coverage_score"], policy_coverage["coverage_score"]]))
        confidence = _clamp(58.0 + len(evidence) * 2.5 + len(controls) * 0.8)
        gaps = {
            "missing_frameworks": framework_coverage["missing"],
            "missing_controls": control_coverage["missing"],
            "missing_policies": policy_coverage["missing"],
            "missing_evidence": evidence_coverage["missing"],
        }
        findings = [
            {"finding_code": f"gap-{index}", "severity": "medium" if index % 2 else "high", "gap": gap}
            for index, gap in enumerate(gaps["missing_controls"][:5] or gaps["missing_policies"][:5] or gaps["missing_frameworks"][:5], start=1)
        ]
        recommendations = [
            "Close the highest priority control gaps.",
            "Collect supporting evidence for open requirements.",
            "Review policy alignment with mapped frameworks.",
        ]
        if score >= 80:
            recommendations.append("Maintain continuous monitoring for regressions.")
        return {
            "score": score,
            "confidence": confidence,
            "frameworks": framework_codes,
            "framework": framework_coverage,
            "control_mapping": self._control_mapping(request.control_codes, controls, framework_codes),
            "evidence": evidence,
            "coverage": {
                "framework": framework_coverage,
                "control": control_coverage,
                "policy": policy_coverage,
                "evidence": evidence_coverage,
            },
            "gap_analysis": gaps,
            "findings": findings,
            "recommendations": recommendations,
            "business_impact": "Unaddressed governance gaps can lead to findings, penalties, and operational exposure.",
            "regulatory_impact": self._regulatory_impact(framework_codes, gaps),
            "ai_governance_score": self._ai_governance_score(request.ai_model_names, frameworks),
            "scorecard": {
                "policy_coverage": policy_coverage["coverage_score"],
                "framework_coverage": framework_coverage["coverage_score"],
                "control_coverage": control_coverage["coverage_score"],
                "evidence_coverage": evidence_coverage["coverage_score"],
            },
            "open_findings": findings,
            "risk_summary": self._risk_summary(risks, score),
        }

    def compliance_bundle(self, request: ComplianceAnalyzeRequest, assessment: dict[str, object], risks: list[dict[str, object]], ai_records: list[dict[str, object]]) -> dict[str, object]:
        base_score = float(assessment["score"])
        ai_score = self._ai_compliance_score(request.ai_model_names, ai_records)
        compliance_score = _clamp((base_score * 0.7) + (ai_score * 0.3) - min(len(risks) * 1.5, 12.0))
        confidence = _clamp(float(assessment["confidence"]) + len(risks) * 0.5)
        return {
            "score": compliance_score,
            "confidence": confidence,
            "frameworks": assessment["frameworks"],
            "control_mapping": assessment["control_mapping"],
            "evidence": assessment["evidence"],
            "coverage": assessment["coverage"],
            "gap_analysis": assessment["gap_analysis"],
            "recommendations": assessment["recommendations"],
            "business_impact": assessment["business_impact"],
            "regulatory_impact": assessment["regulatory_impact"],
            "open_findings": assessment["open_findings"],
            "ai_governance_score": ai_score,
            "risk_summary": self._risk_summary(risks, compliance_score),
            "scorecard": {
                **assessment["scorecard"],
                "compliance_score": compliance_score,
                "ai_governance_score": ai_score,
            },
        }

    def report_bundle(self, request: ComplianceAnalyzeRequest, compliance: dict[str, object], assessment: dict[str, object], risks: list[dict[str, object]]) -> dict[str, object]:
        framework_coverage = assessment["coverage"]["framework"]
        control_coverage = assessment["coverage"]["control"]
        evidence_summary = {
            "evidence_count": len(assessment["evidence"]),
            "risk_count": len(risks),
            "open_findings": len(compliance["open_findings"]),
        }
        return {
            "report_code": request.report_code,
            "report_type": request.report_type.value,
            "subject_type": request.subject_type,
            "subject_id": request.subject_id,
            "scorecard": compliance["scorecard"],
            "framework_coverage": framework_coverage,
            "control_coverage": control_coverage,
            "evidence_summary": evidence_summary,
            "open_findings": compliance["open_findings"],
            "recommendations": compliance["recommendations"],
            "status": "published" if float(compliance["score"]) >= 60 else "draft",
            "report_metadata": request.metadata,
            "score": compliance["score"],
            "confidence": compliance["confidence"],
            "frameworks": compliance["frameworks"],
            "control_mapping": compliance["control_mapping"],
            "evidence": compliance["evidence"],
            "coverage": compliance["coverage"],
            "gap_analysis": compliance["gap_analysis"],
            "business_impact": compliance["business_impact"],
            "regulatory_impact": compliance["regulatory_impact"],
            "ai_governance_score": compliance["ai_governance_score"],
            "report_id": request.report_code,
            "explainability": {
                "framework": assessment["framework"],
                "control_mapping": assessment["control_mapping"],
                "evidence": assessment["evidence"],
                "confidence": compliance["confidence"],
                "coverage": assessment["coverage"],
                "gap_analysis": assessment["gap_analysis"],
                "recommendations": compliance["recommendations"],
                "business_impact": compliance["business_impact"],
                "regulatory_impact": compliance["regulatory_impact"],
            },
        }

    def ai_governance_bundle(self, model_name: str, provider: str, metadata: dict[str, object] | None = None) -> dict[str, object]:
        metadata = metadata or {}
        approval_status = "approved" if metadata.get("human_approved", True) else "pending"
        prompt_governance = {"policy": "review", "versioning": True, "human_oversight": True}
        dataset_governance = {"lineage": metadata.get("dataset_lineage", "tracked"), "sensitivity": metadata.get("dataset_sensitivity", "medium")}
        inference_governance = {"logging": True, "explainability": True, "rate_limits": True}
        bias_score = _clamp(100.0 - float(metadata.get("bias_risk", 18.0)))
        fairness_score = _clamp(100.0 - float(metadata.get("fairness_risk", 12.0)))
        transparency_score = _clamp(100.0 - float(metadata.get("transparency_risk", 10.0)))
        lifecycle_stage = str(metadata.get("lifecycle_stage", "governed"))
        return {
            "model_name": model_name,
            "model_provider": provider,
            "approval_status": approval_status,
            "prompt_governance": prompt_governance,
            "dataset_governance": dataset_governance,
            "inference_governance": inference_governance,
            "bias_score": bias_score,
            "fairness_score": fairness_score,
            "transparency_score": transparency_score,
            "lifecycle_stage": lifecycle_stage,
            "explainability": {
                "model_name": model_name,
                "model_provider": provider,
                "approval_status": approval_status,
                "human_oversight": True,
            },
            "metadata": metadata,
        }

    def _framework(self, code: str, name: str, family: str, description: str, control_objectives: list[str], regulatory_scope: list[str]) -> dict[str, object]:
        return {
            "code": code,
            "name": name,
            "family": family,
            "version": "1.0",
            "description": description,
            "status": "active",
            "control_objectives": [{"objective": objective, "status": "mapped"} for objective in control_objectives],
            "regulatory_scope": regulatory_scope,
            "metadata": {"seeded": True},
        }

    def _coverage(self, requested: list[str], source: list[dict[str, object]], key: str) -> dict[str, object]:
        available = {str(item[key]) for item in source}
        requested_set = {str(item) for item in requested if str(item).strip()}
        matched = sorted(requested_set.intersection(available))
        missing = sorted(requested_set.difference(available))
        if not requested_set:
            coverage_score = 100.0 if source else 0.0
        else:
            coverage_score = _clamp((len(matched) / len(requested_set)) * 100.0)
        return {"requested": sorted(requested_set), "matched": matched, "missing": missing, "coverage_score": coverage_score}

    def _control_mapping(self, requested_controls: list[str], controls: list[dict[str, object]], frameworks: list[str]) -> list[dict[str, object]]:
        control_index = {control["code"]: control for control in controls}
        codes = requested_controls or [control["code"] for control in controls]
        mapping = []
        for code in codes:
            control = control_index.get(code)
            if control is None:
                continue
            mapping.append({"control_code": code, "frameworks": control["frameworks"], "control_type": control["control_type"], "status": control["status"]})
        if not mapping:
            mapping = [{"control_code": control["code"], "frameworks": control["frameworks"], "control_type": control["control_type"], "status": control["status"]} for control in controls[:5]]
        return mapping

    def _risk_summary(self, risks: list[dict[str, object]], base_score: float) -> dict[str, object]:
        if not risks:
            return {"risk_count": 0, "risk_trend": [], "residual_risk": _clamp(100.0 - base_score)}
        residual = _clamp(mean([float(risk.get("residual_risk", risk.get("overall_financial_risk", 50.0))) for risk in risks]))
        return {"risk_count": len(risks), "risk_trend": [risk.get("trend", []) for risk in risks[:5]], "residual_risk": residual}

    def _regulatory_impact(self, framework_codes: list[str], gaps: dict[str, object]) -> str:
        if any(code in {"GDPR", "HIPAA"} for code in framework_codes):
            return "Privacy obligations may require remediation and documentation updates."
        if any(code in {"PCI-DSS"} for code in framework_codes):
            return "Payment card obligations require timely control remediation."
        if gaps.get("missing_controls"):
            return "Control gaps may result in audit findings and regulatory exposure."
        return "Regulatory exposure is reduced with current coverage."

    def _ai_governance_score(self, ai_model_names: list[str], frameworks: list[dict[str, object]]) -> float:
        if not ai_model_names:
            return 100.0
        coverage = 100.0 - min(len(ai_model_names) * 4.0, 24.0)
        if any(framework["family"] in {FrameworkName.NIST_AI_RMF.value, FrameworkName.ISO_42001.value, FrameworkName.OWASP_LLM_TOP_10.value} for framework in frameworks):
            coverage += 8.0
        return _clamp(coverage)

    def _ai_compliance_score(self, ai_model_names: list[str], ai_records: list[dict[str, object]]) -> float:
        if not ai_model_names and not ai_records:
            return 100.0
        baseline = 92.0 - min(len(ai_model_names) * 3.0, 18.0)
        if any(record.get("approval_status") == "approved" for record in ai_records):
            baseline += 4.0
        return _clamp(baseline)
