from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import uuid4

from redis.asyncio import Redis

from app.core.settings import AppSettings
from app.knowledge.vectorstore.qdrant_store import QdrantVectorStore, VectorPoint
from app.threat.models import AttackPath, GraphEdge, GraphNode, IOC, MITREMapping, ThreatActor, ThreatCampaign, ThreatCorrelation, ThreatEvidence, ThreatHunt, ThreatRecommendation
from app.threat.repositories.threat_repository import ThreatRepository
from app.threat.schemas import (
    AttackPathAnalyzeRequest,
    AttackPathResponse,
    GraphNodeResponse,
    GraphEdgeResponse,
    GraphPathRequest,
    GraphQueryRequest,
    GraphQueryResponse,
    IOCResponse,
    IOCSearchRequest,
    MITREMappingResponse,
    MITREMatrixResponse,
    ThreatAnalysisRequest,
    ThreatAnalysisResponse,
    ThreatCampaignResponse,
    ThreatCorrelateRequest,
    ThreatCorrelationResponse,
    ThreatHuntRequest,
    ThreatHuntResponse,
    ThreatMetricsResponse,
    ThreatActorResponse,
)
from app.threat.shared import GraphBackend, ThreatIntelEngine, build_graph_backend, _clamp, _normalize


@dataclass(slots=True)
class ThreatService:
    repository: ThreatRepository | None
    settings: AppSettings
    redis_client: Redis | None
    logger: logging.Logger
    engine: ThreatIntelEngine = field(init=False)
    graph_backend: GraphBackend = field(init=False)
    vector_store: QdrantVectorStore = field(init=False)

    def __post_init__(self) -> None:
        self.repository = self.repository or ThreatRepository()
        self.engine = ThreatIntelEngine()
        self.graph_backend = GraphBackend()
        self.vector_store = QdrantVectorStore(self.settings)

    async def analyze(self, request: ThreatAnalysisRequest) -> ThreatAnalysisResponse:
        cached = await self._cache_get(self._cache_key("analyze", request))
        if cached:
            return ThreatAnalysisResponse.model_validate(cached)
        evidence = self._collect_evidence(request)
        bundle = self.engine.analyze(request, self.graph_backend, evidence)
        response = await self._persist_analysis(request, bundle)
        await self._cache_set(self._cache_key("analyze", request), response.model_dump(mode="json"), ttl=self.settings.threat_cache_ttl_seconds)
        return response

    async def correlate(self, request: ThreatCorrelateRequest) -> ThreatAnalysisResponse:
        return await self.analyze(request)

    async def hunt(self, request: ThreatHuntRequest) -> ThreatHuntResponse:
        evidence = self._collect_evidence(request)
        iocs = self.engine.normalize_iocs(request.iocs, request.indicators, evidence)
        bundle = self.engine.hunt(request, iocs, self.graph_backend, evidence)
        hunt = ThreatHunt(hunt_type=request.hunt_type.value, query=request.query, status="completed", confidence=bundle["confidence"], findings=bundle["findings"], mitre_mappings=bundle["mitre_mappings"], iocs=bundle["iocs"], graph_relationships=bundle["graph_relationships"], recommendations=bundle["recommendations"], business_impact=bundle["business_impact"], hunt_metadata=bundle["hunt_metadata"])
        await self.repository.add_hunt(hunt)
        for finding in bundle["findings"]:
            await self.repository.add_evidence(ThreatEvidence(correlation_id=None, source_type=finding["finding_type"], source_name=finding["indicator"], content=request.query, reference_uri=None, score=float(finding["confidence"]), evidence_metadata=finding))
        return ThreatHuntResponse(id=hunt.id or uuid4(), hunt_type=hunt.hunt_type, query=hunt.query, status=hunt.status, confidence=hunt.confidence, findings=hunt.findings, mitre_mappings=[self._mitre_payload_response(item) for item in hunt.mitre_mappings], iocs=[IOCResponse.model_validate(item) for item in hunt.iocs], graph_relationships=hunt.graph_relationships, recommendations=hunt.recommendations, business_impact=hunt.business_impact, hunt_metadata=hunt.hunt_metadata, created_at=hunt.created_at or datetime.now(UTC), updated_at=hunt.updated_at or datetime.now(UTC))

    async def list_actors(self) -> list[ThreatActorResponse]:
        return [self._actor_response(item) for item in await self.repository.list_actors()]

    async def list_campaigns(self) -> list[ThreatCampaignResponse]:
        return [self._campaign_response(item) for item in await self.repository.list_campaigns()]

    async def mitre_matrix(self, query: str | None = None) -> MITREMatrixResponse:
        request = ThreatAnalysisRequest(query=query or "enterprise threat matrix")
        matrix = self.engine.build_mitre_matrix(request)
        tactics = sorted({item["tactic"] for item in matrix})
        return MITREMatrixResponse(tactics=tactics, techniques=[{"tactic": item["tactic"], "technique": item["technique"], "sub_technique": item["sub_technique"], "confidence": item["confidence"]} for item in matrix], groups=sorted({item.get("group_name") or "unknown" for item in matrix}), software=sorted({item.get("software_name") or "unknown" for item in matrix}), mitigations=sorted({mitigation for item in matrix for mitigation in item["mitigations"]}), data_sources=sorted({source for item in matrix for source in item["data_sources"]}), detections=sorted({detection for item in matrix for detection in item["detections"]}), version="v15", confidence=max((float(item["confidence"]) for item in matrix), default=60.0))

    async def graph_query(self, request: GraphQueryRequest) -> GraphQueryResponse:
        backend = self._graph_backend()
        payload = self.engine.graph_query(request, backend)
        return GraphQueryResponse.model_validate(payload)

    async def graph_path(self, request: GraphPathRequest) -> dict[str, object]:
        backend = self._graph_backend()
        return self.engine.graph_path(request.source, request.target, backend)

    async def list_iocs(self) -> list[IOCResponse]:
        return [self._ioc_response(item) for item in await self.repository.list_iocs()]

    async def search_iocs(self, request: IOCSearchRequest) -> list[IOCResponse]:
        normalized = self._search_ioc_payloads(request)
        return [IOCResponse.model_validate(item) for item in normalized]

    async def attack_paths(self, request: AttackPathAnalyzeRequest) -> AttackPathResponse:
        backend = self._graph_backend()
        iocs = self.engine.normalize_iocs([], [], [])
        bundle = self.engine.attack_path(request, backend, iocs)
        path = AttackPath(source_asset=request.source_asset, target_asset=request.target_asset, attack_chain=bundle["attack_chain"], lateral_movement=bundle["lateral_movement"], privilege_escalation=bundle["privilege_escalation"], identity_compromise=bundle["identity_compromise"], cloud_attack_path=bundle["cloud_attack_path"], endpoint_attack_path=bundle["endpoint_attack_path"], data_exfiltration=bundle["data_exfiltration"], critical_asset_exposure=bundle["critical_asset_exposure"], business_impact=bundle["business_impact"], likelihood=bundle["likelihood"], confidence=bundle["confidence"], attack_path_metadata=bundle["attack_path_metadata"])
        await self.repository.add_attack_path(path)
        return AttackPathResponse(id=path.id or uuid4(), source_asset=path.source_asset, target_asset=path.target_asset, attack_chain=path.attack_chain, lateral_movement=path.lateral_movement, privilege_escalation=path.privilege_escalation, identity_compromise=path.identity_compromise, cloud_attack_path=path.cloud_attack_path, endpoint_attack_path=path.endpoint_attack_path, data_exfiltration=path.data_exfiltration, critical_asset_exposure=path.critical_asset_exposure, business_impact=path.business_impact, likelihood=path.likelihood, confidence=path.confidence, attack_path_metadata=path.attack_path_metadata, created_at=path.created_at or datetime.now(UTC), updated_at=path.updated_at or datetime.now(UTC))

    async def metrics(self) -> ThreatMetricsResponse:
        iocs = await self.repository.list_iocs()
        correlations = await self.repository.list_correlations()
        hunts = await self.repository.list_hunts()
        attack_paths = await self.repository.list_attack_paths()
        actors = await self.repository.list_actors()
        evidence = await self.repository.list_evidence()
        mitre_mappings = await self.repository.list_mitre_mappings()
        scorecard = self.engine.metrics(len(actors), len(iocs), len(correlations), len(hunts), len(attack_paths), [float(item.confidence) for item in actors], [hunt.__dict__ for hunt in hunts], self._graph_backend(), len(mitre_mappings))
        return ThreatMetricsResponse.model_validate(scorecard)

    async def _persist_analysis(self, request: ThreatAnalysisRequest, bundle: dict[str, object]) -> ThreatAnalysisResponse:
        ioc_records = [IOC(indicator=item["indicator"], indicator_type=item["indicator_type"], normalized_indicator=item["normalized_indicator"], source=item["source"], description=item["description"], confidence=item["confidence"], first_seen=item["first_seen"], last_seen=item["last_seen"], status=item["status"], ioc_metadata=item["ioc_metadata"]) for item in bundle["iocs"]]
        await self.repository.add_iocs(ioc_records)
        for ioc in ioc_records:
            self.graph_backend.add_node(ioc.normalized_indicator, "ioc", ioc.indicator, indicator=ioc.indicator, indicator_type=ioc.indicator_type, confidence=ioc.confidence)
        for index, mapping in enumerate(bundle["mitre_mappings"], start=1):
            mitre = MITREMapping(framework=mapping["framework"], tactic=mapping["tactic"], technique=mapping["technique"], sub_technique=mapping.get("sub_technique"), group_name=mapping.get("group_name"), software_name=mapping.get("software_name"), mitigations=mapping["mitigations"], data_sources=mapping["data_sources"], detections=mapping["detections"], procedure_examples=mapping["procedure_examples"], version=mapping["version"], confidence=float(mapping["confidence"]), mapping_metadata=mapping["mapping_metadata"])
            await self.repository.add_mitre_mapping(mitre)
        actor_records = [ThreatActor(name=item.name, aliases=item.aliases, motivations=item.motivations, geography=item.geography, capabilities=item.capabilities, techniques=item.techniques, campaigns=item.campaigns, infrastructure=item.infrastructure, confidence=item.confidence, actor_metadata=item.actor_metadata) for item in bundle["threat_actors"]]
        campaign_records = [ThreatCampaign(name=item.name, aliases=item.aliases, objective=item.objective, impact=item.impact, techniques=item.techniques, infrastructure=item.infrastructure, confidence=item.confidence, campaign_metadata=item.campaign_metadata) for item in bundle["campaigns"]]
        for actor in actor_records:
            await self.repository.add_actor(actor)
        for campaign in campaign_records:
            await self.repository.add_campaign(campaign)
        correlations = []
        for item in bundle["correlations"]:
            correlation = ThreatCorrelation(correlation_type=item["correlation_type"], entity_type=item["entity_type"], entity_value=item["entity_value"], confidence=float(item["confidence"]), evidence_count=int(item["evidence_count"]), related_entities=item["related_entities"], timeline=item["timeline"], attribution=item.get("attribution"), correlation_metadata=item["correlation_metadata"])
            await self.repository.add_correlation(correlation)
            correlations.append(correlation)
        paths = []
        for item in bundle["attack_paths"]:
            path = AttackPath(source_asset=item["source_asset"], target_asset=item["target_asset"], attack_chain=item["attack_chain"], lateral_movement=item["lateral_movement"], privilege_escalation=item["privilege_escalation"], identity_compromise=item["identity_compromise"], cloud_attack_path=item["cloud_attack_path"], endpoint_attack_path=item["endpoint_attack_path"], data_exfiltration=item["data_exfiltration"], critical_asset_exposure=item["critical_asset_exposure"], business_impact=item["business_impact"], likelihood=float(item["likelihood"]), confidence=float(item["confidence"]), attack_path_metadata=item["attack_path_metadata"])
            await self.repository.add_attack_path(path)
            paths.append(path)
        recommendations = []
        for index, recommendation in enumerate(bundle["explainability"]["recommendations"], start=1):
            record = ThreatRecommendation(priority_rank=index, title=f"Recommendation {index}", action=recommendation, business_impact=bundle["business_impact"], technical_impact=bundle["technical_impact"], recommendation_metadata={"query": request.query, "priority_rank": index})
            await self.repository.add_recommendation(record)
            recommendations.append(record)
        confidence = float(bundle["confidence"])
        return ThreatAnalysisResponse(id=uuid4(), query=request.query, evidence=bundle["evidence"], mitre_mappings=[self._mitre_response(item) for item in await self.repository.list_mitre_mappings()], mitre_atlas_mappings=[self._mitre_response(item) for item in await self.repository.list_mitre_mappings()], kill_chain_stage=bundle["kill_chain_stage"], diamond_model=bundle["diamond_model"], graph_relationships=bundle["graph_relationships"], attack_paths=[self._attack_path_response(item) for item in paths], correlations=[self._correlation_response(item) for item in correlations], iocs=[self._ioc_response(item) for item in ioc_records], threat_actors=[self._actor_response(item) for item in actor_records], campaigns=[self._campaign_response(item) for item in campaign_records], confidence=confidence, confidence_breakdown=bundle["confidence_breakdown"], recommendations=bundle["recommendations"], business_impact=bundle["business_impact"], technical_impact=bundle["technical_impact"], timeline=bundle["timeline"], explainability=bundle["explainability"], metadata=request.metadata, created_at=datetime.now(UTC), updated_at=datetime.now(UTC))

    def _collect_evidence(self, request: ThreatAnalysisRequest) -> list[dict[str, object]]:
        evidence = []
        for indicator in request.indicators:
            text = str(indicator.get("indicator") or indicator.get("value") or indicator.get("text") or request.query)
            evidence.append({"source_type": str(indicator.get("source_type") or "indicator"), "source_name": str(indicator.get("source_name") or request.metadata.get("source") or "unknown"), "indicator": text, "content": str(indicator.get("content") or text), "reference_uri": indicator.get("reference_uri"), "score": float(indicator.get("score") or 60.0), "timestamp": indicator.get("timestamp") or datetime.now(UTC), "evidence_metadata": dict(indicator.get("metadata") or {})})
        for ref in request.source_references:
            evidence.append({"source_type": "reference", "source_name": "source_reference", "indicator": ref, "content": ref, "reference_uri": ref, "score": 75.0, "timestamp": datetime.now(UTC), "evidence_metadata": {"origin": "reference"}})
        if request.context:
            for key, value in request.context.items():
                content = f"{key}: {value}"
                evidence.append({"source_type": "context", "source_name": key, "indicator": content, "content": content, "reference_uri": None, "score": 50.0, "timestamp": datetime.now(UTC), "evidence_metadata": {"origin": "context"}})
        return evidence or [{"source_type": "query", "source_name": "analysis", "indicator": request.query, "content": request.query, "reference_uri": None, "score": 50.0, "timestamp": datetime.now(UTC), "evidence_metadata": {"origin": "fallback"}}]

    def _search_ioc_payloads(self, request: IOCSearchRequest) -> list[dict[str, object]]:
        query = request.query.strip().lower()
        candidates = [ioc for ioc in self.repository.iocs if query in ioc.indicator.lower() or query in ioc.normalized_indicator.lower() or query in (ioc.description or "").lower()]
        if request.indicator_type:
            candidates = [ioc for ioc in candidates if ioc.indicator_type == request.indicator_type.value]
        payloads = [self._ioc_response(ioc).model_dump(mode="json") for ioc in candidates]
        if request.deduplicate:
            deduped = {item["normalized_indicator"]: item for item in payloads}
            payloads = list(deduped.values())
        return payloads[: request.limit]

    def _graph_backend(self) -> GraphBackend:
        return build_graph_backend([{"node_key": node.node_key, "node_type": node.node_type, "label": node.label, "properties": node.properties} for node in self.repository.graph_nodes], [{"source": edge.source_node_key, "target": edge.target_node_key, "relation_type": edge.relation_type, "confidence": edge.confidence, "metadata": edge.edge_metadata} for edge in self.repository.graph_edges])

    def _ioc_response(self, ioc: IOC) -> IOCResponse:
        return IOCResponse(id=ioc.id or uuid4(), indicator=ioc.indicator, indicator_type=ioc.indicator_type, normalized_indicator=ioc.normalized_indicator, source=ioc.source, description=ioc.description, confidence=ioc.confidence, first_seen=ioc.first_seen, last_seen=ioc.last_seen, status=ioc.status, ioc_metadata=ioc.ioc_metadata, created_at=ioc.created_at or datetime.now(UTC), updated_at=ioc.updated_at or datetime.now(UTC))

    def _actor_response(self, actor: ThreatActor) -> ThreatActorResponse:
        return ThreatActorResponse(id=actor.id or uuid4(), name=actor.name, aliases=actor.aliases, motivations=actor.motivations, geography=actor.geography, capabilities=actor.capabilities, techniques=actor.techniques, campaigns=actor.campaigns, infrastructure=actor.infrastructure, confidence=actor.confidence, actor_metadata=actor.actor_metadata, created_at=actor.created_at or datetime.now(UTC), updated_at=actor.updated_at or datetime.now(UTC))

    def _campaign_response(self, campaign: ThreatCampaign) -> ThreatCampaignResponse:
        return ThreatCampaignResponse(id=campaign.id or uuid4(), name=campaign.name, aliases=campaign.aliases, objective=campaign.objective, impact=campaign.impact, techniques=campaign.techniques, infrastructure=campaign.infrastructure, confidence=campaign.confidence, campaign_metadata=campaign.campaign_metadata, created_at=campaign.created_at or datetime.now(UTC), updated_at=campaign.updated_at or datetime.now(UTC))

    def _mitre_response(self, mapping: MITREMapping) -> MITREMappingResponse:
        return MITREMappingResponse(id=mapping.id or uuid4(), framework=mapping.framework, tactic=mapping.tactic, technique=mapping.technique, sub_technique=mapping.sub_technique, group_name=mapping.group_name, software_name=mapping.software_name, mitigations=mapping.mitigations, data_sources=mapping.data_sources, detections=mapping.detections, procedure_examples=mapping.procedure_examples, version=mapping.version, confidence=mapping.confidence, mapping_metadata=mapping.mapping_metadata, created_at=mapping.created_at or datetime.now(UTC), updated_at=mapping.updated_at or datetime.now(UTC))

    def _mitre_payload_response(self, mapping: dict[str, object]) -> MITREMappingResponse:
        now = datetime.now(UTC)
        return MITREMappingResponse(id=mapping.get("id") or uuid4(), framework=str(mapping.get("framework") or "mitre_attack"), tactic=str(mapping.get("tactic") or "unknown"), technique=str(mapping.get("technique") or "unknown"), sub_technique=mapping.get("sub_technique"), group_name=mapping.get("group_name"), software_name=mapping.get("software_name"), mitigations=list(mapping.get("mitigations") or []), data_sources=list(mapping.get("data_sources") or []), detections=list(mapping.get("detections") or []), procedure_examples=list(mapping.get("procedure_examples") or []), version=str(mapping.get("version") or "v1"), confidence=float(mapping.get("confidence") or 0.0), mapping_metadata=dict(mapping.get("mapping_metadata") or {}), created_at=mapping.get("created_at") or now, updated_at=mapping.get("updated_at") or now)

    def _correlation_response(self, correlation: ThreatCorrelation) -> ThreatCorrelationResponse:
        return ThreatCorrelationResponse(id=correlation.id or uuid4(), correlation_type=correlation.correlation_type, entity_type=correlation.entity_type, entity_value=correlation.entity_value, confidence=correlation.confidence, evidence_count=correlation.evidence_count, related_entities=correlation.related_entities, timeline=correlation.timeline, attribution=correlation.attribution, correlation_metadata=correlation.correlation_metadata, created_at=correlation.created_at or datetime.now(UTC), updated_at=correlation.updated_at or datetime.now(UTC))

    def _attack_path_response(self, attack_path: AttackPath) -> AttackPathResponse:
        return AttackPathResponse(id=attack_path.id or uuid4(), source_asset=attack_path.source_asset, target_asset=attack_path.target_asset, attack_chain=attack_path.attack_chain, lateral_movement=attack_path.lateral_movement, privilege_escalation=attack_path.privilege_escalation, identity_compromise=attack_path.identity_compromise, cloud_attack_path=attack_path.cloud_attack_path, endpoint_attack_path=attack_path.endpoint_attack_path, data_exfiltration=attack_path.data_exfiltration, critical_asset_exposure=attack_path.critical_asset_exposure, business_impact=attack_path.business_impact, likelihood=attack_path.likelihood, confidence=attack_path.confidence, attack_path_metadata=attack_path.attack_path_metadata, created_at=attack_path.created_at or datetime.now(UTC), updated_at=attack_path.updated_at or datetime.now(UTC))

    async def _cache_get(self, key: str) -> dict[str, object] | None:
        if self.redis_client is None:
            return None
        cached = await self.redis_client.get(key)
        return json.loads(cached) if cached else None

    async def _cache_set(self, key: str, payload: dict[str, object], ttl: int) -> None:
        if self.redis_client is None:
            return
        await self.redis_client.set(key, json.dumps(payload), ex=ttl)

    def _cache_key(self, prefix: str, request: object) -> str:
        return f"{self.settings.threat_redis_cache_prefix}:{prefix}:{hash(json.dumps(request.model_dump(mode='json'), sort_keys=True))}"
