"use client";

import { useState } from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
} from "@tanstack/react-table";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowUpDown } from "lucide-react";
import { cn } from "@/lib/utils";
import { InventoryPlanItem } from "@/types/inventory";

interface InventoryTableProps {
  data: InventoryPlanItem[];
}

const statusConfig = {
  healthy: {
    label: "Healthy",
    className:
      "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
  },
  "reorder-soon": {
    label: "Reorder Soon",
    className:
      "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
  },
  "reorder-now": {
    label: "Reorder Now",
    className:
      "bg-orange-500/10 text-orange-600 dark:text-orange-400 border-orange-500/20",
  },
  critical: {
    label: "Critical",
    className:
      "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20",
  },
};

export function InventoryTable({ data }: InventoryTableProps) {
  const [sorting, setSorting] = useState<SortingState>([]);

  const columns: ColumnDef<InventoryPlanItem>[] = [
    {
      accessorKey: "sku",
      header: "SKU",
    },
    {
      accessorKey: "productName",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="-ml-4"
        >
          Product Name
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
    },
    {
      accessorKey: "currentStock",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="-ml-4"
        >
          Current Stock
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => (
        <div className="text-right">
          {row.getValue<number>("currentStock").toLocaleString()}
        </div>
      ),
    },
    {
      accessorKey: "forecastDemand",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="-ml-4"
        >
          Forecast Demand
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => (
        <div className="text-right">
          {row.getValue<number>("forecastDemand").toLocaleString()}
        </div>
      ),
    },
    {
      accessorKey: "safetyStock",
      header: "Safety Stock",
      cell: ({ row }) => (
        <div className="text-right">
          {row.getValue<number>("safetyStock").toLocaleString()}
        </div>
      ),
    },
    {
      accessorKey: "reorderPoint",
      header: "Reorder Point",
      cell: ({ row }) => (
        <div className="text-right">
          {row.getValue<number>("reorderPoint").toLocaleString()}
        </div>
      ),
    },
    {
      accessorKey: "eoq",
      header: "EOQ",
      cell: ({ row }) => (
        <div className="text-right">
          {row.getValue<number>("eoq").toLocaleString()}
        </div>
      ),
    },
    {
      accessorKey: "recommendedOrder",
      header: ({ column }) => (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="-ml-4"
        >
          Recommended Order
          <ArrowUpDown className="ml-2 h-4 w-4" />
        </Button>
      ),
      cell: ({ row }) => {
        const val = row.getValue<number>("recommendedOrder");
        return (
          <div
            className={cn(
              "text-right font-medium",
              val > 0 ? "text-amber-600 dark:text-amber-400" : "text-muted-foreground"
            )}
          >
            {val > 0 ? val.toLocaleString() : "—"}
          </div>
        );
      },
    },
    {
      accessorKey: "status",
      header: "Status",
      cell: ({ row }) => {
        const status = row.getValue<keyof typeof statusConfig>("status");
        const config = statusConfig[status];
        return (
          <Badge className={cn(config.className)} variant="outline">
            {config.label}
          </Badge>
        );
      },
    },
  ];

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    state: { sorting },
    initialState: { pagination: { pageSize: 8 } },
  });

  return (
    <div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id}>
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No inventory data found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="flex items-center justify-end space-x-2 py-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => table.previousPage()}
          disabled={!table.getCanPreviousPage()}
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => table.nextPage()}
          disabled={!table.getCanNextPage()}
        >
          Next
        </Button>
      </div>
    </div>
  );
}
