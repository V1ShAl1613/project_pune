"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { useForm } from "react-hook-form";

import { Button, Input, Textarea } from "@/components/ui/controls";
import { Card } from "@/components/ui/surfaces";
import { EntityPageShell } from "@/features/shared/page-shell";
import { sessionStore } from "@/store/session-store";
import { getProfile, updateProfile } from "@/services/api/identity-api";

type ProfileForm = { firstName?: string; lastName?: string; fullName?: string; phoneNumber?: string; timezone?: string; language?: string; theme?: string; profilePictureUrl?: string; emergencyContactName?: string; emergencyContactPhone?: string; };

export default function ProfilePage(): React.JSX.Element {
  const user = sessionStore((state) => state.user);
  const { data } = useQuery({ queryKey: ["profile", user?.id], queryFn: () => (user?.id ? getProfile(user.id) : Promise.resolve(null)), enabled: Boolean(user?.id) });
  const form = useForm<ProfileForm>({ defaultValues: { timezone: "UTC", language: "en" } });
  const mutation = useMutation({ mutationFn: ({ userId, payload }: { userId: string; payload: ProfileForm }) => updateProfile(userId, payload) });

  return <EntityPageShell title="Profile" description="Manage user profile, preferences, and contact details." breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Profile" }]}><div className="grid gap-6 xl:grid-cols-[1fr_0.9fr]"><Card><pre className="overflow-auto rounded-2xl bg-canvas p-4 text-xs text-muted">{JSON.stringify(data ?? {}, null, 2)}</pre></Card><form className="space-y-3 rounded-2xl border border-line bg-canvas p-4" onSubmit={form.handleSubmit((values) => { if (!user?.id) return; mutation.mutate({ userId: user.id, payload: values }); })}><h2 className="text-lg font-semibold">Edit profile</h2><Input placeholder="First name" {...form.register("firstName")} /><Input placeholder="Last name" {...form.register("lastName")} /><Input placeholder="Full name" {...form.register("fullName")} /><Input placeholder="Profile picture URL" {...form.register("profilePictureUrl")} /><Input placeholder="Timezone" {...form.register("timezone")} /><Input placeholder="Language" {...form.register("language")} /><Input placeholder="Theme" {...form.register("theme")} /><Input placeholder="Emergency contact name" {...form.register("emergencyContactName")} /><Input placeholder="Emergency contact phone" {...form.register("emergencyContactPhone")} /><Textarea placeholder="Additional profile notes" {...form.register("fullName")} /><Button className="w-full" type="submit">Save profile</Button></form></div></EntityPageShell>;
}
