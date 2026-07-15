"use client";

// Threat intelligence overview route built on the SOC list-page primitives.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { threatData } from "@/soc/shared/soc-demo-data";
import { threatColumns } from "@/soc/shared/soc-column-helpers";

export default function ThreatCenterPage(): React.JSX.Element {
  return <SocListPage eyebrow="Threat intelligence" title="Threat Center" description="Threat actors, campaigns, groups, reports, categories, tags, and sources." status="intelligence feed" stats={[{ label: "Threats", value: String(threatData.length), detail: "Current watchlist" }, { label: "Campaigns", value: "Ready", detail: "Frontend-only placeholder" }]} data={threatData} columns={threatColumns} searchPlaceholder="Search threats" />;
}
