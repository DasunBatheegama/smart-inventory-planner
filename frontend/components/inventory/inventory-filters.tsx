"use client";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { InventoryFilters as Filters } from "@/types/inventory";

interface InventoryFiltersProps {
  products: { id: string; name: string }[];
  categories: string[];
  suppliers: string[];
  statuses: { value: string; label: string }[];
  filters: Filters;
  onFiltersChange: (filters: Filters) => void;
}

export function InventoryFilters({
  products,
  categories,
  suppliers,
  statuses,
  filters,
  onFiltersChange,
}: InventoryFiltersProps) {
  return (
    <div className="flex flex-wrap items-end gap-4">
      <div className="space-y-2">
        <Label>Product</Label>
        <Select
          value={filters.product}
          onValueChange={(v) =>
            v && onFiltersChange({ ...filters, product: v })
          }
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="All Products" />
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
        <Label>Category</Label>
        <Select
          value={filters.category}
          onValueChange={(v) =>
            v && onFiltersChange({ ...filters, category: v })
          }
        >
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="All Categories" />
          </SelectTrigger>
          <SelectContent>
            {categories.map((c) => (
              <SelectItem key={c} value={c}>
                {c}
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
            <SelectValue placeholder="All Suppliers" />
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
        <Label>Status</Label>
        <Select
          value={filters.status}
          onValueChange={(v) =>
            v && onFiltersChange({ ...filters, status: v })
          }
        >
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="All Statuses" />
          </SelectTrigger>
          <SelectContent>
            {statuses.map((s) => (
              <SelectItem key={s.value} value={s.value}>
                {s.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
    </div>
  );
}
