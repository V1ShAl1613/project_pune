"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Card, StatusBadge } from "@/components/ui/surfaces";
import { EntityPageShell } from "@/features/shared/page-shell";
import { listTeams } from "@/services/api/identity-api";

export default function TeamDetailsPage(): React.JSX.Element {
  const params = useParams<{ id: string }>();
  const { data } = useQuery({ queryKey: ["team", params.id], queryFn: () => listTeams({ page: 1, pageSize: 100 }), enabled: Boolean(params.id) });
  const team = data?.items.find((item: { id: string }) => item.id === params.id);

  return <EntityPageShell title={team?.name ?? "Team details"} description="Detailed team profile and metadata." breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Teams", href: "/teams" }, { label: team?.name ?? params.id }]}><Card><div className="space-y-3 text-sm"><div><span className="text-muted">Code:</span> {team?.code ?? params.id}</div><div><span className="text-muted">Status:</span> {team ? <StatusBadge status={team.status} /> : "Loading"}</div><pre className="overflow-auto rounded-2xl bg-canvas p-4 text-xs text-muted">{JSON.stringify(team ?? {}, null, 2)}</pre></div></Card></EntityPageShell>;
}
