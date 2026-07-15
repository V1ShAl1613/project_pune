"use client";

import { createColumnHelper } from "@tanstack/react-table";

import { IdentityListPage } from "@/identity/shared/iam-list-page";
import { demoPermissions } from "@/identity/shared/iam-demo-data";
import { Badge } from "@/components/ui/surfaces";
import type { Permission } from "@/types/identity";

const columnHelper = createColumnHelper<Permission>();

const columns = [
  columnHelper.accessor("name", { header: "Permission", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  columnHelper.accessor("key", { header: "Key" }),
  columnHelper.accessor("category", { header: "Category" }),
  columnHelper.accessor("effect", { header: "Effect", cell: (info) => <Badge tone={info.getValue() === "allow" ? "success" : "danger"}>{info.getValue() ?? "allow"}</Badge> }),
];

export default function PermissionsPage(): React.JSX.Element {
  return <IdentityListPage eyebrow="Permission model" title="Permissions" description="Permission categories, effective access previews, and assignment UX for backend evaluation." status="policy ready" stats={[{ label: "Permissions", value: String(demoPermissions.length), detail: "Registered permission keys" }, { label: "Evaluation", value: "Backend", detail: "Frontend prepares input only" }]} columns={columns} data={demoPermissions} searchPlaceholder="Search permissions" />;
}