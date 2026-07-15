"use client";

// SOC risk dashboard route with register, matrix, trends, filters, and export-ready UI.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { riskData } from "@/soc/shared/soc-demo-data";
import { riskColumns } from "@/soc/shared/soc-column-helpers";

export default function RiskCenterPage(): React.JSX.Element {
  return <SocListPage eyebrow="Risk center" title="Risk Dashboard" description="Risk register, matrix, details, trends, categories, filters, timeline, and export UX." status="risk operations" stats={[{ label: "Risks", value: String(riskData.length), detail: "Register items" }, { label: "High risk", value: String(riskData.filter((item) => item.score >= 80).length), detail: "Priority review" }]} data={riskData} columns={riskColumns} searchPlaceholder="Search risks" />;
}
