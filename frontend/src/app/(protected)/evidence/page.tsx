"use client";

// Evidence management route for collection, metadata, timeline, integrity, and attachments.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { evidenceData } from "@/soc/shared/soc-demo-data";
import { evidenceColumns } from "@/soc/shared/soc-column-helpers";

export default function EvidencePage(): React.JSX.Element {
  return <SocListPage eyebrow="Evidence management" title="Evidence" description="Evidence table, viewer, metadata, timeline, attachments, download, integrity status, notes, and search." status="digital forensics" stats={[{ label: "Evidence items", value: String(evidenceData.length), detail: "Captured artifacts" }, { label: "Verified", value: String(evidenceData.filter((item) => item.integrity === "Verified").length), detail: "Integrity validated" }]} data={evidenceData} columns={evidenceColumns} searchPlaceholder="Search evidence" />;
}
