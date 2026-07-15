"use client";

import { createColumnHelper } from "@tanstack/react-table";

import { IdentityListPage } from "@/identity/shared/iam-list-page";
import { demoApiKeys } from "@/identity/shared/iam-demo-data";
import { Badge } from "@/components/ui/surfaces";
import type { ApiKey } from "@/types/identity";

const columnHelper = createColumnHelper<ApiKey>();

const columns = [
  columnHelper.accessor("name", { header: "API Key", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  columnHelper.accessor("prefix", { header: "Prefix" }),
  columnHelper.accessor("scopes", { header: "Scopes", cell: (info) => <div className="text-sm text-muted">{info.getValue().join(", ")}</div> }),
  columnHelper.accessor("status", { header: "Status", cell: (info) => <Badge tone={info.getValue() === "active" ? "success" : info.getValue() === "rotating" ? "warning" : "neutral"}>{info.getValue()}</Badge> }),
];

export default function ApiKeysPage(): React.JSX.Element {
  return <IdentityListPage eyebrow="Secrets" title="API Keys" description="Generate, rotate, revoke, and inspect access-key UX with usage placeholders." status="token management" stats={[{ label: "Keys", value: String(demoApiKeys.length), detail: "Static API key examples" }, { label: "Scopes", value: "Ready", detail: "Scope list UI supported" }]} columns={columns} data={demoApiKeys} searchPlaceholder="Search API keys" />;
}