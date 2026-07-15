"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Card, StatusBadge } from "@/components/ui/surfaces";
import { EntityPageShell } from "@/features/shared/page-shell";
import { listUsers } from "@/services/api/identity-api";

export default function UserDetailsPage(): React.JSX.Element {
  const params = useParams<{ id: string }>();
  const { data } = useQuery({ queryKey: ["user", params.id], queryFn: () => listUsers({ page: 1, pageSize: 100 }), enabled: Boolean(params.id) });
  const user = data?.items.find((item: { id: string }) => item.id === params.id);

  return <EntityPageShell title={user?.displayName ?? "User details"} description="Detailed user profile and access metadata." breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Users", href: "/users" }, { label: user?.displayName ?? params.id }]}><Card><div className="space-y-3 text-sm"><div><span className="text-muted">Email:</span> {user?.email ?? params.id}</div><div><span className="text-muted">Status:</span> {user ? <StatusBadge status={user.status} /> : "Loading"}</div><pre className="overflow-auto rounded-2xl bg-canvas p-4 text-xs text-muted">{JSON.stringify(user ?? {}, null, 2)}</pre></div></Card></EntityPageShell>;
}
