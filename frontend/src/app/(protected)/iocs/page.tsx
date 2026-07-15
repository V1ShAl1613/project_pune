"use client";

// IOC management route for indicator discovery, status, relationships, and export workflows.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { iocData } from "@/soc/shared/soc-demo-data";
import { iocColumns } from "@/soc/shared/soc-column-helpers";

export default function IocsPage(): React.JSX.Element {
  return <SocListPage eyebrow="IOC management" title="IOCs" description="Indicator dashboard, search, categories, timeline, status, confidence, source, tags, relationships, and export." status="indicator tracking" stats={[{ label: "IOCs", value: String(iocData.length), detail: "Current indicator set" }, { label: "Confirmed", value: String(iocData.filter((item) => item.status === "Confirmed").length), detail: "Validated indicators" }]} data={iocData} columns={iocColumns} searchPlaceholder="Search indicators" />;
}
