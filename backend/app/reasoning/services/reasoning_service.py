from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from uuid import uuid4

from redis.asyncio import Redis

from app.core.settings import AppSettings
from app.reasoning.models import (
    ConfidenceScore,
    DecisionRecord,
    EvidenceRecord,
    EvaluationMetric,
    EvaluationRun,
    HallucinationRecord,
    Recommendation,
    ReasoningTrace,
    RiskProjection,
    TrustScore,
)
from app.reasoning.repositories.reasoning_repository import ReasoningRepository
from app.reasoning.schemas import (
    ConfidenceResponse,
    DecisionValidationResponse,
    EvidenceResponse,
    EvaluationMetricResponse,
    EvaluationRunResponse,
    HallucinationResponse,
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
    ReasoningStrategy,
    TrustResponse,
)
from app.reasoning.shared import (
    cache_key,
    ConfidenceEngine,
    DecisionValidator,
    EvidenceEngine,
    EvaluationEngine,
    HallucinationDetector,
    QuantumRiskEngine,
    ReasoningMetricsEngine,
    ReasoningPlanner,
    RecommendationEngine,
    RiskEngine,
    TrustEngine,
    _risk_level,
)


@dataclass(slots=True)
class ReasoningService:
    repository: ReasoningRepository | None
    settings: AppSettings
    redis_client: Redis | None
    logger: logging.Logger
    planner: ReasoningPlanner = field(init=False)
    evidence_engine: EvidenceEngine = field(init=False)
    confidence_engine: ConfidenceEngine = field(init=False)
    trust_engine: TrustEngine = field(init=False)
    hallucination_detector: HallucinationDetector = field(init=False)
    validator: DecisionValidator = field(init=False)
    risk_engine: RiskEngine = field(init=False)
    quantum_risk_engine: QuantumRiskEngine = field(init=False)
    recommendation_engine: RecommendationEngine = field(init=False)
    evaluation_engine: EvaluationEngine = field(init=False)
    metrics_engine: ReasoningMetricsEngine = field(init=False)

    def __post_init__(self) -> None:
        self.repository = self.repository or ReasoningRepository()
        self.planner = ReasoningPlanner()
        self.evidence_engine = EvidenceEngine()
        self.confidence_engine = ConfidenceEngine()
        self.trust_engine = TrustEngine()
        self.hallucination_detector = HallucinationDetector()
        self.validator = DecisionValidator()
        self.risk_engine = RiskEngine()
        self.quantum_risk_engine = QuantumRiskEngine()
        self.recommendation_engine = RecommendationEngine()
        self.evaluation_engine = EvaluationEngine()
        self.metrics_engine = ReasoningMetricsEngine()

    async def analyze(self, request: ReasoningRequest) -> ReasoningAnalysisResponse:
        cached = await self._cache_get(self._cache_key("analyze", request))
        if cached:
            return ReasoningAnalysisResponse.model_validate(cached)
        bundle = self._analyze_bundle(request)
        response = await self._persist_analysis(request, bundle)
        await self._cache_set(self._cache_key("analyze", request), response.model_dump(mode="json"), ttl=self.settings.reasoning_cache_ttl_seconds)
        return response

    async def validate(self, request: ReasoningValidateRequest) -> DecisionValidationResponse:
        return (await self.analyze(request)).validation

    async def explain(self, request: ReasoningRequest) -> ReasoningAnalysisResponse:
        return await self.analyze(request)

    async def evaluate(self, request: ReasoningEvaluateRequest) -> EvaluationRunResponse:
        cached = await self._cache_get(self._cache_key("evaluate", request))
        if cached:
            return EvaluationRunResponse.model_validate(cached)
        bundle = self.evaluation_engine.evaluate(request)
        run = EvaluationRun(trace_id=None, dataset_name=bundle["dataset_name"], benchmark_name=bundle["benchmark_name"], model_name=bundle["model_name"], status="completed", scorecard=bundle["scorecard"], evaluation_metadata={**request.metadata, **bundle["summary"], "frameworks": self._available_evaluation_frameworks()})
        await self.repository.add_evaluation_run(run)
        metrics = [EvaluationMetric(run_id=run.id, metric_name=item["metric_name"], metric_value=item["metric_value"], benchmark_value=item["benchmark_value"], target_value=item["target_value"], passed=item["passed"], metric_metadata={"dataset": request.dataset_name}) for item in bundle["metrics"]]
        await self.repository.add_evaluation_metrics(metrics)
        response = EvaluationRunResponse(id=run.id or uuid4(), trace_id=run.trace_id, dataset_name=run.dataset_name, benchmark_name=run.benchmark_name, model_name=run.model_name, status=run.status, scorecard=run.scorecard, metrics=[self._to_evaluation_metric_response(item) for item in metrics], evaluation_metadata=run.evaluation_metadata, created_at=run.created_at or datetime.now(UTC), updated_at=run.updated_at or datetime.now(UTC))
        await self._cache_set(self._cache_key("evaluate", request), response.model_dump(mode="json"), ttl=self.settings.reasoning_evaluation_cache_ttl_seconds)
        return response

    async def risk_analyze(self, request: RiskAnalyzeRequest) -> RiskAssessmentResponse:
        bundle = self._risk_bundle(request)
        return self._to_risk_response(bundle)

    async def risk_project(self, request: RiskProjectRequest) -> QuantumRiskProjectionResponse:
        risk_bundle = self._risk_bundle(request)
        reasoning_request = self._risk_reasoning_request(request)
        horizon_days = int(getattr(request, "horizon_days", 30) or 30)
        quantum_bundle = self.quantum_risk_engine.project(request, self.evidence_engine.collect(reasoning_request), risk_bundle, horizon_days)
        return self._to_quantum_response(quantum_bundle)

    async def recommendations(self) -> list[RecommendationResponse]:
        return [self._to_recommendation_response(record) for record in await self.repository.list_recommendations()]

    async def confidence(self) -> list[ConfidenceResponse]:
        return [self._to_confidence_response(record) for record in await self.repository.list_confidence_scores()]

    async def trust(self) -> list[TrustResponse]:
        return [self._to_trust_response(record) for record in await self.repository.list_trust_scores()]

    async def evaluations(self) -> list[EvaluationRunResponse]:
        runs = await self.repository.list_evaluation_runs()
        metrics = await self.repository.list_evaluation_metrics()
        return [EvaluationRunResponse(id=run.id or uuid4(), trace_id=run.trace_id, dataset_name=run.dataset_name, benchmark_name=run.benchmark_name, model_name=run.model_name, status=run.status, scorecard=run.scorecard, metrics=[self._to_evaluation_metric_response(item) for item in metrics if item.run_id == run.id], evaluation_metadata=run.evaluation_metadata, created_at=run.created_at or datetime.now(UTC), updated_at=run.updated_at or datetime.now(UTC)) for run in runs]

    async def metrics(self) -> ReasoningMetricsResponse:
        traces = [self._trace_to_dict(item) for item in await self.repository.list_traces()]
        decisions = [self._decision_to_dict(item) for item in await self.repository.list_decisions()]
        confidence_scores = [self._confidence_to_dict(item) for item in await self.repository.list_confidence_scores()]
        trust_scores = [self._trust_to_dict(item) for item in await self.repository.list_trust_scores()]
        hallucinations = [self._hallucination_to_dict(item) for item in await self.repository.list_hallucinations()]
        validations = [self._validation_to_dict(item) for item in await self.repository.list_decisions()]
        recommendations = [self._recommendation_to_dict(item) for item in await self.repository.list_recommendations()]
        scorecards = [self._scorecard_to_dict(item) for item in await self.repository.list_evaluation_runs()]
        return ReasoningMetricsResponse.model_validate(self.metrics_engine.summarize(traces, decisions, confidence_scores, trust_scores, hallucinations, validations, recommendations, scorecards))

    def _analyze_bundle(self, request: ReasoningRequest) -> dict[str, object]:
        plan = self.planner.plan(request)
        evidence = self.evidence_engine.collect(request)
        risk_request = RiskAnalyzeRequest(query=request.query, current_risk=float(request.metadata.get("current_risk", 50.0)), risk_factors=request.risk_factors, assets=list(request.context.get("assets", [])) if isinstance(request.context.get("assets"), list) else list(request.metadata.get("assets", [])) if isinstance(request.metadata.get("assets"), list) else [], dependencies=list(request.context.get("dependencies", [])) if isinstance(request.context.get("dependencies"), list) else list(request.metadata.get("dependencies", [])) if isinstance(request.metadata.get("dependencies"), list) else [], context=request.context, metadata=request.metadata)
        risk = self.risk_engine.assess(risk_request, evidence, {"overall_confidence": 0.0})
        confidence = self.confidence_engine.score(request, evidence, risk["current_risk"], plan["steps"])
        hallucination = self.hallucination_detector.detect(request, evidence, request.metadata.get("response_text", request.query))
        trust = self.trust_engine.score(request, evidence, confidence, hallucination)
        validation = self.validator.validate(request, evidence, confidence, trust, hallucination, risk["risk_level"])
        quantum = self.quantum_risk_engine.project(risk_request, evidence, risk, int(request.metadata.get("horizon_days", 30)))
        recommendations = self.recommendation_engine.generate(request, evidence, risk, validation)
        explanation = self._explain(request, evidence, confidence, trust, risk, quantum, validation, hallucination, recommendations, plan)
        return {"plan": plan, "evidence": evidence, "confidence": confidence, "trust": trust, "validation": validation, "risk": risk, "quantum": quantum, "recommendations": recommendations, "hallucination": hallucination, "explanation": explanation, "risk_level": risk["risk_level"], "bundle_scorecard": explanation["scorecard"]}

    async def _persist_analysis(self, request: ReasoningRequest, bundle: dict[str, object]) -> ReasoningAnalysisResponse:
        trace = ReasoningTrace(query=request.query, decision_type=request.decision_type, strategy=request.strategy.value, decision_summary=bundle["explanation"]["decision_summary"], decision_graph=bundle["plan"]["graph"], reasoning_steps=bundle["plan"]["steps"], source_references=request.source_references or [item["reference_uri"] for item in bundle["evidence"] if item.get("reference_uri")], knowledge_sources=request.knowledge_sources, mitre_references=request.mitre_references, compliance_references=request.compliance_references, risk_level=bundle["risk_level"], business_impact=bundle["risk"]["business_impact"], technical_impact=bundle["risk"]["technical_impact"], limitations=bundle["explanation"]["limitations"], recommended_actions=bundle["explanation"]["recommended_actions"], alternative_actions=bundle["explanation"]["alternative_actions"], decision_metadata={**request.metadata, "strategy": request.strategy.value}, scorecard=bundle["bundle_scorecard"], input_context={"query": request.query, "context": request.context}, output_context={"risk": bundle["risk"], "confidence": bundle["confidence"], "trust": bundle["trust"]})
        await self.repository.add_trace(trace)
        decision = DecisionRecord(trace_id=trace.id, decision_key=f"decision:{trace.id}", decision_type=request.decision_type, decision_summary=trace.decision_summary, decision_payload={"analysis": bundle["explanation"], "confidence": bundle["confidence"], "trust": bundle["trust"]}, decision_version=1, comparison_payload={"strategy": request.strategy.value}, status="validated" if bundle["validation"]["validated"] else "review", confidence_score=bundle["confidence"]["overall_confidence"], trust_score=bundle["trust"]["overall_trust"], risk_level=bundle["risk_level"], business_impact=trace.business_impact, technical_impact=trace.technical_impact, decision_metadata={**request.metadata, "validated": bundle["validation"]["validated"]})
        await self.repository.add_decision(decision)
        evidence_records = [EvidenceRecord(trace_id=trace.id, decision_id=decision.id, source_type=item["source_type"], source_name=item["source_name"], claim=item["claim"], snippet=item.get("snippet"), reference_uri=item.get("reference_uri"), score=float(item.get("score", 0.0)), verified=bool(item.get("verified", False)), evidence_metadata=dict(item.get("evidence_metadata") or {})) for item in bundle["evidence"]]
        await self.repository.add_evidence(evidence_records)
        confidence_record = ConfidenceScore(trace_id=trace.id, decision_id=decision.id, evidence_strength=bundle["confidence"]["evidence_strength"], knowledge_score=bundle["confidence"]["knowledge_score"], model_score=bundle["confidence"]["model_score"], reasoning_score=bundle["confidence"]["reasoning_score"], data_quality_score=bundle["confidence"]["data_quality_score"], risk_confidence=bundle["confidence"]["risk_confidence"], decision_confidence=bundle["confidence"]["decision_confidence"], overall_confidence=bundle["confidence"]["overall_confidence"], confidence_metadata={"strategy": request.strategy.value})
        trust_record = TrustScore(trace_id=trace.id, decision_id=decision.id, evidence_trust=bundle["trust"]["evidence_trust"], knowledge_trust=bundle["trust"]["knowledge_trust"], reasoning_trust=bundle["trust"]["reasoning_trust"], source_trust=bundle["trust"]["source_trust"], decision_trust=bundle["trust"]["decision_trust"], agent_trust=bundle["trust"]["agent_trust"], model_trust=bundle["trust"]["model_trust"], overall_trust=bundle["trust"]["overall_trust"], trust_metadata={"strategy": request.strategy.value})
        hallucination_record = HallucinationRecord(trace_id=trace.id, decision_id=decision.id, unsupported_claims=bundle["hallucination"]["unsupported_claims"], fact_verification=bundle["hallucination"]["fact_verification"], reference_validation=bundle["hallucination"]["reference_validation"], confidence_penalty=bundle["hallucination"]["confidence_penalty"], response_verified=bundle["hallucination"]["response_verified"], hallucination_metadata={"strategy": request.strategy.value})
        risk_record = RiskProjection(trace_id=trace.id, decision_id=decision.id, risk_level=bundle["risk"]["risk_level"], current_risk=bundle["risk"]["current_risk"], technical_risk=bundle["risk"]["technical_risk"], operational_risk=bundle["risk"]["operational_risk"], business_risk=bundle["risk"]["business_risk"], financial_risk=bundle["risk"]["financial_risk"], compliance_risk=bundle["risk"]["compliance_risk"], reputation_risk=bundle["risk"]["reputation_risk"], infrastructure_risk=bundle["risk"]["infrastructure_risk"], identity_risk=bundle["risk"]["identity_risk"], cloud_risk=bundle["risk"]["cloud_risk"], ai_risk=bundle["risk"]["ai_risk"], supply_chain_risk=bundle["risk"]["supply_chain_risk"], risk_breakdown=bundle["risk"]["risk_breakdown"], business_impact=bundle["risk"]["business_impact"], technical_impact=bundle["risk"]["technical_impact"], risk_metadata=bundle["risk"]["risk_metadata"])
        await self.repository.add_confidence(confidence_record)
        await self.repository.add_trust(trust_record)
        await self.repository.add_hallucination(hallucination_record)
        await self.repository.add_risk_projection(risk_record)
        recommendation_records = [Recommendation(trace_id=trace.id, decision_id=decision.id, priority_rank=item["priority_rank"], category=item["category"], title=item["title"], action=item["action"], horizon=item["horizon"], expected_impact=item["expected_impact"], business_value=item["business_value"], technical_value=item["technical_value"], security_value=item["security_value"], compliance_value=item["compliance_value"], recommendation_metadata=item["recommendation_metadata"]) for item in bundle["recommendations"]]
        await self.repository.add_recommendations(recommendation_records)
        quantum = bundle["quantum"]
        return ReasoningAnalysisResponse(id=trace.id or uuid4(), trace_id=trace.id or uuid4(), decision_id=decision.id or uuid4(), query=trace.query, strategy=trace.strategy, decision_summary=trace.decision_summary, decision_graph=trace.decision_graph, reasoning_steps=trace.reasoning_steps, evidence=[self._to_evidence_response(item) for item in evidence_records], confidence=self._to_confidence_response(confidence_record), trust=self._to_trust_response(trust_record), hallucination=self._to_hallucination_response(hallucination_record), validation=self._to_validation_response(bundle["validation"], trace.id, decision.id), risk=self._to_risk_response(bundle["risk"], trace.id, decision.id), quantum_risk=self._to_quantum_response(quantum, trace.id, decision.id), recommendations=[self._to_recommendation_response(item) for item in recommendation_records], source_references=trace.source_references, knowledge_sources=trace.knowledge_sources, mitre_references=trace.mitre_references, compliance_references=trace.compliance_references, risk_level=trace.risk_level, business_impact=trace.business_impact, technical_impact=trace.technical_impact, limitations=trace.limitations, recommended_actions=trace.recommended_actions, alternative_actions=trace.alternative_actions, decision_metadata=trace.decision_metadata, scorecard=trace.scorecard, created_at=trace.created_at or datetime.now(UTC), updated_at=trace.updated_at or datetime.now(UTC))

    def _explain(self, request: ReasoningRequest, evidence: list[dict[str, object]], confidence: dict[str, float], trust: dict[str, float], risk: dict[str, object], quantum: dict[str, object], validation: dict[str, object], hallucination: dict[str, object], recommendations: list[dict[str, object]], plan: dict[str, object]) -> dict[str, object]:
        summary = f"{request.strategy.value.replace('_', ' ').title()} reasoning for {request.decision_domain}: {len(evidence)} evidence items, confidence {confidence['overall_confidence']:.0f}/100, risk {risk['risk_level']} at {risk['current_risk']:.0f}/100."
        limitations = []
        if not evidence:
            limitations.append("Limited evidence available for full grounding.")
        if hallucination["unsupported_claims"]:
            limitations.append("Unsupported claims were detected and penalized.")
        if not validation["validated"]:
            limitations.append("Validation thresholds were not fully satisfied.")
        return {"decision_summary": summary, "decision_graph": plan["graph"], "reasoning_steps": plan["steps"], "risk_level": risk["risk_level"], "business_impact": risk["business_impact"], "technical_impact": risk["technical_impact"], "limitations": limitations, "recommended_actions": request.recommended_actions or [item["action"] for item in recommendations[:3]], "alternative_actions": request.alternative_actions, "scorecard": {"confidence": confidence["overall_confidence"], "trust": trust["overall_trust"], "risk": risk["current_risk"], "quantum_risk": quantum["projected_risk"], "validation": 100.0 if validation["validated"] else 0.0, "hallucination_penalty": hallucination["confidence_penalty"]}}

    def _risk_bundle(self, request: RiskAnalyzeRequest) -> dict[str, object]:
        evidence = self.evidence_engine.collect(self._risk_reasoning_request(request))
        risk = self.risk_engine.assess(request, evidence, {"overall_confidence": 70.0})
        risk.update({"id": uuid4(), "trace_id": None, "decision_id": None, "created_at": datetime.now(UTC), "updated_at": datetime.now(UTC)})
        return risk

    def _risk_reasoning_request(self, request: RiskAnalyzeRequest) -> ReasoningRequest:
        return ReasoningRequest(query=request.query, strategy=ReasoningStrategy.HYBRID, decision_domain="risk", context=request.context, evidence=[], knowledge_sources=[], mitre_references=[], compliance_references=[], source_references=[], recommended_actions=[], alternative_actions=[], risk_factors=request.risk_factors, metadata=request.metadata)

    def _to_evidence_response(self, record: EvidenceRecord) -> EvidenceResponse:
        return EvidenceResponse(id=record.id or uuid4(), trace_id=record.trace_id, decision_id=record.decision_id, source_type=record.source_type, source_name=record.source_name, claim=record.claim, snippet=record.snippet, reference_uri=record.reference_uri, score=record.score, verified=record.verified, evidence_metadata=record.evidence_metadata, created_at=record.created_at or datetime.now(UTC), updated_at=record.updated_at or datetime.now(UTC))

    def _to_confidence_response(self, record: ConfidenceScore) -> ConfidenceResponse:
        return ConfidenceResponse(id=record.id or uuid4(), trace_id=record.trace_id, decision_id=record.decision_id, evidence_strength=record.evidence_strength, knowledge_score=record.knowledge_score, model_score=record.model_score, reasoning_score=record.reasoning_score, data_quality_score=record.data_quality_score, risk_confidence=record.risk_confidence, decision_confidence=record.decision_confidence, overall_confidence=record.overall_confidence, confidence_metadata=record.confidence_metadata, created_at=record.created_at or datetime.now(UTC), updated_at=record.updated_at or datetime.now(UTC))

    def _to_trust_response(self, record: TrustScore) -> TrustResponse:
        return TrustResponse(id=record.id or uuid4(), trace_id=record.trace_id, decision_id=record.decision_id, evidence_trust=record.evidence_trust, knowledge_trust=record.knowledge_trust, reasoning_trust=record.reasoning_trust, source_trust=record.source_trust, decision_trust=record.decision_trust, agent_trust=record.agent_trust, model_trust=record.model_trust, overall_trust=record.overall_trust, trust_metadata=record.trust_metadata, created_at=record.created_at or datetime.now(UTC), updated_at=record.updated_at or datetime.now(UTC))

    def _to_hallucination_response(self, record: HallucinationRecord) -> HallucinationResponse:
        return HallucinationResponse(id=record.id or uuid4(), trace_id=record.trace_id, decision_id=record.decision_id, unsupported_claims=record.unsupported_claims, fact_verification=record.fact_verification, reference_validation=record.reference_validation, confidence_penalty=record.confidence_penalty, response_verified=record.response_verified, hallucination_metadata=record.hallucination_metadata, created_at=record.created_at or datetime.now(UTC), updated_at=record.updated_at or datetime.now(UTC))

    def _to_risk_response(self, bundle: dict[str, object], trace_id: object = None, decision_id: object = None) -> RiskAssessmentResponse:
        return RiskAssessmentResponse(id=bundle.get("id") or uuid4(), trace_id=trace_id, decision_id=decision_id, risk_level=bundle["risk_level"], current_risk=bundle["current_risk"], technical_risk=bundle["technical_risk"], operational_risk=bundle["operational_risk"], business_risk=bundle["business_risk"], financial_risk=bundle["financial_risk"], compliance_risk=bundle["compliance_risk"], reputation_risk=bundle["reputation_risk"], infrastructure_risk=bundle["infrastructure_risk"], identity_risk=bundle["identity_risk"], cloud_risk=bundle["cloud_risk"], ai_risk=bundle["ai_risk"], supply_chain_risk=bundle["supply_chain_risk"], risk_breakdown=bundle["risk_breakdown"], business_impact=bundle["business_impact"], technical_impact=bundle["technical_impact"], risk_metadata=bundle["risk_metadata"], created_at=bundle.get("created_at") or datetime.now(UTC), updated_at=bundle.get("updated_at") or datetime.now(UTC))

    def _to_quantum_response(self, bundle: dict[str, object], trace_id: object = None, decision_id: object = None) -> QuantumRiskProjectionResponse:
        return QuantumRiskProjectionResponse(id=uuid4(), trace_id=trace_id, decision_id=decision_id, current_risk=bundle["current_risk"], projected_risk=bundle["projected_risk"], worst_case=bundle["worst_case"], best_case=bundle["best_case"], likelihood=bundle["likelihood"], exposure=bundle["exposure"], business_criticality=bundle["business_criticality"], recovery_difficulty=bundle["recovery_difficulty"], confidence=bundle["confidence"], attack_chain=bundle["attack_chain"], quantum_metadata=bundle["quantum_metadata"], created_at=datetime.now(UTC), updated_at=datetime.now(UTC))

    def _to_recommendation_response(self, record: Recommendation) -> RecommendationResponse:
        return RecommendationResponse(id=record.id or uuid4(), trace_id=record.trace_id, decision_id=record.decision_id, priority_rank=record.priority_rank, category=record.category, title=record.title, action=record.action, horizon=record.horizon, expected_impact=record.expected_impact, business_value=record.business_value, technical_value=record.technical_value, security_value=record.security_value, compliance_value=record.compliance_value, recommendation_metadata=record.recommendation_metadata, created_at=record.created_at or datetime.now(UTC), updated_at=record.updated_at or datetime.now(UTC))

    def _to_validation_response(self, validation: dict[str, object], trace_id: object = None, decision_id: object = None) -> DecisionValidationResponse:
        return DecisionValidationResponse(id=uuid4(), trace_id=trace_id, decision_id=decision_id, evidence_completeness=bool(validation["evidence_completeness"]), confidence_threshold_met=bool(validation["confidence_threshold_met"]), policy_compliance=bool(validation["policy_compliance"]), knowledge_freshness=bool(validation["knowledge_freshness"]), risk_threshold_met=bool(validation["risk_threshold_met"]), contradictory_evidence=bool(validation["contradictory_evidence"]), reasoning_quality=bool(validation["reasoning_quality"]), output_integrity=bool(validation["output_integrity"]), validated=bool(validation["validated"]), validation_notes=list(validation["validation_notes"]), validation_metadata={}, created_at=datetime.now(UTC), updated_at=datetime.now(UTC))

    def _to_evaluation_metric_response(self, record: EvaluationMetric) -> EvaluationMetricResponse:
        return EvaluationMetricResponse(id=record.id or uuid4(), run_id=record.run_id, metric_name=record.metric_name, metric_value=record.metric_value, benchmark_value=record.benchmark_value, target_value=record.target_value, passed=record.passed, metric_metadata=record.metric_metadata, created_at=record.created_at or datetime.now(UTC), updated_at=record.updated_at or datetime.now(UTC))

    def _trace_to_dict(self, record: ReasoningTrace) -> dict[str, object]:
        return {"risk_level": record.risk_level, "decision_summary": record.decision_summary}

    def _decision_to_dict(self, record: DecisionRecord) -> dict[str, object]:
        return {"validated": record.status == "validated"}

    def _confidence_to_dict(self, record: ConfidenceScore) -> dict[str, object]:
        return {"overall_confidence": record.overall_confidence}

    def _trust_to_dict(self, record: TrustScore) -> dict[str, object]:
        return {"overall_trust": record.overall_trust}

    def _hallucination_to_dict(self, record: HallucinationRecord) -> dict[str, object]:
        return {"unsupported_claims": record.unsupported_claims, "confidence_penalty": record.confidence_penalty}

    def _validation_to_dict(self, record: DecisionRecord) -> dict[str, object]:
        return {"validated": record.status == "validated"}

    def _recommendation_to_dict(self, record: Recommendation) -> dict[str, object]:
        return {"priority_rank": record.priority_rank, "action": record.action}

    def _scorecard_to_dict(self, record: EvaluationRun) -> dict[str, object]:
        return {"latency_ms": record.evaluation_metadata.get("latency_ms", 0.0), **record.scorecard}

    def _available_evaluation_frameworks(self) -> list[str]:
        frameworks = ["custom"]
        try:
            import importlib.util

            if importlib.util.find_spec("deepeval") is not None:
                frameworks.append("deepeval")
            if importlib.util.find_spec("ragas") is not None:
                frameworks.append("ragas")
        except Exception:
            pass
        return frameworks

    def _cache_key(self, prefix: str, request: object) -> str:
        return cache_key(f"{self.settings.reasoning_redis_cache_prefix}:{prefix}", request.model_dump(mode="json"))

    async def _cache_get(self, key: str) -> dict[str, object] | None:
        if self.redis_client is None:
            return None
        cached = await self.redis_client.get(key)
        return json.loads(cached) if cached else None

    async def _cache_set(self, key: str, payload: dict[str, object], ttl: int) -> None:
        if self.redis_client is None:
            return
        await self.redis_client.set(key, json.dumps(payload), ex=ttl)
