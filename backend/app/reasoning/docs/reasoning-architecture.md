# Reasoning Architecture

The reasoning layer turns enterprise AI output into a structured, explainable decision workflow.

## Pipeline

1. Plan the decision path with sequential, hierarchical, graph, rule-based, or hybrid reasoning.
2. Collect evidence from the request context, explicit references, knowledge sources, MITRE references, and compliance references.
3. Rank and validate evidence.
4. Score confidence, trust, and hallucination risk.
5. Assess business and technical risk.
6. Project future cascading risk through the quantum risk model.
7. Generate prioritized recommendations.
8. Emit the final explainable decision payload.

## Outputs

Every analysis response includes:

- Decision summary
- Evidence
- Confidence
- Source references
- Knowledge sources
- MITRE references
- Compliance references
- Risk level
- Business impact
- Technical impact
- Limitations
- Recommended actions
- Alternative actions

## API Surface

- `POST /reasoning/analyze`
- `POST /reasoning/validate`
- `POST /reasoning/explain`
- `POST /reasoning/evaluate`
- `POST /risk/analyze`
- `POST /risk/project`
- `GET /recommendations`
- `GET /confidence`
- `GET /trust`
- `GET /evaluations`
- `GET /metrics`

## Persistence

The ORM layer stores:

- `ReasoningTrace`
- `DecisionRecord`
- `EvidenceRecord`
- `ConfidenceScore`
- `TrustScore`
- `Recommendation`
- `RiskProjection`
- `EvaluationRun`
- `EvaluationMetric`
- `HallucinationRecord`

## Evaluation

The evaluation engine ships with custom enterprise metrics and can detect optional `deepeval` and `ragas` installations at runtime for reporting.
