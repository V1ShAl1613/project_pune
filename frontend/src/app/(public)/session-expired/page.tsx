import Link from "next/link";

import { Card } from "@/components/ui/surfaces";

export default function SessionExpiredPage(): React.JSX.Element {
  return <Card className="max-w-xl text-center"><h2 className="text-3xl font-semibold">Session expired</h2><p className="mt-3 text-sm text-muted">Your session has ended. Sign in again to continue.</p><div className="mt-6"><Link className="text-primary hover:underline" href="/login">Sign in</Link></div></Card>;
}
