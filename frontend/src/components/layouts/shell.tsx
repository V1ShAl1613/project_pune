import { cn } from "@/lib/cn";

export function PageContainer({ children, className }: { children: React.ReactNode; className?: string }): React.JSX.Element {
  return <div className={cn("mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8", className)}>{children}</div>;
}

export function ContentWrapper({ children, className }: { children: React.ReactNode; className?: string }): React.JSX.Element {
  return <div className={cn("space-y-6 py-6", className)}>{children}</div>;
}
