"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";

import { Card, StatusBadge } from "@/components/ui/surfaces";
import { EntityPageShell } from "@/features/shared/page-shell";
import { listDepartments } from "@/services/api/identity-api";

export default function DepartmentDetailsPage(): React.JSX.Element {
  const params = useParams<{ id: string }>();
  const { data } = useQuery({ queryKey: ["department", params.id], queryFn: () => listDepartments({ page: 1, pageSize: 100 }), enabled: Boolean(params.id) });
  const department = data?.items.find((item: { id: string }) => item.id === params.id);

  return <EntityPageShell title={department?.name ?? "Department details"} description="Detailed department profile and metadata." breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Departments", href: "/departments" }, { label: department?.name ?? params.id }]}><Card><div className="space-y-3 text-sm"><div><span className="text-muted">Code:</span> {department?.code ?? params.id}</div><div><span className="text-muted">Status:</span> {department ? <StatusBadge status={department.status} /> : "Loading"}</div><pre className="overflow-auto rounded-2xl bg-canvas p-4 text-xs text-muted">{JSON.stringify(department ?? {}, null, 2)}</pre></div></Card></EntityPageShell>;
}
