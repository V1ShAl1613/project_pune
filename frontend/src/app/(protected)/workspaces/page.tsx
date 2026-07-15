"use client";

import { createColumnHelper } from "@tanstack/react-table";
import { Layers3 } from "lucide-react";

import { IdentityListPage } from "@/identity/shared/iam-list-page";
import { demoWorkspaces } from "@/identity/shared/iam-demo-data";
import { Badge } from "@/components/ui/surfaces";
import type { TenantWorkspace } from "@/types/identity";

const columnHelper = createColumnHelper<TenantWorkspace>();

const columns = [
  columnHelper.accessor("name", { header: "Workspace", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  columnHelper.accessor("code", { header: "Code" }),
  columnHelper.accessor("status", { header: "Status", cell: (info) => <Badge tone={info.getValue() === "active" ? "success" : "neutral"}>{info.getValue()}</Badge> }),
  columnHelper.accessor("organizationId", { header: "Organization" }),
  columnHelper.accessor("description", { header: "Description" }),
];

export default function WorkspacesPage(): React.JSX.Element {
  return <IdentityListPage eyebrow="Workspace management" title="Workspaces" description="Workspace context, preferences, branding, archive, and restore flows." status="tenant-scoped" stats={[{ label: "Workspaces", value: String(demoWorkspaces.length), detail: "Workspace records available" }, { label: "Context", value: "Ready", detail: "Tenant-aware switching" }]} actions={[{ label: "Create workspace", href: "/workspaces", variant: "secondary" }]} columns={columns} data={demoWorkspaces} searchPlaceholder="Search workspaces" topSummary={<div className="flex items-center gap-2 text-sm text-muted"><Layers3 className="h-4 w-4" />Workspace selector and archive/restore UX are ready for backend wiring.</div>} />;
}