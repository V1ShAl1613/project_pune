"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Card, StatusBadge } from "@/components/ui/surfaces";
import { EntityPageShell } from "@/features/shared/page-shell";
import { listOrganizations } from "@/services/api/identity-api";

export default function OrganizationDetailsPage(): React.JSX.Element {
  const params = useParams<{ id: string }>();
  const { data } = useQuery({ queryKey: ["organization", params.id], queryFn: () => listOrganizations({ page: 1, pageSize: 100 }), enabled: Boolean(params.id) });
  const organization = data?.items.find((item: { id: string }) => item.id === params.id);

  return <EntityPageShell title={organization?.name ?? "Organization details"} description="Detailed organization profile and metadata." breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Organizations", href: "/organizations" }, { label: organization?.name ?? params.id }]}><Card><div className="space-y-3 text-sm"><div><span className="text-muted">Code:</span> {organization?.code ?? params.id}</div><div><span className="text-muted">Status:</span> {organization ? <StatusBadge status={organization.status} /> : "Loading"}</div><pre className="overflow-auto rounded-2xl bg-canvas p-4 text-xs text-muted">{JSON.stringify(organization ?? {}, null, 2)}</pre></div></Card></EntityPageShell>;
}
