"use client";

import { createColumnHelper } from "@tanstack/react-table";
import { DatabaseZap, ShieldCheck } from "lucide-react";

import { IdentityListPage } from "@/identity/shared/iam-list-page";
import { demoTenants } from "@/identity/shared/iam-demo-data";
import { Badge } from "@/components/ui/surfaces";
import type { Tenant } from "@/types/identity";

const columnHelper = createColumnHelper<Tenant>();

const columns = [
  columnHelper.accessor("code", { header: "Tenant", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  columnHelper.accessor("name", { header: "Name" }),
  columnHelper.accessor("status", { header: "Status", cell: (info) => <Badge tone={info.getValue() === "active" ? "success" : "neutral"}>{info.getValue()}</Badge> }),
  columnHelper.accessor("configuration", { header: "Controls", cell: (info) => <div className="text-sm text-muted">{Object.keys(info.getValue()).length} settings</div> }),
  columnHelper.accessor("activatedAt", { header: "Activated", cell: (info) => <div className="text-sm text-muted">{info.getValue() ?? "Pending"}</div> }),
];

export default function TenantsPage(): React.JSX.Element {
  return <IdentityListPage eyebrow="Tenant management" title="Tenants" description="Tenant isolation, status, metadata, and access policy entry point." status="multi-tenant" stats={[{ label: "Tenants", value: String(demoTenants.length), detail: "Tenant records available" }, { label: "Isolation", value: "Enabled", detail: "Context-aware shell" }]} columns={columns} data={demoTenants} searchPlaceholder="Search tenants" topSummary={<div className="text-sm text-muted">Tenant routing and workspace scoping are prepared for backend session context.</div>} />;
}