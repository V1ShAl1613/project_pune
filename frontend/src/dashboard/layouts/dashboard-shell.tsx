// High-level enterprise dashboard shell combining navigation, header, and content framing.
"use client";

import { useState } from "react";
import { motion } from "framer-motion";

import { cn } from "@/lib/cn";
import { Footer } from "@/components/layouts/navigation";
import { PageContainer } from "@/components/layouts/shell";
import { DashboardCommandPalette, EnterpriseSidebar, WorkspaceHeader } from "@/dashboard/navigation/dashboard-navigation";

export function DashboardShell({ children, className }: { children: React.ReactNode; className?: string }): React.JSX.Element {
  const [collapsed, setCollapsed] = useState(false);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);

  return <div className="min-h-screen bg-canvas text-text"><WorkspaceHeader /><div className="flex min-h-[calc(100vh-72px)]"><EnterpriseSidebar collapsed={collapsed} onToggle={() => setCollapsed((value) => !value)} /><main className={cn("flex-1", className)}><PageContainer><motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2 }} className="space-y-6 py-6">{children}</motion.div></PageContainer><Footer /></main></div><DashboardCommandPalette open={commandPaletteOpen} onOpenChange={setCommandPaletteOpen} /></div>;
}
