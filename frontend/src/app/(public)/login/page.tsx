import Link from "next/link";

import { LoginForm } from "@/components/forms/auth-forms";

export default function LoginPage(): React.JSX.Element {
  return <div className="grid gap-6 lg:grid-cols-[1fr_auto]"><div className="max-w-xl space-y-4"><h2 className="text-4xl font-semibold tracking-tight">Welcome back</h2><p className="text-muted">Authenticate to continue into the enterprise control plane.</p><div className="text-sm text-muted">Need an account? <Link className="text-primary hover:underline" href="/register">Register here</Link>.</div></div><LoginForm /></div>;
}
