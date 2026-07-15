"use client";

// Attack graph route using React Flow for incident, IOC, asset, threat, and campaign relationships.
import type { Edge, Node } from "reactflow";

import { SocGraph } from "@/soc/shared/soc-graph";
import { SocShell } from "@/soc/shared/soc-shell";

const nodes: Node[] = [
  { id: "incident", position: { x: 0, y: 120 }, data: { label: "Incident" }, type: "input" },
  { id: "ioc", position: { x: 240, y: 0 }, data: { label: "IOC" } },
  { id: "asset", position: { x: 240, y: 180 }, data: { label: "Asset" } },
  { id: "threat", position: { x: 480, y: 90 }, data: { label: "Threat Actor" }, type: "output" },
  { id: "campaign", position: { x: 720, y: 90 }, data: { label: "Campaign" }, type: "output" },
];

const edges: Edge[] = [
  { id: "e1-2", source: "incident", target: "ioc", animated: true },
  { id: "e1-3", source: "incident", target: "asset", animated: true },
  { id: "e2-4", source: "ioc", target: "threat" },
  { id: "e3-4", source: "asset", target: "threat" },
  { id: "e4-5", source: "threat", target: "campaign" },
];

export default function AttackPage(): React.JSX.Element {
  return <SocShell eyebrow="Attack visualization" title="Attack Graph" description="Attack, incident, IOC, asset, threat, and campaign graphs rendered with React Flow. Kill-chain placeholder and relationship graph support are frontend-only." status="graph workspace" stats={[{ label: "Nodes", value: String(nodes.length), detail: "Graph entities" }, { label: "Edges", value: String(edges.length), detail: "Relationships" }]}><SocGraph title="Attack relationship graph" description="Frontend-only attack map with React Flow." nodes={nodes} edges={edges} /></SocShell>;
}
