"use client";

import { createColumnHelper } from "@tanstack/react-table";

import { IdentityListPage } from "@/identity/shared/iam-list-page";
import { demoInvitations } from "@/identity/shared/iam-demo-data";
import { Badge } from "@/components/ui/surfaces";
import type { Invitation } from "@/types/identity";

const columnHelper = createColumnHelper<Invitation>();

const columns = [
  columnHelper.accessor("email", { header: "Email", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  columnHelper.accessor("roleName", { header: "Role" }),
  columnHelper.accessor("status", { header: "Status", cell: (info) => <Badge tone={info.getValue() === "pending" ? "warning" : info.getValue() === "expired" ? "danger" : "success"}>{info.getValue()}</Badge> }),
  columnHelper.accessor("expiresAt", { header: "Expires" }),
];

export default function InvitationsPage(): React.JSX.Element {
  return <IdentityListPage eyebrow="Invitations" title="Invitations" description="Bulk invite, resend, cancel, and history flows for enterprise onboarding." status="onboarding" stats={[{ label: "Invites", value: String(demoInvitations.length), detail: "Pending and expired examples" }, { label: "Bulk", value: "Ready", detail: "Static UI scaffold" }]} columns={columns} data={demoInvitations} searchPlaceholder="Search invitations" />;
}