"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { Button, Input } from "@/components/ui/controls";
import { Table, EmptyState } from "@/components/ui/data-display";
import { StatusBadge } from "@/components/ui/surfaces";
import { EntityPageShell } from "@/features/shared/page-shell";
import { createUser, listUsers } from "@/services/api/identity-api";

type UserForm = { email: string; username: string; displayName: string };

export default function UsersPage(): React.JSX.Element {
  const queryClient = useQueryClient();
  const { data } = useQuery({ queryKey: ["users"], queryFn: () => listUsers({ page: 1, pageSize: 20 }) });
  const form = useForm<UserForm>({ defaultValues: { email: "", username: "", displayName: "" } });
  const mutation = useMutation({ mutationFn: createUser, onSuccess: async () => { await queryClient.invalidateQueries({ queryKey: ["users"] }); form.reset(); } });

  return <EntityPageShell title="Users" description="Provision users within the active tenant." breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Users" }]}><div className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]"><div>{data?.items.length ? <Table><thead><tr className="border-b border-line text-xs uppercase tracking-wide text-muted"><th className="px-4 py-3">Email</th><th className="px-4 py-3">Display name</th><th className="px-4 py-3">Status</th></tr></thead><tbody>{data.items.map((user) => <tr key={user.id} className="border-b border-line/70 last:border-b-0"><td className="px-4 py-3 font-medium">{user.email}</td><td className="px-4 py-3">{user.displayName}</td><td className="px-4 py-3"><StatusBadge status={user.status} /></td></tr>)}</tbody></Table> : <EmptyState title="No users" description="Create users and assign them to the tenant structure." />}</div><form className="space-y-3 rounded-2xl border border-line bg-canvas p-4" onSubmit={form.handleSubmit((values) => mutation.mutate(values))}><h2 className="text-lg font-semibold">Create user</h2><Input placeholder="Email" {...form.register("email", { required: true })} /><Input placeholder="Username" {...form.register("username", { required: true })} /><Input placeholder="Display name" {...form.register("displayName", { required: true })} /><Button className="w-full" type="submit" disabled={mutation.isPending}>Create user</Button></form></div></EntityPageShell>;
}
