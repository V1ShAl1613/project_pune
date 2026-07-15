"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { Button, Input } from "@/components/ui/controls";
import { Table, EmptyState } from "@/components/ui/data-display";
import { StatusBadge } from "@/components/ui/surfaces";
import { EntityPageShell } from "@/features/shared/page-shell";
import { createDepartment, listDepartments } from "@/services/api/identity-api";

type DepartmentForm = { organizationId: string; code: string; name: string };

export default function DepartmentsPage(): React.JSX.Element {
  const queryClient = useQueryClient();
  const { data } = useQuery({ queryKey: ["departments"], queryFn: () => listDepartments({ page: 1, pageSize: 20 }) });
  const form = useForm<DepartmentForm>({ defaultValues: { organizationId: "", code: "", name: "" } });
  const mutation = useMutation({ mutationFn: createDepartment, onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ["departments"] }); form.reset(); } });

  return <EntityPageShell title="Departments" description="Create and manage departmental structure for the tenant." breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Departments" }]}><div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]"><div>{data?.items.length ? <Table><thead><tr className="border-b border-line text-xs uppercase tracking-wide text-muted"><th className="px-4 py-3">Code</th><th className="px-4 py-3">Name</th><th className="px-4 py-3">Status</th></tr></thead><tbody>{data.items.map((department) => <tr key={department.id} className="border-b border-line/70 last:border-b-0"><td className="px-4 py-3 font-medium">{department.code}</td><td className="px-4 py-3">{department.name}</td><td className="px-4 py-3"><StatusBadge status={department.status} /></td></tr>)}</tbody></Table> : <EmptyState title="No departments" description="Create a department to organize teams and users." />}</div><form className="space-y-3 rounded-2xl border border-line bg-canvas p-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}><h2 className="text-lg font-semibold">Create department</h2><Input placeholder="Organization ID" {...form.register("organizationId", { required: true })} /><Input placeholder="Code" {...form.register("code", { required: true })} /><Input placeholder="Name" {...form.register("name", { required: true })} /><Button className="w-full" type="submit" disabled={mutation.isPending}>Create department</Button></form></div></EntityPageShell>;
}
