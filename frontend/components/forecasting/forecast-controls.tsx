"use client";

import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ForecastControls as Controls } from "@/types/forecast";

interface ForecastControlsProps {
  products: { id: string; name: string }[];
  categories: string[];
  controls: Controls;
  onControlsChange: (controls: Controls) => void;
}

export function ForecastControls({
  products,
  categories,
  controls,
  onControlsChange,
}: ForecastControlsProps) {
  return (
    <div className="flex flex-wrap items-end gap-4">
      <div className="space-y-2">
        <Label>Product</Label>
        <Select
          value={controls.productId}
          onValueChange={(v) => v && onControlsChange({ ...controls, productId: v })}
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue placeholder="Select product" />
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
          value={controls.category}
          onValueChange={(v) => v && onControlsChange({ ...controls, category: v })}
        >
          <SelectTrigger className="w-[160px]">
            <SelectValue placeholder="All categories" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map((c) => (
              <SelectItem key={c} value={c}>
                {c}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>Forecast Horizon</Label>
        <Select
          value={String(controls.horizon)}
          onValueChange={(v) =>
            v && onControlsChange({ ...controls, horizon: Number(v) })
          }
        >
          <SelectTrigger className="w-[160px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1">1 Month</SelectItem>
            <SelectItem value="3">3 Months</SelectItem>
            <SelectItem value="6">6 Months</SelectItem>
            <SelectItem value="12">12 Months</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="space-y-2">
        <Label>Forecast Method</Label>
        <Select
          value={controls.method}
          onValueChange={(v) =>
            v &&
            onControlsChange({
              ...controls,
              method: v as "moving-average" | "exponential-smoothing",
            })
          }
        >
          <SelectTrigger className="w-[200px]">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="moving-average">Moving Average</SelectItem>
            <SelectItem value="exponential-smoothing">
              Exponential Smoothing
            </SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex items-center gap-2 pb-1">
        <span className="text-sm text-muted-foreground">Method:</span>
        <Badge variant="secondary">
          {controls.method === "moving-average"
            ? "Moving Average"
            : "Exponential Smoothing"}
        </Badge>
      </div>
    </div>
  );
}
