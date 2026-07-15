// Shared TanStack column helpers for SOC list views.
import { createColumnHelper } from "@tanstack/react-table";

import { Badge } from "@/components/ui/surfaces";
import type { AlertRecord, AssetRecord, CaseRecord, EvidenceRecord, IncidentRecord, InvestigationRecord, IocRecord, MitreTechniqueRecord, PlaybookRecord, RiskRecord, ThreatRecord } from "@/soc/shared/soc-demo-data";

const alertHelper = createColumnHelper<AlertRecord>();
export const alertColumns = [alertHelper.accessor("id", { header: "Alert ID" }), alertHelper.accessor("title", { header: "Title", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }), alertHelper.accessor("severity", { header: "Severity", cell: (info) => <Badge tone={info.getValue() === "critical" || info.getValue() === "high" ? "danger" : info.getValue() === "medium" ? "warning" : "neutral"}>{info.getValue()}</Badge> }), alertHelper.accessor("status", { header: "Status" }), alertHelper.accessor("source", { header: "Source" }), alertHelper.accessor("analyst", { header: "Analyst" })];

const incidentHelper = createColumnHelper<IncidentRecord>();
export const incidentColumns = [incidentHelper.accessor("id", { header: "Incident ID" }), incidentHelper.accessor("title", { header: "Title", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }), incidentHelper.accessor("severity", { header: "Severity", cell: (info) => <Badge tone={info.getValue() === "critical" || info.getValue() === "high" ? "danger" : info.getValue() === "medium" ? "warning" : "neutral"}>{info.getValue()}</Badge> }), incidentHelper.accessor("priority", { header: "Priority" }), incidentHelper.accessor("status", { header: "Status" }), incidentHelper.accessor("owner", { header: "Owner" })];

const caseHelper = createColumnHelper<CaseRecord>();
export const caseColumns = [caseHelper.accessor("id", { header: "Case ID" }), caseHelper.accessor("title", { header: "Title", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }), caseHelper.accessor("priority", { header: "Priority" }), caseHelper.accessor("status", { header: "Status" }), caseHelper.accessor("assignedTo", { header: "Assigned to" }), caseHelper.accessor("evidenceCount", { header: "Evidence" })];

const investigationHelper = createColumnHelper<InvestigationRecord>();
export const investigationColumns = [investigationHelper.accessor("id", { header: "Investigation ID" }), investigationHelper.accessor("title", { header: "Title", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }), investigationHelper.accessor("status", { header: "Status" }), investigationHelper.accessor("owner", { header: "Owner" }), investigationHelper.accessor("evidence", { header: "Evidence" }), investigationHelper.accessor("bookmarks", { header: "Bookmarks" })];

const iocHelper = createColumnHelper<IocRecord>();
export const iocColumns = [iocHelper.accessor("indicator", { header: "Indicator", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }), iocHelper.accessor("type", { header: "Type" }), iocHelper.accessor("confidence", { header: "Confidence" }), iocHelper.accessor("source", { header: "Source" }), iocHelper.accessor("status", { header: "Status" })];

const threatHelper = createColumnHelper<ThreatRecord>();
export const threatColumns = [threatHelper.accessor("name", { header: "Threat", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }), threatHelper.accessor("category", { header: "Category" }), threatHelper.accessor("severity", { header: "Severity", cell: (info) => <Badge tone={info.getValue() === "critical" || info.getValue() === "high" ? "danger" : info.getValue() === "medium" ? "warning" : "neutral"}>{info.getValue()}</Badge> }), threatHelper.accessor("actor", { header: "Actor" }), threatHelper.accessor("status", { header: "Status" }), threatHelper.accessor("source", { header: "Source" })];

const assetHelper = createColumnHelper<AssetRecord>();
export const assetColumns = [assetHelper.accessor("name", { header: "Asset", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }), assetHelper.accessor("type", { header: "Type" }), assetHelper.accessor("criticality", { header: "Criticality" }), assetHelper.accessor("owner", { header: "Owner" }), assetHelper.accessor("status", { header: "Status" })];

const evidenceHelper = createColumnHelper<EvidenceRecord>();
export const evidenceColumns = [evidenceHelper.accessor("name", { header: "Evidence", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }), evidenceHelper.accessor("type", { header: "Type" }), evidenceHelper.accessor("integrity", { header: "Integrity" }), evidenceHelper.accessor("source", { header: "Source" }), evidenceHelper.accessor("status", { header: "Status" })];

const playbookHelper = createColumnHelper<PlaybookRecord>();
export const playbookColumns = [playbookHelper.accessor("name", { header: "Playbook", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }), playbookHelper.accessor("category", { header: "Category" }), playbookHelper.accessor("status", { header: "Status" }), playbookHelper.accessor("steps", { header: "Steps" }), playbookHelper.accessor("owner", { header: "Owner" })];

const riskHelper = createColumnHelper<RiskRecord>();
export const riskColumns = [riskHelper.accessor("name", { header: "Risk", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }), riskHelper.accessor("category", { header: "Category" }), riskHelper.accessor("score", { header: "Score" }), riskHelper.accessor("status", { header: "Status" }), riskHelper.accessor("owner", { header: "Owner" })];

const mitreHelper = createColumnHelper<MitreTechniqueRecord>();
export const mitreColumns = [mitreHelper.accessor("id", { header: "Technique ID" }), mitreHelper.accessor("technique", { header: "Technique", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }), mitreHelper.accessor("tactic", { header: "Tactic" }), mitreHelper.accessor("coverage", { header: "Coverage" }), mitreHelper.accessor("status", { header: "Status" })];
