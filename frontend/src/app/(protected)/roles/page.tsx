"use client";

import { createColumnHelper } from "@tanstack/react-table";

import { IdentityListPage } from "@/identity/shared/iam-list-page";
import { demoRoles } from "@/identity/shared/iam-demo-data";
import { Badge } from "@/components/ui/surfaces";
import type { Role } from "@/types/identity";

const columnHelper = createColumnHelper<Role>();

const columns = [
  columnHelper.accessor("name", { header: "Role", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  columnHelper.accessor("key", { header: "Key" }),
  columnHelper.accessor("priority", { header: "Priority", cell: (info) => <div className="text-sm text-muted">{info.getValue() ?? 0}</div> }),
  columnHelper.accessor("color", { header: "Color", cell: (info) => <Badge tone="neutral">{info.getValue() ?? "default"}</Badge> }),
  columnHelper.accessor("status", { header: "Status", cell: (info) => <Badge tone={info.getValue() === "active" ? "success" : "neutral"}>{info.getValue()}</Badge> }),
];

export default function RolesPage(): React.JSX.Element {
  return <IdentityListPage eyebrow="RBAC" title="Roles" description="Role lifecycle, cloning, members, priority, and color coding for enterprise access." status="authorization ready" stats={[{ label: "Roles", value: String(demoRoles.length), detail: "Static role catalog" }, { label: "Assignments", value: "Planned", detail: "Role matrix supported" }]} columns={columns} data={demoRoles} searchPlaceholder="Search roles" />;
}