// Enterprise dashboard navigation chrome with sidebar and header controls.
"use client";

import Link from "next/link";
import type { Route } from "next";
import { useEffect, useMemo, useState } from "react";
import { AnimatePresence, motion, useReducedMotion } from "framer-motion";
import { ChevronDown, Command, Filter, Menu, Search, Settings2, Sparkles, Star, Clock3, LayoutDashboard, BellRing, PanelRightOpen, PanelLeftClose } from "lucide-react";

import { cn } from "@/lib/cn";
import { Button, Input } from "@/components/ui/controls";
import { Badge, Card } from "@/components/ui/surfaces";
import { Dialog, Popover } from "@/components/ui/overlays";
import { preferenceStore } from "@/store/preference-store";
import { themeStore } from "@/store/theme-store";
import { dashboardNavigation } from "@/dashboard/core/dashboard-models";
import { resolveDashboardIcon } from "@/dashboard/shared/icon-registry";

export function EnterpriseSidebar({ collapsed, onToggle }: { collapsed: boolean; onToggle: () => void }): React.JSX.Element {
  const pathname = typeof window !== "undefined" ? window.location.pathname : "/dashboard";
  const reducedMotion = useReducedMotion();
  const pinned = dashboardNavigation.filter((item) => item.pinned);
  const recent = dashboardNavigation.filter((item) => item.recent);
  const favorites = dashboardNavigation.filter((item) => item.favorite);

  return (
    <motion.aside
      animate={{ width: collapsed ? 88 : 316 }}
      transition={reducedMotion ? { duration: 0 } : { type: "spring", stiffness: 220, damping: 26 }}
      className="hidden h-[calc(100vh-72px)] shrink-0 border-r border-line bg-panel/90 lg:flex lg:flex-col"
    >
      <div className="flex items-center justify-between gap-3 border-b border-line px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary text-primary-foreground">
            <LayoutDashboard className="h-5 w-5" />
          </div>
          {collapsed ? null : (
            <div>
              <div className="text-sm font-semibold text-text">Enterprise Workspace</div>
              <div className="text-xs text-muted">Sentinel Fusion AI</div>
            </div>
          )}
        </div>
        <button
          aria-label="Collapse sidebar"
          className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-line"
          onClick={onToggle}
        >
          {collapsed ? <PanelRightOpen className="h-4 w-4" /> : <PanelLeftClose className="h-4 w-4" />}
        </button>
      </div>

      <div className="space-y-4 overflow-auto px-3 py-4">
        <SidebarGroup title={collapsed ? "" : "Pinned Pages"} items={pinned} collapsed={collapsed} pathname={pathname} />
        <SidebarGroup title={collapsed ? "" : "Favorites"} items={favorites} collapsed={collapsed} pathname={pathname} />
        <SidebarGroup title={collapsed ? "" : "Recent Pages"} items={recent} collapsed={collapsed} pathname={pathname} />
        <SidebarGroup title={collapsed ? "" : "Navigation"} items={dashboardNavigation} collapsed={collapsed} pathname={pathname} />
      </div>

      <div className="mt-auto border-t border-line p-4 text-xs text-muted">{collapsed ? "" : "Responsive drawer and hover-expand ready."}</div>
    </motion.aside>
  );
}

function SidebarGroup({ title, items, collapsed, pathname }: { title: string; items: typeof dashboardNavigation; collapsed: boolean; pathname: string }): React.JSX.Element | null {
  if (items.length === 0) return null;
  return <div className="space-y-2"><div className={cn("px-3 text-xs font-semibold uppercase tracking-wide text-muted", collapsed && "sr-only")}>{title}</div><div className="space-y-1">{items.map((item) => { const Icon = resolveDashboardIcon(item.icon); return <Link key={item.key} href={item.href as Route} className={cn("group flex items-center gap-3 rounded-2xl px-3 py-2 text-sm transition", pathname === item.href ? "bg-primary text-primary-foreground" : "text-muted hover:bg-canvas hover:text-text")}>{<Icon className="h-4 w-4 shrink-0" />}{collapsed ? null : <span className="min-w-0 flex-1 truncate">{item.label}</span>}{collapsed ? null : item.pinned ? <Star className="h-3.5 w-3.5 opacity-60" /> : null}</Link>; })}</div></div>;
}

export function WorkspaceHeader(): React.JSX.Element {
  const theme = themeStore((state) => state.theme);
  const setTheme = themeStore((state) => state.setTheme);
  const organizationId = preferenceStore((state) => state.organizationId);
  const setOrganizationId = preferenceStore((state) => state.setOrganizationId);

  return <div className="flex flex-wrap items-center gap-3 border-b border-line bg-canvas/95 px-4 py-4 backdrop-blur sm:px-6 lg:px-8"><div className="min-w-0 flex-1"><div className="text-sm font-semibold text-text">Workspace</div><div className="text-xs text-muted">Enterprise dashboard shell</div></div><div className="flex flex-wrap items-center gap-2"><SearchBar /><WorkspaceSelector organizationId={organizationId} onChange={setOrganizationId} /><ThemeQuickToggle theme={theme} onChange={setTheme} /><NotificationCenterButton /><ProfileShortcut /><SettingsQuickLink /><CommandShortcut /></div></div>;
}

function SearchBar(): React.JSX.Element {
  return <label className="hidden min-w-72 items-center gap-2 rounded-2xl border border-line bg-panel px-3 py-2 text-sm text-muted md:flex"><Search className="h-4 w-4" /><input aria-label="Global search" className="w-full bg-transparent outline-none" placeholder="Search pages, widgets, metrics" /></label>;
}

function WorkspaceSelector({ organizationId, onChange }: { organizationId: string | null; onChange: (organizationId: string | null) => void }): React.JSX.Element {
  return <Popover trigger={<button className="inline-flex min-h-10 items-center gap-2 rounded-2xl border border-line bg-panel px-3 py-2 text-sm"><Sparkles className="h-4 w-4" /><span>{organizationId ? "Workspace" : "Default Workspace"}</span><ChevronDown className="h-4 w-4 text-muted" /></button>} content={<div className="space-y-2"><div className="text-xs uppercase tracking-wide text-muted">Workspace Selector</div><button className="w-full rounded-xl px-3 py-2 text-left text-sm hover:bg-canvas" onClick={() => onChange(null)}>Default Workspace</button><button className="w-full rounded-xl px-3 py-2 text-left text-sm hover:bg-canvas" onClick={() => onChange("enterprise")}>Enterprise Workspace</button></div>} />;
}

function ThemeQuickToggle({ theme, onChange }: { theme: string; onChange: (theme: "light" | "dark" | "system") => void }): React.JSX.Element {
  const nextTheme = theme === "light" ? "dark" : theme === "dark" ? "system" : "light";
  return <button className="inline-flex h-10 items-center gap-2 rounded-2xl border border-line bg-panel px-3 text-sm" aria-label="Toggle theme" onClick={() => onChange(nextTheme)}><Settings2 className="h-4 w-4" />{theme}</button>;
}

function NotificationCenterButton(): React.JSX.Element {
  return <Popover trigger={<button className="inline-flex h-10 items-center gap-2 rounded-2xl border border-line bg-panel px-3 text-sm"><BellRing className="h-4 w-4" />Notifications</button>} content={<Card className="w-[22rem] max-w-[80vw]"><div className="space-y-3"><div className="flex items-center justify-between"><div className="text-sm font-semibold">Notification Center</div><Badge tone="success">Unread</Badge></div><div className="space-y-2 text-sm text-muted"><NotificationItem title="Maintenance window" description="Planned maintenance tonight." /><NotificationItem title="Workspace updated" description="Your layout preferences were saved." /></div></div></Card>} />;
}

function ProfileShortcut(): React.JSX.Element { return <button className="inline-flex h-10 items-center gap-2 rounded-2xl border border-line bg-panel px-3 text-sm"><LayoutDashboard className="h-4 w-4" />Profile</button>; }
function SettingsQuickLink(): React.JSX.Element { return <Link href="/settings" className="inline-flex h-10 items-center gap-2 rounded-2xl border border-line bg-panel px-3 text-sm"><Settings2 className="h-4 w-4" />Settings</Link>; }
function CommandShortcut(): React.JSX.Element { return <button className="inline-flex h-10 items-center gap-2 rounded-2xl border border-line bg-panel px-3 text-sm"><Command className="h-4 w-4" />Ctrl K</button>; }

function NotificationItem({ title, description }: { title: string; description: string }): React.JSX.Element {
  return <div className="rounded-2xl border border-line bg-canvas p-3"><div className="text-sm font-medium text-text">{title}</div><div className="text-xs text-muted">{description}</div></div>;
}

export function DashboardCommandPalette({ open, onOpenChange }: { open: boolean; onOpenChange: (open: boolean) => void }): React.JSX.Element {
  const commands = useMemo(() => ["Dashboard", "Users", "Organizations", "Settings", "Theme Light", "Theme Dark", "Theme System"], []);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent): void {
      if ((event.metaKey || event.ctrlKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        onOpenChange(!open);
      }
      if (event.key === "Escape") {
        onOpenChange(false);
      }
    }

    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open, onOpenChange]);

  return <Dialog open={open} title="Command Palette" onClose={() => onOpenChange(false)}><div className="space-y-4"><Input placeholder="Search commands, pages, or actions" aria-label="Command search" /><div className="grid gap-2">{commands.map((command) => <button key={command} className="flex items-center justify-between rounded-xl border border-line px-3 py-2 text-left text-sm hover:bg-canvas"><span>{command}</span><Clock3 className="h-4 w-4 text-muted" /></button>)}</div><div className="flex justify-end gap-2"><Button variant="secondary" onClick={() => onOpenChange(false)}>Close</Button></div></div></Dialog>;
}
