import Link from "next/link";

import { ForgotPasswordForm } from "@/components/forms/auth-forms";

export default function ForgotPasswordPage(): React.JSX.Element {
  return <div className="grid gap-6 lg:grid-cols-[1fr_auto]"><div className="max-w-xl space-y-4"><h2 className="text-4xl font-semibold tracking-tight">Reset access safely</h2><p className="text-muted">Request a secure password reset email for your account.</p><div className="text-sm text-muted"><Link className="text-primary hover:underline" href="/login">Return to login</Link>.</div></div><ForgotPasswordForm /></div>;
}
