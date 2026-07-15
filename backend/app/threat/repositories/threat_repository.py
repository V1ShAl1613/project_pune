from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.threat.models import AttackPath, GraphEdge, GraphNode, IOC, MITREMapping, ThreatActor, ThreatCampaign, ThreatCorrelation, ThreatEvidence, ThreatHunt, ThreatRecommendation


@dataclass(slots=True)
class ThreatRepository:
    session: AsyncSession | None = None
    threat_actors: list[ThreatActor] = field(default_factory=list)
    campaigns: list[ThreatCampaign] = field(default_factory=list)
    iocs: list[IOC] = field(default_factory=list)
    attack_paths: list[AttackPath] = field(default_factory=list)
    graph_nodes: list[GraphNode] = field(default_factory=list)
    graph_edges: list[GraphEdge] = field(default_factory=list)
    threat_correlations: list[ThreatCorrelation] = field(default_factory=list)
    mitre_mappings: list[MITREMapping] = field(default_factory=list)
    threat_hunts: list[ThreatHunt] = field(default_factory=list)
    threat_evidence: list[ThreatEvidence] = field(default_factory=list)
    threat_recommendations: list[ThreatRecommendation] = field(default_factory=list)

    async def add_actor(self, actor: ThreatActor) -> ThreatActor:
        return await self._store(self.threat_actors, actor)

    async def add_campaign(self, campaign: ThreatCampaign) -> ThreatCampaign:
        return await self._store(self.campaigns, campaign)

    async def add_iocs(self, iocs: list[IOC]) -> list[IOC]:
        stored = []
        for ioc in iocs:
            stored.append(await self._store(self.iocs, ioc))
        return stored

    async def add_attack_path(self, attack_path: AttackPath) -> AttackPath:
        return await self._store(self.attack_paths, attack_path)

    async def add_graph_node(self, node: GraphNode) -> GraphNode:
        return await self._store(self.graph_nodes, node)

    async def add_graph_edge(self, edge: GraphEdge) -> GraphEdge:
        return await self._store(self.graph_edges, edge)

    async def add_correlation(self, correlation: ThreatCorrelation) -> ThreatCorrelation:
        return await self._store(self.threat_correlations, correlation)

    async def add_mitre_mapping(self, mapping: MITREMapping) -> MITREMapping:
        return await self._store(self.mitre_mappings, mapping)

    async def add_hunt(self, hunt: ThreatHunt) -> ThreatHunt:
        return await self._store(self.threat_hunts, hunt)

    async def add_evidence(self, evidence: ThreatEvidence) -> ThreatEvidence:
        return await self._store(self.threat_evidence, evidence)

    async def add_recommendation(self, recommendation: ThreatRecommendation) -> ThreatRecommendation:
        return await self._store(self.threat_recommendations, recommendation)

    async def list_actors(self) -> list[ThreatActor]:
        return list(self.threat_actors)

    async def list_campaigns(self) -> list[ThreatCampaign]:
        return list(self.campaigns)

    async def list_iocs(self) -> list[IOC]:
        return list(self.iocs)

    async def list_attack_paths(self) -> list[AttackPath]:
        return list(self.attack_paths)

    async def list_graph_nodes(self) -> list[GraphNode]:
        return list(self.graph_nodes)

    async def list_graph_edges(self) -> list[GraphEdge]:
        return list(self.graph_edges)

    async def list_correlations(self) -> list[ThreatCorrelation]:
        return list(self.threat_correlations)

    async def list_mitre_mappings(self) -> list[MITREMapping]:
        return list(self.mitre_mappings)

    async def list_hunts(self) -> list[ThreatHunt]:
        return list(self.threat_hunts)

    async def list_evidence(self) -> list[ThreatEvidence]:
        return list(self.threat_evidence)

    async def list_recommendations(self) -> list[ThreatRecommendation]:
        return list(self.threat_recommendations)

    async def _store(self, collection: list[Any], record: Any) -> Any:
        if self.session is None:
            collection.append(record)
            return record
        self.session.add(record)
        await self.session.flush()
        collection.append(record)
        return record
