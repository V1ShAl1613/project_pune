"use client";

// Alert center route for triage, assignment, notes, history, export, and bulk actions.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { alertData } from "@/soc/shared/soc-demo-data";
import { alertColumns } from "@/soc/shared/soc-column-helpers";

export default function AlertsPage(): React.JSX.Element {
  return <SocListPage eyebrow="Alert center" title="Alerts" description="Alert table, details, filters, severity, status, timeline, assignment, tags, notes, history, export, and bulk actions." status="triage queue" stats={[{ label: "Alerts", value: String(alertData.length), detail: "Current triage volume" }, { label: "Critical", value: String(alertData.filter((item) => item.severity === "critical").length), detail: "Highest severity items" }]} data={alertData} columns={alertColumns} searchPlaceholder="Search alerts" />;
}
