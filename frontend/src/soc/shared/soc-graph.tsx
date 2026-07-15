"use client";

// React Flow graph surface for attack, incident, asset, threat, and IOC relationships.
import ReactFlow, { Background, Controls, MiniMap, type Edge, type Node } from "reactflow";
import "reactflow/dist/style.css";

import { Card } from "@/components/ui/surfaces";

type GraphNode = Node;
type GraphEdge = Edge;

export function SocGraph({ title, description, nodes, edges }: { title: string; description: string; nodes: GraphNode[]; edges: GraphEdge[] }): React.JSX.Element {
  return <Card className="space-y-4"><div><h3 className="text-base font-semibold text-text">{title}</h3><p className="text-sm text-muted">{description}</p></div><div className="h-[32rem] rounded-2xl border border-line bg-canvas"><ReactFlow nodes={nodes} edges={edges} fitView><Background /><Controls /><MiniMap /></ReactFlow></div></Card>;
}
