import { cn } from "@/lib/cn";

export function Table({ children, className }: { children: React.ReactNode; className?: string }): React.JSX.Element {
  return <div className={cn("overflow-hidden rounded-2xl border border-line bg-panel", className)}><table className="w-full border-collapse text-left text-sm">{children}</table></div>;
}

export function Breadcrumb({ items }: { items: Array<{ label: string; href?: string }> }): React.JSX.Element {
  return <nav aria-label="Breadcrumb" className="flex items-center gap-2 text-sm text-muted">{items.map((item, index) => (<span key={item.label} className="flex items-center gap-2">{index > 0 ? <span>/</span> : null}{item.href ? <a className="hover:text-text" href={item.href}>{item.label}</a> : <span className="text-text">{item.label}</span>}</span>))}</nav>;
}

export function Pagination({ page, pageSize, total, onPageChange }: { page: number; pageSize: number; total: number; onPageChange: (page: number) => void }): React.JSX.Element {
  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  return <div className="flex items-center justify-between gap-3 text-sm text-muted"><span>Page {page} of {totalPages}</span><div className="flex gap-2"><button className="rounded-xl border border-line px-3 py-2 text-text disabled:opacity-50" disabled={page <= 1} onClick={() => onPageChange(page - 1)}>Previous</button><button className="rounded-xl border border-line px-3 py-2 text-text disabled:opacity-50" disabled={page >= totalPages} onClick={() => onPageChange(page + 1)}>Next</button></div></div>;
}

export function EmptyState({ title, description }: { title: string; description?: string }): React.JSX.Element {
  return <div className="rounded-2xl border border-dashed border-line bg-canvas p-8 text-center"><div className="text-base font-semibold text-text">{title}</div>{description ? <div className="mt-2 text-sm text-muted">{description}</div> : null}</div>;
}
