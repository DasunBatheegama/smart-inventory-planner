"use client";

import { useMemo } from "react";
import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  useReactTable,
} from "@tanstack/react-table";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { SalesRecord } from "@/types/sales";

interface UploadPreviewProps {
  records: SalesRecord[];
}

export function UploadPreview({ records }: UploadPreviewProps) {
  const previewData = useMemo(() => records.slice(0, 20), [records]);

  const columns: ColumnDef<SalesRecord>[] = [
    {
      accessorKey: "date",
      header: "Date",
    },
    {
      accessorKey: "sku",
      header: "SKU",
    },
    {
      accessorKey: "quantitySold",
      header: "Quantity Sold",
    },
  ];

  const table = useReactTable({
    data: previewData,
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (records.length === 0) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <p className="text-sm font-medium">
          Preview{" "}
          <span className="text-muted-foreground font-normal">
            (first {Math.min(20, records.length)} of {records.length} records)
          </span>
        </p>
      </div>
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
            {table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => (
                  <TableCell key={cell.id}>
                    {flexRender(cell.column.columnDef.cell, cell.getContext())}
                  </TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
