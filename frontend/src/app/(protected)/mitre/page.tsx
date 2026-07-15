"use client";

// MITRE ATT&CK frontend-only route for matrix, technique browser, tactic browser, and coverage.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { mitreData } from "@/soc/shared/soc-demo-data";
import { mitreColumns } from "@/soc/shared/soc-column-helpers";

export default function MitrePage(): React.JSX.Element {
  return <SocListPage eyebrow="MITRE ATT&CK" title="MITRE Matrix" description="Technique browser, tactic browser, details, filters, navigator, heatmap placeholder, relationships, and coverage view." status="coverage mapping" stats={[{ label: "Techniques", value: String(mitreData.length), detail: "Mapped techniques" }, { label: "Coverage", value: "Ready", detail: "Frontend matrix scaffold" }]} data={mitreData} columns={mitreColumns} searchPlaceholder="Search techniques" />;
}
