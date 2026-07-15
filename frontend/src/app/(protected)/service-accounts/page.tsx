"use client";

import { createColumnHelper } from "@tanstack/react-table";

import { IdentityListPage } from "@/identity/shared/iam-list-page";
import { demoServiceAccounts } from "@/identity/shared/iam-demo-data";
import { Badge } from "@/components/ui/surfaces";
import type { ServiceAccount } from "@/types/identity";

const columnHelper = createColumnHelper<ServiceAccount>();

const columns = [
  columnHelper.accessor("name", { header: "Service Account", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  columnHelper.accessor("description", { header: "Description" }),
  columnHelper.accessor("scopes", { header: "Scopes", cell: (info) => <div className="text-sm text-muted">{info.getValue().join(", ")}</div> }),
  columnHelper.accessor("secretRotation", { header: "Rotation" }),
  columnHelper.accessor("status", { header: "Status", cell: (info) => <Badge tone={info.getValue() === "active" ? "success" : "neutral"}>{info.getValue()}</Badge> }),
];

export default function ServiceAccountsPage(): React.JSX.Element {
  return <IdentityListPage eyebrow="Automation identities" title="Service Accounts" description="Create, edit, revoke, and rotate service account credentials and scopes." status="machine identity" stats={[{ label: "Accounts", value: String(demoServiceAccounts.length), detail: "Static service account examples" }, { label: "Rotation", value: "Ready", detail: "Secret lifecycle UI" }]} columns={columns} data={demoServiceAccounts} searchPlaceholder="Search service accounts" />;
}