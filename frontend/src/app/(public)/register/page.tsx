import Link from "next/link";

import { RegisterForm } from "@/components/forms/auth-forms";

export default function RegisterPage(): React.JSX.Element {
  return <div className="grid gap-6 lg:grid-cols-[1fr_auto]"><div className="max-w-xl space-y-4"><h2 className="text-4xl font-semibold tracking-tight">Create an enterprise account</h2><p className="text-muted">Provision access with validated identity and session controls.</p><div className="text-sm text-muted">Already registered? <Link className="text-primary hover:underline" href="/login">Sign in</Link>.</div></div><RegisterForm /></div>;
}
