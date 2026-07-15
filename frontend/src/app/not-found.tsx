import Link from "next/link";

import { Button } from "@/components/ui/controls";
import { Card } from "@/components/ui/surfaces";

export default function NotFound(): React.JSX.Element {
  return <main className="flex min-h-screen items-center justify-center px-4"><Card className="max-w-md text-center"><h1 className="text-3xl font-semibold">404</h1><p className="mt-3 text-sm text-muted">The requested page is not available.</p><div className="mt-6 flex justify-center gap-3"><Link href="/"><Button>Go home</Button></Link><Link href="/dashboard"><Button variant="secondary">Dashboard</Button></Link></div></Card></main>;
}
