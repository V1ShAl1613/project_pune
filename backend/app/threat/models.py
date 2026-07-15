from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.database.models.base import BaseModel, TimestampMixin, UUIDMixin


class ThreatActor(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "threat_actors"
    __table_args__ = (UniqueConstraint("name", name="uq_threat_actors_name"),)

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    aliases: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    motivations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    geography: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    capabilities: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    techniques: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    campaigns: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    infrastructure: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    actor_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ThreatCampaign(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "campaigns"
    __table_args__ = (UniqueConstraint("name", name="uq_campaigns_name"),)

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    aliases: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    objective: Mapped[str] = mapped_column(Text, nullable=False, default="")
    impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    techniques: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    infrastructure: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    campaign_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class IOC(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "iocs"
    __table_args__ = (UniqueConstraint("normalized_indicator", name="uq_iocs_normalized_indicator"),)

    indicator: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    indicator_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    normalized_indicator: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(255), nullable=False, default="unknown")
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")
    ioc_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class AttackPath(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "attack_paths"

    source_asset: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_asset: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    attack_chain: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    lateral_movement: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    privilege_escalation: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    identity_compromise: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    cloud_attack_path: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    endpoint_attack_path: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    data_exfiltration: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    critical_asset_exposure: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    business_impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    likelihood: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    attack_path_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class GraphNode(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "graph_nodes"
    __table_args__ = (UniqueConstraint("node_key", name="uq_graph_nodes_node_key"),)

    node_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    node_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    properties: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)


class GraphEdge(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "graph_edges"

    source_node_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    target_node_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    edge_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ThreatCorrelation(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "threat_correlations"

    correlation_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    entity_value: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    related_entities: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    timeline: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    attribution: Mapped[str | None] = mapped_column(String(255), nullable=True)
    correlation_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class MITREMapping(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "mitre_mappings"

    framework: Mapped[str] = mapped_column(String(64), nullable=False, default="mitre_attack")
    tactic: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    technique: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    sub_technique: Mapped[str | None] = mapped_column(String(255), nullable=True)
    group_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    software_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mitigations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    data_sources: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    detections: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    procedure_examples: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    version: Mapped[str] = mapped_column(String(32), nullable=False, default="v1")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    mapping_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ThreatHunt(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "threat_hunts"

    hunt_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="completed")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    findings: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    mitre_mappings: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    iocs: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    graph_relationships: Mapped[list[dict[str, object]]] = mapped_column(JSON, nullable=False, default=list)
    recommendations: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    business_impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    hunt_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ThreatEvidence(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "threat_evidence"

    correlation_id: Mapped[UUID | None] = mapped_column(Uuid(as_uuid=True), ForeignKey("threat_correlations.id", ondelete="SET NULL"), nullable=True, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    reference_uri: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    evidence_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)


class ThreatRecommendation(BaseModel, UUIDMixin, TimestampMixin):
    __tablename__ = "threat_recommendations"

    priority_rank: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    business_impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    technical_impact: Mapped[str] = mapped_column(Text, nullable=False, default="")
    recommendation_metadata: Mapped[dict[str, object]] = mapped_column(JSON, nullable=False, default=dict)
