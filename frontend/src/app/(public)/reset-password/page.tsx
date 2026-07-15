import Link from "next/link";

import { ResetPasswordForm } from "@/components/forms/auth-forms";

export default function ResetPasswordPage(): React.JSX.Element {
  return <div className="grid gap-6 lg:grid-cols-[1fr_auto]"><div className="max-w-xl space-y-4"><h2 className="text-4xl font-semibold tracking-tight">Set a new password</h2><p className="text-muted">Complete the password reset using your secure token.</p><div className="text-sm text-muted"><Link className="text-primary hover:underline" href="/login">Back to login</Link>.</div></div><ResetPasswordForm /></div>;
}
