import Link from "next/link";
import type { Route } from "next";
import { ArrowRight, ShieldCheck, Sparkles, Users, LayoutDashboard } from "lucide-react";

import { Button } from "@/components/ui/controls";
import { Card, StatusBadge } from "@/components/ui/surfaces";
import { publicNavigation } from "@/constants/navigation";

export default function HomePage(): React.JSX.Element {
  return <main className="min-h-screen"><section className="mx-auto grid min-h-screen max-w-7xl gap-10 px-4 py-10 sm:px-6 lg:grid-cols-[1.2fr_0.8fr] lg:px-8"><div className="flex flex-col justify-center gap-8"><StatusBadge status="active" /><div className="space-y-4"><h1 className="max-w-3xl text-5xl font-semibold tracking-tight text-text sm:text-6xl">Enterprise frontend foundation for Sentinel Fusion AI.</h1><p className="max-w-2xl text-lg text-muted">A responsive, accessible control plane for enterprise identity, organization management, authentication, and secure settings workflows.</p></div><div className="flex flex-wrap gap-3"><Link href="/login"><Button>Open control plane <ArrowRight className="h-4 w-4" /></Button></Link><Link href="/dashboard"><Button variant="secondary">Go to dashboard</Button></Link></div><div className="grid gap-4 sm:grid-cols-3"><FeatureCard icon={<ShieldCheck className="h-5 w-5" />} title="Secure by design" description="Protected routes, session-aware shell, and API-aware state." /><FeatureCard icon={<LayoutDashboard className="h-5 w-5" />} title="Reusable layouts" description="Main, auth, settings, dashboard, blank, and error shells." /><FeatureCard icon={<Users className="h-5 w-5" />} title="Enterprise forms" description="RHF + Zod-driven forms for auth and identity workflows." /></div></div><Card className="self-center"><div className="space-y-4"><div className="flex items-center gap-3"><div className="rounded-2xl bg-primary p-3 text-primary-foreground"><Sparkles className="h-6 w-6" /></div><div><div className="text-lg font-semibold">Navigation</div><div className="text-sm text-muted">Public entry points</div></div></div><div className="space-y-2">{publicNavigation.map((item) => <Link key={item.href} href={item.href as Route} className="flex items-center justify-between rounded-xl border border-line px-4 py-3 text-sm hover:bg-canvas"><span>{item.label}</span><ArrowRight className="h-4 w-4 text-muted" /></Link>)}</div></div></Card></section></main>;
}

function FeatureCard({ icon, title, description }: { icon: React.ReactNode; title: string; description: string }): React.JSX.Element {
  return <div className="rounded-2xl border border-line bg-panel p-4 shadow-soft"><div className="mb-3 inline-flex rounded-xl bg-primary/10 p-2 text-primary">{icon}</div><div className="text-sm font-semibold text-text">{title}</div><div className="mt-1 text-sm text-muted">{description}</div></div>;
}
