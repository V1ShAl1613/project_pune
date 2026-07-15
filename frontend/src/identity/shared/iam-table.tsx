"use client";

// Generic interactive IAM table framework with filtering, sorting, selection, and pagination.
import { useMemo, useState } from "react";
import type { ReactNode } from "react";
import {
  type ColumnDef,
  type ColumnFiltersState,
  type PaginationState,
  type RowSelectionState,
  type SortingState,
  type VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";
import { ChevronDown, ChevronLeft, ChevronRight, Download, RefreshCw, Search } from "lucide-react";

import { Button, Input } from "@/components/ui/controls";
import { cn } from "@/lib/cn";

type IdentityTableProps<TData> = {
  title: string;
  description?: string;
  data: TData[];
  columns: ColumnDef<TData, any>[];
  searchPlaceholder?: string;
  actions?: ReactNode;
  density?: "comfortable" | "compact";
};

export function IdentityTable<TData>({ title, description, data, columns, searchPlaceholder = "Search records", actions, density = "comfortable" }: IdentityTableProps<TData>): React.JSX.Element {
  const [globalFilter, setGlobalFilter] = useState("");
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [rowSelection, setRowSelection] = useState<RowSelectionState>({});
  const [columnVisibility, setColumnVisibility] = useState<VisibilityState>({});
  const [pagination, setPagination] = useState<PaginationState>({ pageIndex: 0, pageSize: 5 });

  const table = useReactTable({
    data,
    columns,
    state: { sorting, columnFilters, rowSelection, columnVisibility, pagination, globalFilter },
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onRowSelectionChange: setRowSelection,
    onColumnVisibilityChange: setColumnVisibility,
    onPaginationChange: setPagination,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    globalFilterFn: (row, _columnId, filterValue) => {
      const query = String(filterValue).toLowerCase();
      return row.getAllCells().some((cell) => String(cell.getValue() ?? "").toLowerCase().includes(query));
    },
  });

  const densityClass = density === "compact" ? "py-2" : "py-3";
  const selectedCount = useMemo(() => Object.keys(rowSelection).length, [rowSelection]);

  return (
    <div className="rounded-3xl border border-line bg-panel shadow-soft">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-4 sm:px-5">
        <div className="space-y-1">
          <div className="text-base font-semibold text-text">{title}</div>
          {description ? <div className="text-sm text-muted">{description}</div> : null}
        </div>
        <div className="flex flex-wrap items-center gap-2">
          {actions}
          <Button variant="secondary" type="button"><RefreshCw className="h-4 w-4" />Refresh</Button>
          <Button variant="secondary" type="button"><Download className="h-4 w-4" />Export</Button>
        </div>
      </div>
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-line px-4 py-4 sm:px-5">
        <label className="flex min-w-[18rem] flex-1 items-center gap-2 rounded-2xl border border-line bg-canvas px-3 py-2 text-sm text-muted">
          <Search className="h-4 w-4" />
          <Input value={globalFilter} onChange={(event) => setGlobalFilter(event.target.value)} placeholder={searchPlaceholder} className="h-auto border-0 bg-transparent px-0 focus-visible:ring-0" />
        </label>
        <div className="text-sm text-muted">{selectedCount > 0 ? `${selectedCount} selected` : `${table.getFilteredRowModel().rows.length} results`}</div>
      </div>

      <div className="overflow-x-auto">
        <table className="min-w-full border-separate border-spacing-0 text-left text-sm">
          <thead className="bg-canvas/80 text-xs uppercase tracking-wide text-muted">
            {table.getHeaderGroups().map((headerGroup) => (
              <tr key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <th key={header.id} className={cn("border-b border-line px-4", densityClass)}>
                    {header.isPlaceholder ? null : (
                      <button type="button" className={cn("inline-flex items-center gap-2 font-semibold text-text", header.column.getCanSort() && "cursor-pointer select-none")} onClick={header.column.getToggleSortingHandler()}>
                        {flexRender(header.column.columnDef.header, header.getContext())}
                        {{ asc: "↑", desc: "↓" }[header.column.getIsSorted() as "asc" | "desc"] ?? <ChevronDown className="h-3.5 w-3.5 text-muted" />}
                      </button>
                    )}
                  </th>
                ))}
              </tr>
            ))}
          </thead>
          <tbody>
            {table.getRowModel().rows.length > 0 ? table.getRowModel().rows.map((row) => (
              <tr key={row.id} className="border-b border-line/70 hover:bg-canvas/60">
                {row.getVisibleCells().map((cell) => (
                  <td key={cell.id} className={cn("px-4 align-top", densityClass)}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </td>
                ))}
              </tr>
            )) : (
              <tr>
                <td colSpan={columns.length} className="px-4 py-10 text-center text-sm text-muted">
                  No records match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-3 border-t border-line px-4 py-4 sm:px-5">
        <div className="text-sm text-muted">
          Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount() || 1}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" type="button" onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}><ChevronLeft className="h-4 w-4" />Previous</Button>
          <Button variant="secondary" type="button" onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>Next<ChevronRight className="h-4 w-4" /></Button>
        </div>
      </div>
    </div>
  );
}