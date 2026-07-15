"use client";

import { useEffect } from "react";

export function Dialog({ open, title, onClose, children }: { open: boolean; title: string; onClose: () => void; children: React.ReactNode }): React.JSX.Element | null {
  useEffect(() => {
    function onKeyDown(event: KeyboardEvent): void {
      if (event.key === "Escape") onClose();
    }
    if (open) {
      document.addEventListener("keydown", onKeyDown);
      return () => document.removeEventListener("keydown", onKeyDown);
    }
    return undefined;
  }, [open, onClose]);

  if (!open) return null;
  return <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/55 p-4"><div role="dialog" aria-modal="true" aria-labelledby={title} className="w-full max-w-2xl rounded-2xl border border-line bg-panel p-6 shadow-soft"><div className="mb-4 flex items-center justify-between"><h2 className="text-lg font-semibold text-text">{title}</h2><button className="rounded-full px-2 py-1 text-muted hover:bg-canvas" onClick={onClose}>Close</button></div>{children}</div></div>;
}

export function Tooltip({ label, children }: { label: string; children: React.ReactNode }): React.JSX.Element {
  return <span className="group relative inline-flex">{children}<span role="tooltip" className="pointer-events-none absolute left-1/2 top-full z-20 mt-2 w-max -translate-x-1/2 rounded-lg bg-text px-3 py-1.5 text-xs text-canvas opacity-0 transition group-hover:opacity-100">{label}</span></span>;
}

export function Popover({ trigger, content }: { trigger: React.ReactNode; content: React.ReactNode }): React.JSX.Element {
  return <details className="relative inline-block"><summary className="list-none">{trigger}</summary><div className="absolute right-0 z-20 mt-2 min-w-72 rounded-2xl border border-line bg-panel p-4 shadow-soft">{content}</div></details>;
}

export function Tabs({ tabs, activeTab, onChange }: { tabs: Array<{ id: string; label: string }>; activeTab: string; onChange: (id: string) => void }): React.JSX.Element {
  return <div className="flex flex-wrap gap-2 rounded-2xl bg-canvas p-1">{tabs.map((tab) => <button key={tab.id} aria-pressed={activeTab === tab.id} className={`rounded-xl px-4 py-2 text-sm font-medium ${activeTab === tab.id ? "bg-panel text-text shadow-soft" : "text-muted hover:text-text"}`} onClick={() => onChange(tab.id)}>{tab.label}</button>)}</div>;
}
