import Link from "next/link";

import { Card } from "@/components/ui/surfaces";

export default function EmailVerificationPage(): React.JSX.Element {
  return <Card className="max-w-xl text-center"><h2 className="text-3xl font-semibold">Verify your email</h2><p className="mt-3 text-sm text-muted">Open the verification link sent to your inbox to activate your account.</p><div className="mt-6"><Link className="text-primary hover:underline" href="/login">Return to login</Link></div></Card>;
}
