"use client";

// Playbooks route for action templates, categories, documentation, and execution timeline placeholders.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { playbookData } from "@/soc/shared/soc-demo-data";
import { playbookColumns } from "@/soc/shared/soc-column-helpers";

export default function PlaybooksPage(): React.JSX.Element {
  return <SocListPage eyebrow="Playbooks" title="Playbooks" description="Playbook list, details, steps, categories, search, documentation, and execution timeline placeholder." status="response automation" stats={[{ label: "Playbooks", value: String(playbookData.length), detail: "Published and draft playbooks" }, { label: "Steps", value: String(playbookData.reduce((total, item) => total + item.steps, 0)), detail: "Documented procedures" }]} data={playbookData} columns={playbookColumns} searchPlaceholder="Search playbooks" />;
}
