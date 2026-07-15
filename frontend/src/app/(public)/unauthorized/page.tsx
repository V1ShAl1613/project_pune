import Link from "next/link";

import { Card } from "@/components/ui/surfaces";

export default function UnauthorizedPage(): React.JSX.Element {
  return <Card className="max-w-xl text-center"><h2 className="text-3xl font-semibold">Unauthorized</h2><p className="mt-3 text-sm text-muted">You do not have permission to view this resource.</p><div className="mt-6"><Link className="text-primary hover:underline" href="/login">Sign in</Link></div></Card>;
}
