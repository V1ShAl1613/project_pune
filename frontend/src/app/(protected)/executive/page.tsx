"use client";

import { useQuery } from "@tanstack/react-query";
import { ArrowDownRight, ArrowUpRight, BarChart3, BrainCircuit, ClipboardList, ShieldCheck, TrendingUp } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { Badge, Card, StatusBadge, Spinner } from "@/components/ui/surfaces";
import { Table, EmptyState } from "@/components/ui/data-display";
import { getExecutiveOverview } from "@/services/api/executive-api";
import type { ExecutiveForecast, ExecutiveKPI, ExecutiveRecommendation, ExecutiveReport, ExecutiveTrend } from "@/types/executive";

export default function ExecutivePage(): React.JSX.Element {
  const { data, isLoading, isError } = useQuery({ queryKey: ["executive-overview"], queryFn: getExecutiveOverview });

  if (isLoading) {
    return <div className="flex min-h-[40vh] items-center justify-center"><Spinner label="Loading executive intelligence" /></div>;
  }

  if (isError || !data) {
    return <EmptyState title="Executive intelligence unavailable" description="The analytics and reporting service could not be loaded." />;
  }

  return <div className="space-y-6 pb-8"><Card className="bg-gradient-to-br from-panel via-panel to-canvas"><div className="flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between"><div className="max-w-3xl space-y-4"><div className="flex items-center gap-2 text-xs uppercase tracking-[0.3em] text-muted"><BrainCircuit className="h-4 w-4" />Executive intelligence</div><h1 className="text-3xl font-semibold tracking-tight text-text sm:text-4xl">{data.summary.title}</h1><p className="max-w-2xl text-sm leading-6 text-muted sm:text-base">{data.summary.narrative}</p><div className="flex flex-wrap gap-2"><Badge tone="success">{data.summary.operating_status}</Badge><Badge tone={data.summary.risk_posture === "controlled" ? "success" : "warning"}>Risk posture {data.summary.risk_posture}</Badge><Badge tone="neutral">Decision velocity {data.summary.decision_velocity}</Badge></div></div><div className="grid gap-3 sm:grid-cols-3 xl:w-[28rem]"><MetricPill icon={<ShieldCheck className="h-4 w-4" />} label="Health score" value={`${data.summary.health_score.toFixed(1)}%`} /><MetricPill icon={<TrendingUp className="h-4 w-4" />} label="Reports" value={String(data.reports.length)} /><MetricPill icon={<ClipboardList className="h-4 w-4" />} label="Decisions" value={String(data.decisions.length)} /></div></div></Card><section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{data.kpis.map((kpi) => <KpiCard key={kpi.code} kpi={kpi} />)}</section><section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]"><Card><div className="mb-4 flex items-center justify-between gap-3"><div><h2 className="text-lg font-semibold text-text">Executive trends</h2><p className="text-sm text-muted">Operational performance, risk, and decision cadence over the last review cycle.</p></div><BarChart3 className="h-5 w-5 text-muted" /></div><div className="grid gap-4 xl:grid-cols-3">{data.trends.map((trend) => <TrendChart key={trend.code} trend={trend} />)}</div></Card><Card><div className="mb-4 flex items-center justify-between gap-3"><div><h2 className="text-lg font-semibold text-text">Forecast scenarios</h2><p className="text-sm text-muted">Base, upside, and downside cases for executive review.</p></div><ArrowUpRight className="h-5 w-5 text-muted" /></div><div className="space-y-4">{data.forecasts.map((forecast) => <ForecastCard key={forecast.scenario} forecast={forecast} />)}</div></Card></section><section className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]"><Card><div className="mb-4 flex items-center justify-between gap-3"><div><h2 className="text-lg font-semibold text-text">Reports</h2><p className="text-sm text-muted">Executive reporting, board packs, and operating reviews.</p></div><ClipboardList className="h-5 w-5 text-muted" /></div>{data.reports.length ? <ReportTable reports={data.reports} /> : <EmptyState title="No reports" description="Report records will appear here once generated." />}</Card><div className="space-y-6"><Card><div className="mb-4 flex items-center justify-between gap-3"><div><h2 className="text-lg font-semibold text-text">Recommendations</h2><p className="text-sm text-muted">Prioritized decision support for leaders.</p></div><ArrowDownRight className="h-5 w-5 text-muted" /></div><div className="space-y-3">{data.recommendations.map((recommendation) => <RecommendationItem key={recommendation.title} recommendation={recommendation} />)}</div></Card><Card><div className="mb-4 flex items-center justify-between gap-3"><div><h2 className="text-lg font-semibold text-text">Decision log</h2><p className="text-sm text-muted">Approved and in-flight decisions ready for review.</p></div></div><div className="space-y-3">{data.decisions.map((decision) => <DecisionItem key={decision.decision_code} decision={decision} />)}</div></Card></div></section></div>;
}

function KpiCard({ kpi }: { kpi: ExecutiveKPI }): React.JSX.Element {
  const icon = kpi.direction === "up" ? <ArrowUpRight className="h-4 w-4" /> : kpi.direction === "down" ? <ArrowDownRight className="h-4 w-4" /> : <TrendingUp className="h-4 w-4" />;
  const tone = kpi.direction === "up" ? "success" : kpi.direction === "down" ? "warning" : "neutral";
  return <Card><div className="flex items-start justify-between gap-4"><div><p className="text-sm text-muted">{kpi.label}</p><div className="mt-2 text-3xl font-semibold text-text">{kpi.value}</div><p className="mt-1 text-xs uppercase tracking-wide text-muted">{kpi.benchmark ? `Benchmark ${kpi.benchmark}` : kpi.detail}</p></div><Badge tone={tone}>{icon}{kpi.delta ?? "steady"}</Badge></div><p className="mt-4 text-sm leading-6 text-muted">{kpi.detail}</p></Card>;
}

function TrendChart({ trend }: { trend: ExecutiveTrend }): React.JSX.Element {
  return <div className="rounded-2xl border border-line bg-canvas p-4"><div className="mb-3 text-sm font-semibold text-text">{trend.label}</div><div className="mb-2 text-xs text-muted">{trend.summary}</div><div className="h-36"><ResponsiveContainer width="100%" height="100%"><AreaChart data={trend.points}><defs><linearGradient id={trend.code} x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="var(--primary)" stopOpacity={0.35} /><stop offset="95%" stopColor="var(--primary)" stopOpacity={0} /></linearGradient></defs><XAxis dataKey="label" axisLine={false} tickLine={false} tick={{ fontSize: 12 }} /><YAxis hide domain={["dataMin - 5", "dataMax + 5"]} /><Tooltip /><CartesianGrid strokeDasharray="3 3" strokeOpacity={0.15} /><Area type="monotone" dataKey="value" stroke="var(--primary)" fill={`url(#${trend.code})`} strokeWidth={2} /></AreaChart></ResponsiveContainer></div></div>;
}

function ForecastCard({ forecast }: { forecast: ExecutiveForecast }): React.JSX.Element {
  return <div className="rounded-2xl border border-line bg-canvas p-4"><div className="flex items-center justify-between gap-3"><div><div className="text-sm font-semibold text-text">{forecast.scenario}</div><div className="text-xs text-muted">{forecast.horizon}</div></div><Badge tone={forecast.confidence >= 0.85 ? "success" : "warning"}>{Math.round(forecast.confidence * 100)}% confidence</Badge></div><div className="mt-4 grid gap-3 sm:grid-cols-3"><MiniStat label="Projected" value={forecast.projected_value} /><MiniStat label="Range" value={`${forecast.lower_bound} - ${forecast.upper_bound}`} /><MiniStat label="Drivers" value={String(forecast.drivers.length)} /></div><div className="mt-3 text-sm text-muted">{forecast.drivers.join(" · ")}</div></div>;
}

function ReportTable({ reports }: { reports: ExecutiveReport[] }): React.JSX.Element {
  return <Table><thead><tr className="border-b border-line text-xs uppercase tracking-wide text-muted"><th className="px-4 py-3">Report</th><th className="px-4 py-3">Audience</th><th className="px-4 py-3">Status</th><th className="px-4 py-3">Score</th></tr></thead><tbody>{reports.map((report) => <tr key={report.report_code} className="border-b border-line/70 last:border-b-0"><td className="px-4 py-3"><div className="font-medium text-text">{report.title}</div><div className="text-xs text-muted">{report.report_code} · {report.period_label}</div></td><td className="px-4 py-3 text-sm text-muted">{report.audience}</td><td className="px-4 py-3"><StatusBadge status={report.status} /></td><td className="px-4 py-3 text-sm font-medium text-text">{report.score.toFixed(1)}</td></tr>)}</tbody></Table>;
}

function RecommendationItem({ recommendation }: { recommendation: ExecutiveRecommendation }): React.JSX.Element {
  return <div className="rounded-2xl border border-line bg-canvas p-4"><div className="flex items-start justify-between gap-3"><div><div className="text-sm font-semibold text-text">{recommendation.title}</div><div className="mt-1 text-xs text-muted">Owner: {recommendation.owner} · Horizon: {recommendation.horizon}</div></div><Badge tone={recommendation.priority === "critical" ? "danger" : recommendation.priority === "high" ? "warning" : "neutral"}>{recommendation.priority}</Badge></div><p className="mt-3 text-sm leading-6 text-muted">{recommendation.action}</p><p className="mt-2 text-sm leading-6 text-muted">{recommendation.expected_impact}</p></div>;
}

function DecisionItem({ decision }: { decision: { decision_code: string; topic: string; decision: string; status: string; impact: string } }): React.JSX.Element {
  return <div className="rounded-2xl border border-line bg-canvas p-4"><div className="flex items-start justify-between gap-3"><div><div className="text-sm font-semibold text-text">{decision.topic}</div><div className="mt-1 text-xs text-muted">{decision.decision_code}</div></div><StatusBadge status={decision.status} /></div><p className="mt-3 text-sm leading-6 text-muted">{decision.decision}</p><p className="mt-2 text-xs uppercase tracking-wide text-muted">{decision.impact}</p></div>;
}

function MetricPill({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }): React.JSX.Element {
  return <div className="rounded-2xl border border-line/70 bg-panel/80 p-4 backdrop-blur"><div className="flex items-center justify-between text-muted">{icon}<span className="text-xs uppercase tracking-wide">{label}</span></div><div className="mt-3 text-2xl font-semibold text-text">{value}</div></div>;
}

function MiniStat({ label, value }: { label: string; value: string }): React.JSX.Element {
  return <div><div className="text-[11px] uppercase tracking-wide text-muted">{label}</div><div className="mt-1 text-sm font-medium text-text">{value}</div></div>;
}
