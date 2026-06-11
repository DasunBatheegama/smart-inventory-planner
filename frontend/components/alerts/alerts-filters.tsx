"use client";

import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search } from "lucide-react";
import { AlertFilters as Filters } from "@/types/alert";

interface AlertsFiltersProps {
  products: { id: string; name: string }[];
  suppliers: string[];
  alertTypes: { value: string; label: string }[];
  severities: { value: string; label: string }[];
  dateRanges: { value: string; label: string }[];
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
}

export function AlertsFilters({
  products,
  suppliers,
  alertTypes,
  severities,
  dateRanges,
  filters,
  onFiltersChange,
}: AlertsFiltersProps) {
  return (
    <div className="flex flex-wrap items-end gap-4">
      <div className="space-y-2">
        <Label>Alert Type</Label>
        <Select
          value={filters.type}
          onValueChange={(v) =>
            v && onFiltersChange({ ...filters, type: v })
          }
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {alertTypes.map((t) => (
              <SelectItem key={t.value} value={t.value}>
                {t.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>Severity</Label>
        <Select
          value={filters.severity}
          onValueChange={(v) =>
            v && onFiltersChange({ ...filters, severity: v })
          }
        >
          <SelectTrigger className="w-[160px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {severities.map((s) => (
              <SelectItem key={s.value} value={s.value}>
                {s.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>Product</Label>
        <Select
          value={filters.product}
          onValueChange={(v) =>
            v && onFiltersChange({ ...filters, product: v })
          }
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {products.map((p) => (
              <SelectItem key={p.id} value={p.id}>
                {p.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>Supplier</Label>
        <Select
          value={filters.supplier}
          onValueChange={(v) =>
            v && onFiltersChange({ ...filters, supplier: v })
          }
        >
          <SelectTrigger className="w-[180px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {suppliers.map((s) => (
              <SelectItem key={s} value={s}>
                {s}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>Date Range</Label>
        <Select
          value={filters.dateRange}
          onValueChange={(v) =>
            v && onFiltersChange({ ...filters, dateRange: v })
          }
        >
          <SelectTrigger className="w-[150px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {dateRanges.map((d) => (
              <SelectItem key={d.value} value={d.value}>
                {d.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>Search</Label>
        <div className="relative">
          <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search alerts..."
            className="w-[200px] pl-9"
            value={filters.search}
            onChange={(e) =>
              onFiltersChange({ ...filters, search: e.target.value })
            }
          />
        </div>
      </div>
    </div>
  );
}
