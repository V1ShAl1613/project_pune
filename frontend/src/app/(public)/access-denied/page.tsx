import Link from "next/link";

import { Card } from "@/components/ui/surfaces";

export default function AccessDeniedPage(): React.JSX.Element {
  return <Card className="max-w-xl text-center"><h2 className="text-3xl font-semibold">Access denied</h2><p className="mt-3 text-sm text-muted">Your session is valid, but you do not have access to this resource.</p><div className="mt-6"><Link className="text-primary hover:underline" href="/dashboard">Return to dashboard</Link></div></Card>;
}
