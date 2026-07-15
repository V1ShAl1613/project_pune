# Threat Intelligence Architecture

The threat intelligence layer correlates indicators, MITRE ATT&CK, kill chain stages, graph relationships, and attack paths into a single explainable SOC workflow.

## Core Flow

1. Normalize IOCs and indicators.
2. Derive MITRE ATT&CK and MITRE ATLAS mappings.
3. Map the activity to the Cyber Kill Chain.
4. Build a Diamond Model representation.
5. Resolve entities and create graph nodes and edges.
6. Correlate alerts, incidents, and historical events.
7. Analyze attack paths and risk propagation.
8. Produce hunting guidance and recommendations.

## APIs

- `POST /threats/analyze`
- `POST /threats/correlate`
- `POST /threats/hunt`
- `GET /threats/actors`
- `GET /threats/campaigns`
- `GET /mitre/matrix`
- `POST /graph/query`
- `GET /graph/path`
- `GET /iocs`
- `POST /iocs/search`
- `POST /attack-paths/analyze`

## Storage

The persistence layer stores:

- `ThreatActor`
- `ThreatCampaign`
- `IOC`
- `AttackPath`
- `GraphNode`
- `GraphEdge`
- `ThreatCorrelation`
- `MITREMapping`
- `ThreatHunt`
- `ThreatEvidence`
- `ThreatRecommendation`
