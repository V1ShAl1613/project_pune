"use client";

import { createColumnHelper } from "@tanstack/react-table";

import { IdentityListPage } from "@/identity/shared/iam-list-page";
import { demoGroups } from "@/identity/shared/iam-demo-data";
import { Badge } from "@/components/ui/surfaces";
import type { Group } from "@/types/identity";

const columnHelper = createColumnHelper<Group>();

const columns = [
  columnHelper.accessor("name", { header: "Group", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  columnHelper.accessor("organizationId", { header: "Organization" }),
  columnHelper.accessor("isDynamic", { header: "Type", cell: (info) => <Badge tone={info.getValue() ? "warning" : "neutral"}>{info.getValue() ? "Dynamic" : "Nested"}</Badge> }),
  columnHelper.accessor("status", { header: "Status", cell: (info) => <Badge tone={info.getValue() === "active" ? "success" : "neutral"}>{info.getValue()}</Badge> }),
];

export default function GroupsPage(): React.JSX.Element {
  return <IdentityListPage eyebrow="Group management" title="Groups" description="Nested group structure, dynamic rule UI, and group-role composition." status="access scope" stats={[{ label: "Groups", value: String(demoGroups.length), detail: "Static group catalog" }, { label: "Nested", value: "Ready", detail: "Role inheritance ready" }]} columns={columns} data={demoGroups} searchPlaceholder="Search groups" />;
}