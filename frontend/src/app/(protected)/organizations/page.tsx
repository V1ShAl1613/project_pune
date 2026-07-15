"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { Button, Input, Textarea } from "@/components/ui/controls";
import { Table, Pagination, EmptyState } from "@/components/ui/data-display";
import { StatusBadge } from "@/components/ui/surfaces";
import { EntityPageShell } from "@/features/shared/page-shell";
import { createOrganization, listOrganizations } from "@/services/api/identity-api";

type OrganizationForm = { code: string; name: string; legalName?: string; description?: string };

export default function OrganizationsPage(): React.JSX.Element {
  const queryClient = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: ["organizations"], queryFn: () => listOrganizations({ page: 1, pageSize: 20 }) });
  const form = useForm<OrganizationForm>({ defaultValues: { code: "", name: "", legalName: "", description: "" } });
  const mutation = useMutation({ mutationFn: createOrganization, onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ["organizations"] }); form.reset(); } });

  return <EntityPageShell title="Organizations" description="Manage enterprise organizations within the active tenant." breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Organizations" }]}><div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]"><div>{isLoading ? <div className="text-sm text-muted">Loading organizations...</div> : data?.items.length ? <Table><thead><tr className="border-b border-line text-xs uppercase tracking-wide text-muted"><th className="px-4 py-3">Code</th><th className="px-4 py-3">Name</th><th className="px-4 py-3">Status</th></tr></thead><tbody>{data.items.map((organization) => <tr key={organization.id} className="border-b border-line/70 last:border-b-0"><td className="px-4 py-3 font-medium">{organization.code}</td><td className="px-4 py-3">{organization.name}</td><td className="px-4 py-3"><StatusBadge status={organization.status} /></td></tr>)}</tbody></Table> : <EmptyState title="No organizations" description="Create the first organization for this tenant." />}<div className="mt-4">{data ? <Pagination page={data.page} pageSize={data.pageSize} total={data.total} onPageChange={() => undefined} /> : null}</div></div><form className="space-y-3 rounded-2xl border border-line bg-canvas p-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}><h2 className="text-lg font-semibold">Create organization</h2><Input placeholder="Code" {...form.register("code", { required: true })} /><Input placeholder="Name" {...form.register("name", { required: true })} /><Input placeholder="Legal name" {...form.register("legalName")} /><Textarea placeholder="Description" {...form.register("description")} /><Button className="w-full" type="submit" disabled={mutation.isPending}>Create organization</Button></form></div></EntityPageShell>;
}
