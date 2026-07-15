"use client";

// Threat intelligence route for feeds, actors, campaigns, reports, sources, and relationships.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { threatData } from "@/soc/shared/soc-demo-data";
import { threatColumns } from "@/soc/shared/soc-column-helpers";

export default function IntelPage(): React.JSX.Element {
  return <SocListPage eyebrow="Threat intelligence" title="Intel" description="Threat feed, actors, campaigns, groups, timeline, reports, categories, search, relationships, tags, and sources." status="threat intelligence" stats={[{ label: "Threat records", value: String(threatData.length), detail: "Tracked threats" }, { label: "Monitoring", value: "Ready", detail: "Feed surfaces prepared" }]} data={threatData} columns={threatColumns} searchPlaceholder="Search intelligence" />;
}
