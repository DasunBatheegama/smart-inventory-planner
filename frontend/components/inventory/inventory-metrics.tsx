"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { InventoryPlanItem } from "@/types/inventory";

interface InventoryMetricsProps {
  items: InventoryPlanItem[];
}

export function InventoryMetrics({ items }: InventoryMetricsProps) {
  const totalSafetyStock = items.reduce((s, i) => s + i.safetyStock, 0);
  const totalEoq = items.reduce((s, i) => s + i.eoq, 0);
  const totalRecommendedOrder = items.reduce(
    (s, i) => s + i.recommendedOrder,
    0
  );
  const avgDaysRemaining =
    items.length > 0
      ? Math.round(
          items.reduce((s, i) => s + i.daysRemaining, 0) / items.length
        )
      : 0;

  const metrics = [
    {
      label: "Current Stock",
      value: items.reduce((s, i) => s + i.currentStock, 0).toLocaleString(),
    },
    {
      label: "Forecast Demand",
      value: items.reduce((s, i) => s + i.forecastDemand, 0).toLocaleString(),
    },
    { label: "Safety Stock", value: totalSafetyStock.toLocaleString() },
    { label: "Total EOQ", value: totalEoq.toLocaleString() },
    {
      label: "Recommended Orders",
      value: totalRecommendedOrder.toLocaleString(),
    },
    { label: "Avg Days Remaining", value: avgDaysRemaining.toString() },
  ];

  return (
    <div className="grid grid-cols-3 gap-3">
      {metrics.map((m) => (
        <Card key={m.label}>
          <CardHeader className="p-3 pb-0">
            <CardTitle className="text-xs font-medium text-muted-foreground">
              {m.label}
            </CardTitle>
          </CardHeader>
          <CardContent className="p-3 pt-1">
            <p className="text-lg font-bold">{m.value}</p>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
