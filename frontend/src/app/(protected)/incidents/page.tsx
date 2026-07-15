"use client";

// Incident management route for the SOC workspace.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { incidentData } from "@/soc/shared/soc-demo-data";
import { incidentColumns } from "@/soc/shared/soc-column-helpers";

export default function IncidentsPage(): React.JSX.Element {
  return <SocListPage eyebrow="Incident management" title="Incidents" description="Incident queue, details, assignment, priority, severity, tags, resolution, and history." status="incident response" stats={[{ label: "Incidents", value: String(incidentData.length), detail: "Open response items" }, { label: "Critical", value: String(incidentData.filter((item) => item.severity === "critical").length), detail: "Immediate action required" }]} data={incidentData} columns={incidentColumns} searchPlaceholder="Search incidents" />;
}
