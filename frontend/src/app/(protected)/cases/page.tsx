"use client";

// Case management route for structured investigations, tasks, evidence, and history.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { caseData } from "@/soc/shared/soc-demo-data";
import { caseColumns } from "@/soc/shared/soc-column-helpers";

export default function CasesPage(): React.JSX.Element {
  return <SocListPage eyebrow="Case management" title="Cases" description="Case dashboard, queue, details, assignment, status, tasks, notes, evidence, attachments, export, and history." status="structured response" stats={[{ label: "Cases", value: String(caseData.length), detail: "Active case load" }, { label: "Pending review", value: String(caseData.filter((item) => item.status === "Pending review").length), detail: "Waiting review" }]} data={caseData} columns={caseColumns} searchPlaceholder="Search cases" />;
}
