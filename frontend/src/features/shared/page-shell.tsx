import { Breadcrumb, EmptyState } from "@/components/ui/data-display";
import { Card } from "@/components/ui/surfaces";

export function EntityPageShell({ title, description, breadcrumbs, children }: { title: string; description: string; breadcrumbs: Array<{ label: string; href?: string }>; children: React.ReactNode }): React.JSX.Element {
  return <div className="space-y-6"><Breadcrumb items={breadcrumbs} /><Card><div className="space-y-2"><h1 className="text-3xl font-semibold">{title}</h1><p className="text-sm text-muted">{description}</p></div>{children}</Card></div>;
}

export function PageEmptyState({ title, description }: { title: string; description: string }): React.JSX.Element {
  return <EmptyState title={title} description={description} />;
}
