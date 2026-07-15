// SOC icon registry used by dashboards, lists, and graph views.
import { Activity, AlertTriangle, Archive, BookMarked, Bug, ClipboardList, Cpu, FileSearch, GitBranch, Globe, Layers3, Map, MapPinned, ShieldAlert, ShieldCheck, Siren, SquareTerminal, Target, Waves, Workflow, Zap } from "lucide-react";

export const socIcons = {
  dashboard: Activity,
  alerts: Siren,
  incidents: AlertTriangle,
  cases: ClipboardList,
  investigation: FileSearch,
  timeline: GitBranch,
  iocs: Target,
  threats: ShieldAlert,
  intel: Globe,
  assets: Layers3,
  evidence: Archive,
  playbooks: Workflow,
  workbench: SquareTerminal,
  mitre: Map,
  attack: MapPinned,
  malware: Bug,
  vulnerabilities: ShieldCheck,
  risk: Waves,
  quickActions: BookMarked,
  health: Cpu,
  response: Zap,
};
