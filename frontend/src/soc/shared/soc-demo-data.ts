// Static SOC demo data for frontend-only security operations screens.
export type SocSeverity = "critical" | "high" | "medium" | "low" | "informational";

export type AlertRecord = { id: string; title: string; source: string; severity: SocSeverity; status: string; category: string; analyst: string; tags: string[]; timestamp: string };
export type IncidentRecord = { id: string; title: string; severity: SocSeverity; priority: string; status: string; owner: string; queue: string; createdAt: string };
export type CaseRecord = { id: string; title: string; status: string; priority: string; assignedTo: string; evidenceCount: number; updatedAt: string };
export type InvestigationRecord = { id: string; title: string; status: string; owner: string; evidence: number; bookmarks: number; updatedAt: string };
export type IocRecord = { id: string; indicator: string; type: string; confidence: string; source: string; status: string; tags: string[] };
export type ThreatRecord = { id: string; name: string; category: string; severity: SocSeverity; actor: string; status: string; source: string };
export type AssetRecord = { id: string; name: string; type: string; criticality: string; owner: string; status: string; tags: string[] };
export type EvidenceRecord = { id: string; name: string; type: string; integrity: string; source: string; status: string; updatedAt: string };
export type PlaybookRecord = { id: string; name: string; category: string; status: string; steps: number; owner: string };
export type RiskRecord = { id: string; name: string; category: string; score: number; status: string; owner: string };
export type MitreTechniqueRecord = { id: string; technique: string; tactic: string; coverage: string; status: string; notes: string };

export const alertData: AlertRecord[] = [
  { id: "AL-1001", title: "Suspicious PowerShell execution", source: "EDR", severity: "high", status: "Investigating", category: "Endpoint", analyst: "Maya Singh", tags: ["powershell", "endpoint", "lateral-movement"], timestamp: "2026-07-14T08:40:00Z" },
  { id: "AL-1002", title: "Impossible travel login", source: "IAM", severity: "medium", status: "Open", category: "Identity", analyst: "Alex Hale", tags: ["login", "geo", "auth"], timestamp: "2026-07-14T07:55:00Z" },
  { id: "AL-1003", title: "Malware hash match", source: "Sandbox", severity: "critical", status: "Escalated", category: "Malware", analyst: "Jordan Lee", tags: ["hash", "malware", "ioc"], timestamp: "2026-07-14T06:15:00Z" },
];

export const incidentData: IncidentRecord[] = [
  { id: "INC-2001", title: "Phishing to credential replay", severity: "high", priority: "P1", status: "Contained", owner: "SOC A", queue: "Identity", createdAt: "2026-07-14T07:10:00Z" },
  { id: "INC-2002", title: "Endpoint beaconing campaign", severity: "critical", priority: "P0", status: "Investigating", owner: "SOC B", queue: "Endpoint", createdAt: "2026-07-14T05:30:00Z" },
  { id: "INC-2003", title: "Suspicious cloud privilege grant", severity: "medium", priority: "P2", status: "Open", owner: "SOC C", queue: "Cloud", createdAt: "2026-07-13T18:45:00Z" },
];

export const caseData: CaseRecord[] = [
  { id: "CASE-3001", title: "Executive mailbox compromise", status: "Active", priority: "High", assignedTo: "Maya Singh", evidenceCount: 8, updatedAt: "2026-07-14T08:20:00Z" },
  { id: "CASE-3002", title: "Threat actor infrastructure review", status: "Pending review", priority: "Medium", assignedTo: "Jordan Lee", evidenceCount: 5, updatedAt: "2026-07-13T19:00:00Z" },
];

export const investigationData: InvestigationRecord[] = [
  { id: "INV-4001", title: "Domain pivot investigation", status: "Pinned", owner: "Alex Hale", evidence: 14, bookmarks: 6, updatedAt: "2026-07-14T08:12:00Z" },
  { id: "INV-4002", title: "Process tree reconstruction", status: "Open", owner: "SOC B", evidence: 11, bookmarks: 3, updatedAt: "2026-07-14T07:35:00Z" },
];

export const iocData: IocRecord[] = [
  { id: "IOC-5001", indicator: "185.199.110.153", type: "IP Address", confidence: "High", source: "Threat Intel", status: "Active", tags: ["c2", "network"] },
  { id: "IOC-5002", indicator: "update-secure-login[.]com", type: "Domain", confidence: "Medium", source: "Phishing", status: "Observed", tags: ["phish", "brand"] },
  { id: "IOC-5003", indicator: "b4c7e8f0...", type: "Hash", confidence: "Critical", source: "Sandbox", status: "Confirmed", tags: ["malware"] },
];

export const threatData: ThreatRecord[] = [
  { id: "THR-6001", name: "Sandstorm Drift", category: "APT", severity: "high", actor: "APT Group", status: "Tracking", source: "Threat Intel" },
  { id: "THR-6002", name: "Ransomware affiliate surge", category: "Campaign", severity: "critical", actor: "RaaS", status: "Monitoring", source: "External Feed" },
];

export const assetData: AssetRecord[] = [
  { id: "AST-7001", name: "Core Banking API", type: "Application", criticality: "Critical", owner: "Platform", status: "Protected", tags: ["production", "customer"] },
  { id: "AST-7002", name: "SOC Workstation 14", type: "Endpoint", criticality: "High", owner: "SOC", status: "Monitored", tags: ["analyst", "endpoint"] },
  { id: "AST-7003", name: "Azure SQL Primary", type: "Database", criticality: "Critical", owner: "Data", status: "Protected", tags: ["database", "finance"] },
];

export const evidenceData: EvidenceRecord[] = [
  { id: "EVD-8001", name: "Memory dump", type: "File", integrity: "Verified", source: "EDR", status: "Indexed", updatedAt: "2026-07-14T08:01:00Z" },
  { id: "EVD-8002", name: "Mailbox export", type: "Archive", integrity: "Hash matched", source: "Email", status: "Available", updatedAt: "2026-07-13T21:40:00Z" },
];

export const playbookData: PlaybookRecord[] = [
  { id: "PB-9001", name: "Phishing containment", category: "Identity", status: "Published", steps: 9, owner: "SOC Operations" },
  { id: "PB-9002", name: "Malware triage", category: "Endpoint", status: "Draft", steps: 12, owner: "Threat Intel" },
];

export const riskData: RiskRecord[] = [
  { id: "RISK-1001", name: "Privileged account sprawl", category: "Identity", score: 84, status: "High", owner: "IAM" },
  { id: "RISK-1002", name: "Legacy endpoint exposure", category: "Asset", score: 68, status: "Medium", owner: "SOC" },
];

export const mitreData: MitreTechniqueRecord[] = [
  { id: "T1059", technique: "Command and Scripting Interpreter", tactic: "Execution", coverage: "High", status: "Covered", notes: "Mapped to PowerShell monitoring" },
  { id: "T1110", technique: "Brute Force", tactic: "Credential Access", coverage: "Medium", status: "Partially covered", notes: "Identity heuristics pending backend" },
];
