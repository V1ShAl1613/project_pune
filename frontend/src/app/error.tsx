"use client";

import Link from "next/link";
import { useEffect } from "react";

import { Button } from "@/components/ui/controls";
import { Card } from "@/components/ui/surfaces";

export default function Error({ error, reset }: { error: Error & { digest?: string }; reset: () => void }): React.JSX.Element {
  useEffect(() => {
    console.error(error);
  }, [error]);

  return <main className="flex min-h-screen items-center justify-center px-4"><Card className="max-w-lg text-center"><h1 className="text-3xl font-semibold">Something went wrong</h1><p className="mt-3 text-sm text-muted">The application could not complete this request.</p><div className="mt-6 flex justify-center gap-3"><Button onClick={reset}>Retry</Button><Link href="/"><Button variant="secondary">Home</Button></Link></div></Card></main>;
}
