"use client";

import { createColumnHelper } from "@tanstack/react-table";

import { IdentityListPage } from "@/identity/shared/iam-list-page";
import { demoSessions } from "@/identity/shared/iam-demo-data";
import { Badge } from "@/components/ui/surfaces";
import type { SessionDevice } from "@/types/identity";

const columnHelper = createColumnHelper<SessionDevice>();

const columns = [
  columnHelper.accessor("deviceName", { header: "Device", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  columnHelper.accessor("browser", { header: "Browser" }),
  columnHelper.accessor("os", { header: "OS" }),
  columnHelper.accessor("status", { header: "Status", cell: (info) => <Badge tone={info.getValue() === "current" ? "success" : "neutral"}>{info.getValue()}</Badge> }),
  columnHelper.accessor("ipAddress", { header: "IP Address" }),
];

export default function SessionsPage(): React.JSX.Element {
  return <IdentityListPage eyebrow="Session management" title="Sessions" description="Current session, trusted devices, active sessions, and termination workflows." status="session security" stats={[{ label: "Devices", value: String(demoSessions.length), detail: "Trusted and current examples" }, { label: "Terminate", value: "Ready", detail: "Session controls prepared" }]} columns={columns} data={demoSessions} searchPlaceholder="Search sessions" />;
}