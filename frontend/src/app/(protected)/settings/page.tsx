"use client";

import { useState } from "react";

import { Button, Switch } from "@/components/ui/controls";
import { Card } from "@/components/ui/surfaces";
import { EntityPageShell } from "@/features/shared/page-shell";
import { preferenceStore } from "@/store/preference-store";
import { themeStore } from "@/store/theme-store";

export default function SettingsPage(): React.JSX.Element {
  const theme = themeStore((state) => state.theme);
  const setTheme = themeStore((state) => state.setTheme);
  const density = preferenceStore((state) => state.density);
  const setDensity = preferenceStore((state) => state.setDensity);
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);

  return <EntityPageShell title="Settings" description="Adjust appearance, accessibility, and session preferences." breadcrumbs={[{ label: "Dashboard", href: "/dashboard" }, { label: "Settings" }]}><div className="grid gap-6 lg:grid-cols-2"><Card><div className="space-y-4"><h2 className="text-lg font-semibold">Appearance</h2><div className="flex flex-wrap gap-2"><Button variant={theme === "light" ? "primary" : "secondary"} onClick={() => setTheme("light")}>Light</Button><Button variant={theme === "dark" ? "primary" : "secondary"} onClick={() => setTheme("dark")}>Dark</Button><Button variant={theme === "system" ? "primary" : "secondary"} onClick={() => setTheme("system")}>System</Button></div><div className="flex items-center justify-between rounded-2xl border border-line bg-canvas p-4"><div><div className="font-medium">Density</div><div className="text-sm text-muted">Compact layout for dense operational work.</div></div><div className="flex items-center gap-2 text-sm"><span>Compact</span><Switch checked={density === "compact"} onChange={(event) => setDensity(event.target.checked ? "compact" : "comfortable")} /><span>Comfortable</span></div></div></div></Card><Card><div className="space-y-4"><h2 className="text-lg font-semibold">Notifications and privacy</h2><div className="flex items-center justify-between rounded-2xl border border-line bg-canvas p-4"><div><div className="font-medium">Browser notifications</div><div className="text-sm text-muted">Allow important account events.</div></div><Switch checked={notificationsEnabled} onChange={(event) => setNotificationsEnabled(event.target.checked)} /></div><Button>Save preferences</Button></div></Card></div></EntityPageShell>;
}
