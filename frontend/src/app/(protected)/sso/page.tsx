"use client";

import { createColumnHelper } from "@tanstack/react-table";

import { IdentityListPage } from "@/identity/shared/iam-list-page";
import { demoSsoProviders } from "@/identity/shared/iam-demo-data";
import { Badge } from "@/components/ui/surfaces";
import type { SsoProvider } from "@/types/identity";

const columnHelper = createColumnHelper<SsoProvider>();

const columns = [
  columnHelper.accessor("provider", { header: "Provider", cell: (info) => <div className="font-medium text-text">{info.getValue()}</div> }),
  columnHelper.accessor("connectionName", { header: "Connection" }),
  columnHelper.accessor("status", { header: "Status", cell: (info) => <Badge tone={info.getValue() === "connected" ? "success" : info.getValue() === "testing" ? "warning" : "neutral"}>{info.getValue()}</Badge> }),
  columnHelper.accessor("certificateStatus", { header: "Certificate" }),
];

export default function SsoPage(): React.JSX.Element {
  return <IdentityListPage eyebrow="Federation" title="SSO Configuration" description="SAML, OIDC, Azure AD, Okta, Auth0, Ping, OneLogin, and custom provider setup surfaces." status="identity federation" stats={[{ label: "Providers", value: String(demoSsoProviders.length), detail: "Enterprise connectors available" }, { label: "Metadata", value: "Ready", detail: "Upload and test flows" }]} columns={columns} data={demoSsoProviders} searchPlaceholder="Search SSO providers" />;
}