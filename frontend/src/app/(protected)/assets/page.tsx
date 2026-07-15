"use client";

// Asset inventory route with endpoints, servers, applications, cloud assets, containers, and databases.
import { SocListPage } from "@/soc/shared/soc-list-page";
import { assetData } from "@/soc/shared/soc-demo-data";
import { assetColumns } from "@/soc/shared/soc-column-helpers";

export default function AssetsPage(): React.JSX.Element {
  return <SocListPage eyebrow="Asset inventory" title="Assets" description="Servers, endpoints, applications, cloud assets, containers, databases, network devices, critical assets, tags, and search." status="asset watchlist" stats={[{ label: "Assets", value: String(assetData.length), detail: "Inventory records loaded" }, { label: "Critical", value: String(assetData.filter((item) => item.criticality === "Critical").length), detail: "High-value systems" }]} data={assetData} columns={assetColumns} searchPlaceholder="Search assets" />;
}
