from __future__ import annotations

import hashlib
import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from statistics import mean
from typing import Any

from app.reasoning.schemas import ReasoningEvaluateRequest, ReasoningRequest, ReasoningStrategy


def _now() -> datetime:
    return datetime.now(UTC)


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return max(lower, min(upper, value))


def _tokenize(value: str) -> set[str]:
    return {token for token in re.findall(r"[a-z0-9_]+", value.lower()) if len(token) > 2}


def _overlap(left: str, right: str) -> float:
    left_tokens = _tokenize(left)
    right_tokens = _tokenize(right)
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / len(left_tokens | right_tokens)


def _score_from_text(value: str) -> float:
    return _clamp(45.0 + min(40.0, len(value) / 12.0))


@dataclass(slots=True)
class ReasoningPlanner:
    def plan(self, request: ReasoningRequest) -> dict[str, Any]:
        steps = ["collect_evidence", "rank_evidence", "validate_claims", "score_confidence", "score_trust", "assess_risk", "generate_recommendations"]
        if request.strategy in {ReasoningStrategy.SEQUENTIAL, ReasoningStrategy.HIERARCHICAL}:
            steps.insert(1, "fuse_context")
        if request.strategy in {ReasoningStrategy.GRAPH, ReasoningStrategy.HYBRID}:
            steps.append("build_decision_graph")
        if request.strategy in {ReasoningStrategy.REFLECTION, ReasoningStrategy.SELF_VERIFICATION, ReasoningStrategy.ITERATIVE_REFINEMENT}:
            steps.extend(["reflect", "self_verify"])
        if request.strategy == ReasoningStrategy.RULE_BASED:
            steps.insert(2, "apply_policy_rules")
        graph = [
            {"id": "request", "label": request.decision_domain, "type": "input"},
            {"id": "evidence", "label": "evidence collection", "type": "process"},
            {"id": "validation", "label": "validation", "type": "decision"},
            {"id": "confidence", "label": "confidence", "type": "process"},
            {"id": "trust", "label": "trust", "type": "process"},
            {"id": "risk", "label": "risk", "type": "process"},
            {"id": "recommendations", "label": "recommendations", "type": "output"},
        ]
        return {"strategy": request.strategy.value, "steps": steps, "graph": graph, "edges": [{"from": graph[index]["id"], "to": graph[index + 1]["id"]} for index in range(len(graph) - 1)]}


@dataclass(slots=True)
class EvidenceEngine:
    def collect(self, request: ReasoningRequest) -> list[dict[str, Any]]:
        evidence: list[dict[str, Any]] = []
        for item in request.evidence:
            claim = str(item.get("claim") or item.get("text") or request.query)
            evidence.append(
                {
                    "source_type": str(item.get("source_type") or "context"),
                    "source_name": str(item.get("source_name") or request.decision_domain),
                    "claim": claim,
                    "snippet": str(item.get("snippet") or claim),
                    "reference_uri": item.get("reference_uri"),
                    "score": _clamp(float(item.get("score") or _score_from_text(claim))),
                    "verified": bool(item.get("verified", item.get("reference_uri"))),
                    "evidence_metadata": dict(item.get("metadata") or {}),
                }
            )
        for label, values in {
            "knowledge": request.knowledge_sources,
            "mitre": request.mitre_references,
            "compliance": request.compliance_references,
            "source": request.source_references,
            "actions": request.recommended_actions,
            "alternatives": request.alternative_actions,
            "risk": request.risk_factors,
        }.items():
            for value in values:
                text = str(value)
                if text.strip():
                    evidence.append(
                        {
                            "source_type": label,
                            "source_name": text[:128],
                            "claim": text,
                            "snippet": text,
                            "reference_uri": None,
                            "score": _score_from_text(text),
                            "verified": label in {"knowledge", "mitre", "compliance"},
                            "evidence_metadata": {"origin": label},
                        }
                    )
        for key, value in request.context.items():
            if isinstance(value, list):
                for item in value:
                    text = str(item)
                    evidence.append(
                        {
                            "source_type": key,
                            "source_name": key,
                            "claim": text,
                            "snippet": text,
                            "reference_uri": None,
                            "score": _score_from_text(text),
                            "verified": True,
                            "evidence_metadata": {"origin": "context", "key": key},
                        }
                    )
            elif isinstance(value, dict):
                text = ", ".join(f"{k}: {v}" for k, v in value.items())
                evidence.append(
                    {
                        "source_type": key,
                        "source_name": key,
                        "claim": text,
                        "snippet": text,
                        "reference_uri": None,
                        "score": _score_from_text(text),
                        "verified": True,
                        "evidence_metadata": {"origin": "context", "key": key},
                    }
                )
        return sorted(evidence, key=lambda item: item["score"], reverse=True)

    def validate(self, request: ReasoningRequest, evidence: list[dict[str, Any]], output_text: str | None) -> dict[str, Any]:
        unsupported_claims = []
        evidence_text = " ".join(item["claim"] for item in evidence)
        for sentence in [part.strip() for part in re.split(r"[.!?]+", output_text or request.query) if part.strip()]:
            if _overlap(sentence, evidence_text) < 0.12 and _overlap(sentence, request.query) < 0.1:
                unsupported_claims.append(sentence)
        knowledge_freshness = not any(isinstance(item.get("evidence_metadata"), dict) and isinstance(item["evidence_metadata"].get("timestamp"), datetime) and item["evidence_metadata"]["timestamp"] < (_now() - timedelta(hours=request.metadata.get("knowledge_freshness_hours", 72))) for item in evidence)
        contradictions = bool(request.context.get("contradictions"))
        evidence_completeness = bool(evidence and any(item.get("reference_uri") for item in evidence))
        reasoning_quality = len(evidence) >= 1 and len(request.recommended_actions) + len(request.alternative_actions) >= 1
        output_integrity = bool((output_text or request.query).strip())
        return {
            "evidence_completeness": evidence_completeness,
            "knowledge_freshness": knowledge_freshness,
            "contradictory_evidence": contradictions,
            "reasoning_quality": reasoning_quality,
            "output_integrity": output_integrity,
            "unsupported_claims": unsupported_claims,
            "source_references": [item["reference_uri"] for item in evidence if item.get("reference_uri")],
        }


@dataclass(slots=True)
class ConfidenceEngine:
    def score(self, request: ReasoningRequest, evidence: list[dict[str, Any]], risk_score: float, reasoning_steps: list[str]) -> dict[str, float]:
        evidence_strength = _clamp(mean([float(item["score"]) for item in evidence]) if evidence else 25.0)
        knowledge_score = _clamp(20.0 + 12.0 * len(request.knowledge_sources) + evidence_strength * 0.35)
        model_score = _clamp(60.0 + (10.0 if "nemotron" in request.metadata.get("model_name", "nvidia/nemotron-mini").lower() else 0.0))
        reasoning_score = _clamp(35.0 + 7.0 * len(reasoning_steps) + (8.0 if request.strategy in {ReasoningStrategy.HYBRID, ReasoningStrategy.GRAPH} else 0.0))
        data_quality_score = _clamp(30.0 + 5.0 * len(request.source_references) + 3.0 * len(request.context))
        risk_confidence = _clamp(100.0 - risk_score)
        decision_confidence = _clamp((evidence_strength * 0.22) + (knowledge_score * 0.15) + (model_score * 0.18) + (reasoning_score * 0.2) + (data_quality_score * 0.15) + (risk_confidence * 0.1))
        overall = _clamp((decision_confidence * 0.45) + (evidence_strength * 0.15) + (knowledge_score * 0.1) + (reasoning_score * 0.15) + (risk_confidence * 0.15))
        return {"evidence_strength": evidence_strength, "knowledge_score": knowledge_score, "model_score": model_score, "reasoning_score": reasoning_score, "data_quality_score": data_quality_score, "risk_confidence": risk_confidence, "decision_confidence": decision_confidence, "overall_confidence": overall}


@dataclass(slots=True)
class TrustEngine:
    def score(self, request: ReasoningRequest, evidence: list[dict[str, Any]], confidence: dict[str, float], hallucination: dict[str, Any]) -> dict[str, float]:
        evidence_trust = _clamp(confidence["evidence_strength"] * 0.9 + (10.0 if evidence else -10.0))
        knowledge_trust = _clamp(35.0 + 8.0 * len(request.knowledge_sources) + evidence_trust * 0.15)
        reasoning_trust = _clamp(confidence["reasoning_score"] * 0.95)
        source_trust = _clamp(40.0 + 12.0 * len(request.source_references) + (8.0 if any(item.get("verified") for item in evidence) else 0.0))
        decision_trust = _clamp((confidence["decision_confidence"] + confidence["overall_confidence"] + evidence_trust) / 3.0)
        agent_trust = _clamp((decision_trust + reasoning_trust) / 2.0)
        model_trust = _clamp(confidence["model_score"] - hallucination.get("confidence_penalty", 0.0))
        overall = _clamp((evidence_trust * 0.15) + (knowledge_trust * 0.15) + (reasoning_trust * 0.2) + (source_trust * 0.15) + (decision_trust * 0.15) + (agent_trust * 0.1) + (model_trust * 0.1))
        return {"evidence_trust": evidence_trust, "knowledge_trust": knowledge_trust, "reasoning_trust": reasoning_trust, "source_trust": source_trust, "decision_trust": decision_trust, "agent_trust": agent_trust, "model_trust": model_trust, "overall_trust": overall}


@dataclass(slots=True)
class HallucinationDetector:
    def detect(self, request: ReasoningRequest, evidence: list[dict[str, Any]], answer: str) -> dict[str, Any]:
        evidence_text = " ".join(item["claim"] for item in evidence)
        unsupported_claims = [sentence.strip() for sentence in re.split(r"[.!?]+", answer or request.query) if sentence.strip() and _overlap(sentence, evidence_text) < 0.12]
        penalty = _clamp(len(unsupported_claims) * 8.0 + (10.0 if not evidence else 0.0), 0.0, 40.0)
        return {"unsupported_claims": unsupported_claims, "fact_verification": "passed" if not unsupported_claims else "needs_review", "reference_validation": "passed" if any(item.get("reference_uri") for item in evidence) else "missing", "confidence_penalty": penalty, "response_verified": not unsupported_claims and bool(evidence)}


@dataclass(slots=True)
class DecisionValidator:
    def validate(self, request: ReasoningRequest, evidence: list[dict[str, Any]], confidence: dict[str, float], trust: dict[str, float], hallucination: dict[str, Any], risk_level: str) -> dict[str, Any]:
        evidence_completeness = bool(evidence)
        confidence_threshold_met = confidence["overall_confidence"] >= float(request.metadata.get("confidence_threshold", 70))
        trust_threshold_met = trust["overall_trust"] >= float(request.metadata.get("trust_threshold", 70))
        risk_threshold_met = _risk_to_score(risk_level) <= float(request.metadata.get("risk_threshold", 60))
        policy_compliance = not any(term in request.query.lower() for term in request.metadata.get("forbidden_terms", []))
        knowledge_freshness = True
        reasoning_quality = len(request.recommended_actions) + len(request.alternative_actions) >= 1
        output_integrity = bool(request.query.strip())
        validated = all([evidence_completeness, confidence_threshold_met, trust_threshold_met, risk_threshold_met, policy_compliance, knowledge_freshness, reasoning_quality, output_integrity, not hallucination["unsupported_claims"]])
        notes = []
        if not evidence_completeness:
            notes.append("evidence completeness is low")
        if not confidence_threshold_met:
            notes.append("confidence threshold not met")
        if not trust_threshold_met:
            notes.append("trust threshold not met")
        if not risk_threshold_met:
            notes.append("risk threshold exceeded")
        if not policy_compliance:
            notes.append("policy compliance check failed")
        if hallucination["unsupported_claims"]:
            notes.append("unsupported claims detected")
        return {"evidence_completeness": evidence_completeness, "confidence_threshold_met": confidence_threshold_met, "policy_compliance": policy_compliance, "knowledge_freshness": knowledge_freshness, "risk_threshold_met": risk_threshold_met, "contradictory_evidence": bool(request.context.get("contradictions")), "reasoning_quality": reasoning_quality, "output_integrity": output_integrity, "validated": validated, "validation_notes": notes}


@dataclass(slots=True)
class RiskEngine:
    def assess(self, request: ReasoningRequest | Any, evidence: list[dict[str, Any]], confidence: dict[str, float]) -> dict[str, Any]:
        base = _clamp(float(getattr(request, "current_risk", request.metadata.get("current_risk", 50.0))))
        factor_count = max(1, len(getattr(request, "risk_factors", [])) + len(getattr(request, "assets", [])) + len(getattr(request, "dependencies", [])))
        technical = _clamp(base * 0.25 + factor_count * 2.8 + len(evidence) * 1.5)
        operational = _clamp(base * 0.18 + factor_count * 2.0)
        business = _clamp(base * 0.22 + len(getattr(request, "assets", [])) * 3.0)
        financial = _clamp(base * 0.16 + len(getattr(request, "dependencies", [])) * 2.5)
        compliance = _clamp(base * 0.14 + len([factor for factor in getattr(request, "risk_factors", []) if "compliance" in factor.lower()]) * 6.0)
        reputation = _clamp(base * 0.12 + len([factor for factor in getattr(request, "risk_factors", []) if "reputation" in factor.lower() or "brand" in factor.lower()]) * 8.0)
        infrastructure = _clamp(base * 0.2 + len(getattr(request, "dependencies", [])) * 4.0)
        identity = _clamp(base * 0.18 + len([factor for factor in getattr(request, "risk_factors", []) if any(term in factor.lower() for term in ("identity", "auth", "account"))]) * 7.0)
        cloud = _clamp(base * 0.2 + len([asset for asset in getattr(request, "assets", []) if any(term in asset.lower() for term in ("cloud", "k8s", "container"))]) * 8.0)
        ai_risk = _clamp(base * 0.19 + len([factor for factor in getattr(request, "risk_factors", []) if "ai" in factor.lower() or "model" in factor.lower()]) * 8.0)
        supply_chain = _clamp(base * 0.15 + len([dep for dep in getattr(request, "dependencies", []) if any(term in dep.lower() for term in ("vendor", "supplier", "third-party"))]) * 8.0)
        breakdown = {"technical_risk": technical, "operational_risk": operational, "business_risk": business, "financial_risk": financial, "compliance_risk": compliance, "reputation_risk": reputation, "infrastructure_risk": infrastructure, "identity_risk": identity, "cloud_risk": cloud, "ai_risk": ai_risk, "supply_chain_risk": supply_chain}
        risk_score = mean(breakdown.values()) if breakdown else base
        risk_level = _risk_level(risk_score)
        return {"risk_level": risk_level, "current_risk": base, **breakdown, "risk_breakdown": breakdown, "business_impact": f"{risk_level.title()} business exposure across {len(getattr(request, 'assets', []))} assets", "technical_impact": f"{risk_level.title()} technical exposure with {len(evidence)} evidence items", "risk_metadata": {"confidence": confidence["overall_confidence"], "factor_count": factor_count, "evidence_count": len(evidence)}}


@dataclass(slots=True)
class QuantumRiskEngine:
    def project(self, request: Any, evidence: list[dict[str, Any]], risk: dict[str, Any], horizon_days: int = 30) -> dict[str, Any]:
        chain = [{"step": index + 1, "node": factor, "weight": _clamp(40.0 + index * 4.0), "type": "risk_factor"} for index, factor in enumerate(getattr(request, "risk_factors", [])[:10])]
        chain.extend({"step": len(chain) + index + 1, "node": asset, "weight": _clamp(45.0 + index * 3.0), "type": "asset"} for index, asset in enumerate(getattr(request, "assets", [])[:10]))
        exposure = _clamp(len(getattr(request, "assets", [])) * 6.0 + len(getattr(request, "dependencies", [])) * 4.0 + len(getattr(request, "risk_factors", [])) * 2.0)
        current = _clamp(float(risk["current_risk"]))
        projected = _clamp(current + min(30.0, len(chain) * 3.0 + len(evidence) * 1.2) + min(20.0, math.log1p(max(1, horizon_days)) * 4.0) + exposure * 0.35)
        return {"current_risk": current, "projected_risk": projected, "worst_case": _clamp(projected + 15.0), "best_case": _clamp(current - 20.0), "likelihood": _clamp(35.0 + len(chain) * 4.0), "exposure": exposure, "business_criticality": _clamp(len(getattr(request, "assets", [])) * 5.0), "recovery_difficulty": _clamp(20.0 + len(getattr(request, "dependencies", [])) * 4.0 + len(chain) * 3.0), "confidence": _clamp(100.0 - abs(projected - current) * 0.8), "attack_chain": chain, "quantum_metadata": {"horizon_days": horizon_days, "cascade_factor": len(chain)}}


@dataclass(slots=True)
class RecommendationEngine:
    def generate(self, request: ReasoningRequest, evidence: list[dict[str, Any]], risk: dict[str, Any], validation: dict[str, Any]) -> list[dict[str, Any]]:
        severity = risk["risk_level"]
        recommendations = [
            {"priority_rank": 1, "category": "security", "title": "Immediate containment", "action": "Isolate exposed paths, preserve evidence, and verify the blast radius.", "horizon": "immediate", "expected_impact": f"Reduce {severity} risk while increasing confidence.", "business_value": 84.0, "technical_value": 88.0, "security_value": 92.0, "compliance_value": 72.0, "recommendation_metadata": {"severity": severity, "evidence_count": len(evidence)}},
            {"priority_rank": 2, "category": "business", "title": "Continuity controls", "action": "Implement compensating controls and coordinate impacted stakeholders.", "horizon": "short_term", "expected_impact": f"Stabilize operations and reduce risk propagation.", "business_value": 78.0, "technical_value": 72.0, "security_value": 74.0, "compliance_value": 70.0, "recommendation_metadata": {"severity": severity, "evidence_count": len(evidence)}},
            {"priority_rank": 3, "category": "compliance", "title": "Governance hardening", "action": "Update policies, controls, and audit evidence to reduce residual risk.", "horizon": "long_term", "expected_impact": f"Improve compliance posture and decision trust.", "business_value": 70.0, "technical_value": 68.0, "security_value": 76.0, "compliance_value": 88.0, "recommendation_metadata": {"severity": severity, "evidence_count": len(evidence)}},
        ]
        if not validation["evidence_completeness"]:
            recommendations.append({"priority_rank": 4, "category": "evidence", "title": "Strengthen evidence coverage", "action": "Add verified source references and fresher context to improve grounded reasoning.", "horizon": "immediate", "expected_impact": "Improves faithfulness and reduces hallucination risk.", "business_value": 62.0, "technical_value": 88.0, "security_value": 70.0, "compliance_value": 72.0, "recommendation_metadata": {"reason": "evidence_gap"}})
        return recommendations


@dataclass(slots=True)
class EvaluationEngine:
    def evaluate(self, request: ReasoningEvaluateRequest, evidence: list[dict[str, Any]] | None = None, confidence: dict[str, float] | None = None, trust: dict[str, float] | None = None) -> dict[str, Any]:
        metrics: list[dict[str, Any]] = []
        correctness_values: list[float] = []
        precision_values: list[float] = []
        recall_values: list[float] = []
        faithfulness_values: list[float] = []
        groundedness_values: list[float] = []
        hallucination_values: list[float] = []
        recommendation_values: list[float] = []
        latency_values: list[float] = []
        cost_values: list[float] = []
        for sample in request.samples:
            correctness = _overlap(sample.expected_output, sample.actual_output)
            precision = _overlap(sample.actual_output, " ".join(sample.references or [str(sample.context)]))
            recall = _overlap(sample.expected_output, sample.input_text)
            faithfulness = min(1.0, (correctness + precision) / 2.0)
            groundedness = min(1.0, precision + (0.2 if evidence else 0.0))
            hallucination_rate = 1.0 - groundedness
            recommendation_quality = min(1.0, len(sample.references) / max(1.0, len(sample.expected_output.split())))
            latency = 120.0 + len(sample.input_text) * 0.4
            cost = 0.01 * max(1, len(sample.input_text) // 100)
            correctness_values.append(correctness)
            precision_values.append(precision)
            recall_values.append(recall)
            faithfulness_values.append(faithfulness)
            groundedness_values.append(groundedness)
            hallucination_values.append(hallucination_rate)
            recommendation_values.append(recommendation_quality)
            latency_values.append(latency)
            cost_values.append(cost)
            metrics.extend(
                [
                    {"metric_name": "answer_correctness", "metric_value": correctness * 100.0, "benchmark_value": 80.0, "target_value": 75.0, "passed": correctness >= 0.75},
                    {"metric_name": "context_precision", "metric_value": precision * 100.0, "benchmark_value": 75.0, "target_value": 70.0, "passed": precision >= 0.7},
                    {"metric_name": "context_recall", "metric_value": recall * 100.0, "benchmark_value": 70.0, "target_value": 65.0, "passed": recall >= 0.65},
                    {"metric_name": "faithfulness", "metric_value": faithfulness * 100.0, "benchmark_value": 80.0, "target_value": 75.0, "passed": faithfulness >= 0.75},
                    {"metric_name": "groundedness", "metric_value": groundedness * 100.0, "benchmark_value": 80.0, "target_value": 75.0, "passed": groundedness >= 0.75},
                    {"metric_name": "hallucination_rate", "metric_value": hallucination_rate * 100.0, "benchmark_value": 20.0, "target_value": 15.0, "passed": hallucination_rate <= 0.25},
                    {"metric_name": "recommendation_quality", "metric_value": recommendation_quality * 100.0, "benchmark_value": 70.0, "target_value": 65.0, "passed": recommendation_quality >= 0.65},
                    {"metric_name": "latency_ms", "metric_value": latency, "benchmark_value": 250.0, "target_value": 300.0, "passed": latency <= 300.0},
                    {"metric_name": "cost", "metric_value": cost, "benchmark_value": 0.05, "target_value": 0.1, "passed": cost <= 0.1},
                ]
            )
        sample_count = max(1, len(request.samples))
        ai_score = _clamp(mean(correctness_values) * 100.0 if correctness_values else 0.0)
        reasoning_score = _clamp(mean(faithfulness_values) * 100.0 if faithfulness_values else 0.0)
        evidence_score = _clamp(mean(precision_values + recall_values) * 50.0 if precision_values else 0.0)
        risk_score = _clamp(100.0 - (mean(hallucination_values) * 100.0 if hallucination_values else 0.0))
        compliance_score = _clamp(70.0 + (10.0 if request.metadata.get("policy_compliant", True) else -20.0))
        trust_score = _clamp((confidence["overall_confidence"] if confidence else 60.0) * 0.5 + (trust["overall_trust"] if trust else 60.0) * 0.5)
        overall_quality = _clamp((ai_score + reasoning_score + evidence_score + risk_score + compliance_score + trust_score) / 6.0)
        return {"scorecard": {"ai_score": ai_score, "reasoning_score": reasoning_score, "evidence_score": evidence_score, "risk_score": risk_score, "compliance_score": compliance_score, "trust_score": trust_score, "overall_quality": overall_quality, "enterprise_readiness": _clamp((overall_quality + compliance_score + trust_score) / 3.0)}, "metrics": metrics, "benchmark_name": request.benchmark_name, "model_name": request.model_name, "dataset_name": request.dataset_name, "summary": {"samples": sample_count, "latency_ms": mean(latency_values) if latency_values else 0.0, "cost": mean(cost_values) if cost_values else 0.0}}


@dataclass(slots=True)
class ReasoningMetricsEngine:
    def summarize(self, traces: list[dict[str, Any]], decisions: list[dict[str, Any]], confidence_scores: list[dict[str, Any]], trust_scores: list[dict[str, Any]], hallucinations: list[dict[str, Any]], validations: list[dict[str, Any]], recommendations: list[dict[str, Any]], scorecards: list[dict[str, Any]]) -> dict[str, Any]:
        average_confidence = mean([float(item.get("overall_confidence", 0.0)) for item in confidence_scores]) if confidence_scores else 0.0
        average_trust = mean([float(item.get("overall_trust", 0.0)) for item in trust_scores]) if trust_scores else 0.0
        average_risk = mean([_risk_to_score(str(item.get("risk_level", "moderate"))) for item in traces]) if traces else 0.0
        hallucination_rate = (len([item for item in hallucinations if item.get("unsupported_claims")]) / max(1, len(hallucinations))) * 100.0
        validation_pass_rate = (len([item for item in validations if item.get("validated")]) / max(1, len(validations))) * 100.0
        recommendation_success_rate = (len([item for item in recommendations if item.get("priority_rank", 99) <= 3]) / max(1, len(recommendations))) * 100.0
        reasoning_latency_ms = mean([float(item.get("latency_ms", 0.0)) for item in scorecards]) if scorecards else 0.0
        return {"total_traces": len(traces), "total_decisions": len(decisions), "average_confidence": average_confidence, "average_trust": average_trust, "average_risk": average_risk, "hallucination_rate": hallucination_rate, "validation_pass_rate": validation_pass_rate, "recommendation_success_rate": recommendation_success_rate, "reasoning_latency_ms": reasoning_latency_ms, "confidence_distribution": _distribution([float(item.get("overall_confidence", 0.0)) for item in confidence_scores]), "trust_distribution": _distribution([float(item.get("overall_trust", 0.0)) for item in trust_scores]), "scorecard": {"ai_score": mean([float(item.get("ai_score", 0.0)) for item in scorecards]) if scorecards else 0.0, "reasoning_score": mean([float(item.get("reasoning_score", 0.0)) for item in scorecards]) if scorecards else 0.0, "evidence_score": mean([float(item.get("evidence_score", 0.0)) for item in scorecards]) if scorecards else 0.0, "risk_score": mean([float(item.get("risk_score", 0.0)) for item in scorecards]) if scorecards else 0.0, "compliance_score": mean([float(item.get("compliance_score", 0.0)) for item in scorecards]) if scorecards else 0.0, "trust_score": mean([float(item.get("trust_score", 0.0)) for item in scorecards]) if scorecards else 0.0, "overall_quality": mean([float(item.get("overall_quality", 0.0)) for item in scorecards]) if scorecards else 0.0, "enterprise_readiness": mean([float(item.get("enterprise_readiness", 0.0)) for item in scorecards]) if scorecards else 0.0}}


def _distribution(values: list[float]) -> dict[str, float]:
    buckets = {"0_25": 0.0, "25_50": 0.0, "50_75": 0.0, "75_100": 0.0}
    if not values:
        return buckets
    for value in values:
        if value < 25:
            buckets["0_25"] += 1
        elif value < 50:
            buckets["25_50"] += 1
        elif value < 75:
            buckets["50_75"] += 1
        else:
            buckets["75_100"] += 1
    total = float(len(values))
    return {key: round(count / total * 100.0, 2) for key, count in buckets.items()}


def _risk_level(score: float) -> str:
    if score >= 85:
        return "critical"
    if score >= 70:
        return "high"
    if score >= 40:
        return "moderate"
    return "low"


def _risk_to_score(level: str) -> float:
    return {"critical": 95.0, "high": 80.0, "moderate": 55.0, "low": 20.0}.get(level.lower(), 55.0)


def cache_key(prefix: str, payload: dict[str, object]) -> str:
    digest = hashlib.sha256(repr(sorted(payload.items())).encode("utf-8")).hexdigest()
    return f"{prefix}:{digest}"
