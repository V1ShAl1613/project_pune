"use client";

// Reusable Recharts charts for SOC trend and workload visualization.
import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis, Bar, BarChart, Pie, PieChart, Cell, Legend } from "recharts";

import { Card } from "@/components/ui/surfaces";

type ChartPoint = { label: string; value: number; valueB?: number; name?: string };

const colors = ["#2563eb", "#0b4458", "#14b8a6", "#f97316", "#ef4444"];

export function TrendChart({ title, description, data }: { title: string; description: string; data: ChartPoint[] }): React.JSX.Element {
  return <Card className="space-y-4"><div><h3 className="text-base font-semibold text-text">{title}</h3><p className="text-sm text-muted">{description}</p></div><div className="h-64"><ResponsiveContainer width="100%" height="100%"><AreaChart data={data}><defs><linearGradient id="socTrend" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#2563eb" stopOpacity={0.35} /><stop offset="95%" stopColor="#2563eb" stopOpacity={0.02} /></linearGradient></defs><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="label" /><YAxis /><Tooltip /><Area type="monotone" dataKey="value" stroke="#2563eb" fill="url(#socTrend)" strokeWidth={2} /></AreaChart></ResponsiveContainer></div></Card>;
}

export function WorkloadChart({ title, description, data }: { title: string; description: string; data: ChartPoint[] }): React.JSX.Element {
  return <Card className="space-y-4"><div><h3 className="text-base font-semibold text-text">{title}</h3><p className="text-sm text-muted">{description}</p></div><div className="h-64"><ResponsiveContainer width="100%" height="100%"><BarChart data={data}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="label" /><YAxis /><Tooltip /><Bar dataKey="value" fill="#0b4458" radius={[8, 8, 0, 0]} /></BarChart></ResponsiveContainer></div></Card>;
}

export function DistributionChart({ title, description, data }: { title: string; description: string; data: ChartPoint[] }): React.JSX.Element {
  return <Card className="space-y-4"><div><h3 className="text-base font-semibold text-text">{title}</h3><p className="text-sm text-muted">{description}</p></div><div className="h-64"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={data} dataKey="value" nameKey="label" innerRadius={60} outerRadius={90} paddingAngle={3}>{data.map((entry, index) => <Cell key={entry.label} fill={colors[index % colors.length]} />)}</Pie><Tooltip /><Legend /></PieChart></ResponsiveContainer></div></Card>;
}
