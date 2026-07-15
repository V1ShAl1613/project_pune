"use client";

// Investigation workspace route for timelines, notes, evidence, bookmarks, and task boards.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { investigationData } from "@/soc/shared/soc-demo-data";
import { investigationColumns } from "@/soc/shared/soc-column-helpers";

export default function InvestigationsPage(): React.JSX.Element {
  return <SocListPage eyebrow="Investigation workspace" title="Investigation Dashboard" description="Timeline, notes, evidence collection, relationship viewer, checklist, task board, bookmarks, and pinned evidence." status="analyst workspace" stats={[{ label: "Investigations", value: String(investigationData.length), detail: "Active workspaces" }, { label: "Pinned", value: String(investigationData.filter((item) => item.status === "Pinned").length), detail: "Pinned work items" }]} data={investigationData} columns={investigationColumns} searchPlaceholder="Search investigations" />;
}
