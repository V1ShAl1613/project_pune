from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

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


@dataclass(slots=True)
class ReasoningRepository:
    session: AsyncSession | None = None
    traces: list[ReasoningTrace] = field(default_factory=list)
    decisions: list[DecisionRecord] = field(default_factory=list)
    evidence_records: list[EvidenceRecord] = field(default_factory=list)
    trust_scores: list[TrustScore] = field(default_factory=list)
    confidence_scores: list[ConfidenceScore] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    risk_projections: list[RiskProjection] = field(default_factory=list)
    evaluation_runs: list[EvaluationRun] = field(default_factory=list)
    evaluation_metrics: list[EvaluationMetric] = field(default_factory=list)
    hallucination_records: list[HallucinationRecord] = field(default_factory=list)

    async def add_trace(self, trace: ReasoningTrace) -> ReasoningTrace:
        return await self._store(self.traces, trace)

    async def add_decision(self, decision: DecisionRecord) -> DecisionRecord:
        return await self._store(self.decisions, decision)

    async def add_evidence(self, records: Sequence[EvidenceRecord]) -> Sequence[EvidenceRecord]:
        stored = []
        for record in records:
            stored.append(await self._store(self.evidence_records, record))
        return stored

    async def add_confidence(self, confidence: ConfidenceScore) -> ConfidenceScore:
        return await self._store(self.confidence_scores, confidence)

    async def add_trust(self, trust: TrustScore) -> TrustScore:
        return await self._store(self.trust_scores, trust)

    async def add_recommendations(self, records: Sequence[Recommendation]) -> Sequence[Recommendation]:
        stored = []
        for record in records:
            stored.append(await self._store(self.recommendations, record))
        return stored

    async def add_risk_projection(self, projection: RiskProjection) -> RiskProjection:
        return await self._store(self.risk_projections, projection)

    async def add_evaluation_run(self, run: EvaluationRun) -> EvaluationRun:
        return await self._store(self.evaluation_runs, run)

    async def add_evaluation_metrics(self, metrics: Sequence[EvaluationMetric]) -> Sequence[EvaluationMetric]:
        stored = []
        for metric in metrics:
            stored.append(await self._store(self.evaluation_metrics, metric))
        return stored

    async def add_hallucination(self, record: HallucinationRecord) -> HallucinationRecord:
        return await self._store(self.hallucination_records, record)

    async def list_traces(self) -> list[ReasoningTrace]:
        return list(self.traces)

    async def list_decisions(self) -> list[DecisionRecord]:
        return list(self.decisions)

    async def list_recommendations(self) -> list[Recommendation]:
        return list(self.recommendations)

    async def list_confidence_scores(self) -> list[ConfidenceScore]:
        return list(self.confidence_scores)

    async def list_trust_scores(self) -> list[TrustScore]:
        return list(self.trust_scores)

    async def list_evaluation_runs(self) -> list[EvaluationRun]:
        return list(self.evaluation_runs)

    async def list_evaluation_metrics(self) -> list[EvaluationMetric]:
        return list(self.evaluation_metrics)

    async def list_hallucinations(self) -> list[HallucinationRecord]:
        return list(self.hallucination_records)

    async def _store(self, collection: list[Any], record: Any) -> Any:
        if self.session is None:
            collection.append(record)
            return record
        self.session.add(record)
        await self.session.flush()
        collection.append(record)
        return record
