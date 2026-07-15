"use client";

import Link from "next/link";
import type { Route } from "next";
import { usePathname } from "next/navigation";
import { Menu, Search, ShieldCheck } from "lucide-react";

import { cn } from "@/lib/cn";
import { protectedNavigation } from "@/constants/navigation";
import { LanguageSelector, NotificationIcon, OrganizationSwitcher, ProfileMenu, ThemeToggle } from "@/components/layouts/navigation-controls";

export function ResponsiveSidebar(): React.JSX.Element {
  const pathname = usePathname();
  return <aside className="hidden w-72 shrink-0 border-r border-line bg-panel/90 px-4 py-5 lg:block"><div className="mb-6 flex items-center gap-3 px-2"><div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-primary text-primary-foreground"><ShieldCheck className="h-5 w-5" /></div><div><div className="text-sm font-semibold text-text">Sentinel Fusion AI</div><div className="text-xs text-muted">Enterprise Control Plane</div></div></div><nav className="space-y-1">{protectedNavigation.map((item) => <Link key={item.href} href={item.href as Route} className={cn("flex items-center rounded-xl px-3 py-2 text-sm transition", pathname === item.href ? "bg-primary text-primary-foreground" : "text-muted hover:bg-canvas hover:text-text")}>{item.label}</Link>)}</nav></aside>;
}

export function TopNavigation(): React.JSX.Element {
  return <header className="sticky top-0 z-30 border-b border-line bg-canvas/90 backdrop-blur"><div className="flex flex-wrap items-center gap-3 px-4 py-4 sm:px-6 lg:px-8"><button className="inline-flex h-10 w-10 items-center justify-center rounded-xl border border-line lg:hidden"><Menu className="h-5 w-5" /></button><OrganizationSwitcher /><label className="flex min-w-0 flex-1 items-center gap-2 rounded-2xl border border-line bg-panel px-3 py-2 text-sm text-muted"><Search className="h-4 w-4" /><input className="w-full bg-transparent outline-none" placeholder="Search organizations, users, teams" aria-label="Global search" /></label><NotificationIcon /><ThemeToggle /><LanguageSelector /><ProfileMenu /></div></header>;
}

export function Footer(): React.JSX.Element {
  return <footer className="border-t border-line py-6 text-center text-xs text-muted">Sentinel Fusion AI Frontend</footer>;
}
