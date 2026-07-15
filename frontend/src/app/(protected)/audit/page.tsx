"use client";

import { createColumnHelper } from "@tanstack/react-table";

import { IdentityListPage } from "@/identity/shared/iam-list-page";
import { demoAuditEvents } from "@/identity/shared/iam-demo-data";
import { Badge } from "@/components/ui/surfaces";
import type { AuditEvent } from "@/types/identity";

const columnHelper = createColumnHelper<AuditEvent>();

const columns = [
  columnHelper.accessor("timestamp", { header: "Timestamp", cell: (info) => <div className="text-sm text-muted">{info.getValue()}</div> }),
  columnHelper.accessor("actor", { header: "Actor", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  columnHelper.accessor("action", { header: "Action" }),
  columnHelper.accessor("resource", { header: "Resource" }),
  columnHelper.accessor("severity", { header: "Severity", cell: (info) => <Badge tone={info.getValue() === "critical" || info.getValue() === "high" ? "danger" : info.getValue() === "medium" ? "warning" : "neutral"}>{info.getValue()}</Badge> }),
];

export default function AuditPage(): React.JSX.Element {
  return <IdentityListPage eyebrow="Audit center" title="Audit" description="Timeline, filters, exports, search, and saved-filter UI for identity and RBAC events." status="audit ready" stats={[{ label: "Events", value: String(demoAuditEvents.length), detail: "Representative audit events" }, { label: "Export", value: "Ready", detail: "Button and filters UI" }]} columns={columns} data={demoAuditEvents} searchPlaceholder="Search audit events" topSummary={<div className="text-sm text-muted">Filtering and saved views are ready for backend query wiring.</div>} />;
}