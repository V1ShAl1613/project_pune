"use client";

import { useRouter } from "next/navigation";
import { Bell, ChevronDown, Globe, LogOut, MoonStar, Settings2, Building2 } from "lucide-react";
import { useQuery } from "@tanstack/react-query";

import { Popover } from "@/components/ui/overlays";
import { Badge } from "@/components/ui/surfaces";
import { listOrganizations } from "@/services/api/identity-api";
import { notificationStore } from "@/store/notification-store";
import { preferenceStore } from "@/store/preference-store";
import { sessionStore } from "@/store/session-store";
import { themeStore } from "@/store/theme-store";
import { clearSessionCookie } from "@/utils/session-cookie";

export function OrganizationSwitcher(): React.JSX.Element {
  const activeOrganizationId = preferenceStore((state) => state.organizationId);
  const setOrganizationId = preferenceStore((state) => state.setOrganizationId);
  const organizationsQuery = useQuery({ queryKey: ["organizations", "switcher"], queryFn: () => listOrganizations({ page: 1, pageSize: 20 }) });
  const activeOrganization = organizationsQuery.data?.items.find((item) => item.id === activeOrganizationId) ?? organizationsQuery.data?.items[0] ?? null;

  return <Popover trigger={<button className="inline-flex min-h-10 items-center gap-2 rounded-2xl border border-line bg-panel px-3 py-2 text-sm"><Building2 className="h-4 w-4" /><span className="max-w-28 truncate">{activeOrganization?.name ?? "Organization"}</span><ChevronDown className="h-4 w-4 text-muted" /></button>} content={<div className="space-y-2"><div className="text-xs uppercase tracking-wide text-muted">Organizations</div>{organizationsQuery.data?.items.map((organization) => <button key={organization.id} className="flex w-full items-center justify-between rounded-xl px-3 py-2 text-left text-sm hover:bg-canvas" onClick={() => setOrganizationId(organization.id)}><span className="truncate">{organization.name}</span>{organization.id === activeOrganizationId ? <Badge tone="success">Active</Badge> : null}</button>) ?? <div className="text-sm text-muted">No organizations available.</div>}</div>} />;
}

export function ThemeToggle(): React.JSX.Element {
  const theme = themeStore((state) => state.theme);
  const setTheme = themeStore((state) => state.setTheme);
  const nextTheme = theme === "light" ? "dark" : theme === "dark" ? "system" : "light";
  return <button className="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-line bg-panel" aria-label="Toggle theme" onClick={() => setTheme(nextTheme)}><MoonStar className="h-5 w-5" /></button>;
}

export function LanguageSelector(): React.JSX.Element {
  const language = preferenceStore((state) => state.language);
  const setLanguage = preferenceStore((state) => state.setLanguage);
  return <Popover trigger={<button className="inline-flex h-10 items-center gap-2 rounded-2xl border border-line bg-panel px-3 text-sm"><Globe className="h-4 w-4" /><span>{language.toUpperCase()}</span><ChevronDown className="h-4 w-4 text-muted" /></button>} content={<div className="space-y-2"><div className="text-xs uppercase tracking-wide text-muted">Language</div>{["en", "hi", "bn"].map((item) => <button key={item} className="w-full rounded-xl px-3 py-2 text-left text-sm hover:bg-canvas" onClick={() => setLanguage(item)}>{item.toUpperCase()}</button>)}</div>} />;
}

export function NotificationIcon(): React.JSX.Element {
  const count = notificationStore((state) => state.notifications.length);
  return <button className="relative inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-line bg-panel" aria-label="Notifications"><Bell className="h-5 w-5" />{count > 0 ? <span className="absolute right-2 top-2 h-2.5 w-2.5 rounded-full bg-danger" /> : null}</button>;
}

export function ProfileMenu(): React.JSX.Element {
  const router = useRouter();
  const user = sessionStore((state) => state.user);
  const clearSession = sessionStore((state) => state.clearSession);
  return <Popover trigger={<button className="inline-flex items-center gap-2 rounded-2xl border border-line bg-panel px-3 py-2 text-sm"><span className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-xs font-semibold text-primary-foreground">{user?.displayName?.slice(0, 1).toUpperCase() ?? "U"}</span><span className="hidden sm:block">{user?.displayName ?? "Profile"}</span><ChevronDown className="h-4 w-4 text-muted" /></button>} content={<div className="space-y-2"><div><div className="text-sm font-semibold text-text">{user?.displayName ?? "Profile"}</div><div className="text-xs text-muted">{user?.email ?? "No session loaded"}</div></div><button className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm hover:bg-canvas" onClick={() => router.push("/profile")}><Settings2 className="h-4 w-4" />Profile settings</button><button className="flex w-full items-center gap-2 rounded-xl px-3 py-2 text-left text-sm text-danger hover:bg-danger/10" onClick={() => { clearSession(); clearSessionCookie(); router.push("/login"); }}><LogOut className="h-4 w-4" />Sign out</button></div>} />;
}
