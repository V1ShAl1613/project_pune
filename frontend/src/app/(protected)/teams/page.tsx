"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { Button, Input } from "@/components/ui/controls";
import { Table, EmptyState } from "@/components/ui/data-display";
import { StatusBadge } from "@/components/ui/surfaces";
import { EntityPageShell } from "@/features/shared/page-shell";
import { createTeam, listTeams } from "@/services/api/identity-api";

type TeamForm = { departmentId: string; code: string; name: string };

export default function TeamsPage(): React.JSX.Element {
  const queryClient = useQueryClient();
  const { data } = useQuery({ queryKey: ["teams"], queryFn: () => listTeams({ page: 1, pageSize: 20 }) });
  const form = useForm<TeamForm>({ defaultValues: { departmentId: "", code: "", name: "" } });
  const mutation = useMutation({ mutationFn: createTeam, onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ["teams"] }); form.reset(); } });

  return <EntityPageShell title="Teams" description="Track operating teams and ownership across the enterprise." breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Teams" }]}><div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]"><div>{data?.items.length ? <Table><thead><tr className="border-b border-line text-xs uppercase tracking-wide text-muted"><th className="px-4 py-3">Code</th><th className="px-4 py-3">Name</th><th className="px-4 py-3">Status</th></tr></thead><tbody>{data.items.map((team) => <tr key={team.id} className="border-b border-line/70 last:border-b-0"><td className="px-4 py-3 font-medium">{team.code}</td><td className="px-4 py-3">{team.name}</td><td className="px-4 py-3"><StatusBadge status={team.status} /></td></tr>)}</tbody></Table> : <EmptyState title="No teams" description="Create teams to align execution ownership." />}</div><form className="space-y-3 rounded-2xl border border-line bg-canvas p-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}><h2 className="text-lg font-semibold">Create team</h2><Input placeholder="Department ID" {...form.register("departmentId", { required: true })} /><Input placeholder="Code" {...form.register("code", { required: true })} /><Input placeholder="Name" {...form.register("name", { required: true })} /><Button className="w-full" type="submit" disabled={mutation.isPending}>Create team</Button></form></div></EntityPageShell>;
}
