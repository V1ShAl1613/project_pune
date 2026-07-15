// Centralized icon registry for dashboard navigation and shared chrome.
import { Building2, FileText, FolderSearch, Gauge, LayoutDashboard, Plug, Radar, ScrollText, Server, Settings2, ShieldAlert, ShieldCheck, SlidersHorizontal, TriangleAlert, Users, Banknote } from "lucide-react";
import type { LucideIcon } from "lucide-react";

const iconRegistry: Record<string, LucideIcon> = {
  "layout-dashboard": LayoutDashboard,
  "shield-alert": ShieldAlert,
  radar: Radar,
  banknote: Banknote,
  gauge: Gauge,
  "shield-check": ShieldCheck,
  users: Users,
  "building-2": Building2,
  server: Server,
  "triangle-alert": TriangleAlert,
  "folder-search": FolderSearch,
  "file-text": FileText,
  "settings-2": Settings2,
  "scroll-text": ScrollText,
  plug: Plug,
  "sliders-horizontal": SlidersHorizontal,
};

export function resolveDashboardIcon(name: string): LucideIcon {
  return iconRegistry[name] ?? LayoutDashboard;
}
