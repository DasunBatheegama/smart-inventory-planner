"use client";

import {
  ComposedChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";
import { TrendDataPoint } from "@/types/inventory";

interface InventoryChartProps {
  data: TrendDataPoint[];
}

export function InventoryChart({ data }: InventoryChartProps) {
  return (
    <ResponsiveContainer width="100%" height={320}>
      <ComposedChart
        data={data}
        margin={{ top: 20, right: 20, bottom: 20, left: 20 }}
      >
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        <XAxis
          dataKey="month"
          tick={{ fontSize: 12 }}
          className="text-muted-foreground"
          tickFormatter={(v: string) => {
            const [y, m] = v.split("-");
            const months = [
              "J", "F", "M", "A", "M", "J",
              "J", "A", "S", "O", "N", "D",
            ];
            return `${months[parseInt(m) - 1]} ${y.slice(2)}`;
          }}
        />
        <YAxis
          tick={{ fontSize: 12 }}
          className="text-muted-foreground"
          tickFormatter={(v: number) => `${(v / 1000).toFixed(0)}k`}
        />
        <Tooltip
          contentStyle={{
            borderRadius: "8px",
            border: "1px solid hsl(var(--border))",
            background: "hsl(var(--popover))",
          }}
          labelFormatter={(label) => {
            if (typeof label !== "string") return label;
            const [y, m] = label.split("-");
            const months = [
              "Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
            ];
            return `${months[parseInt(m) - 1]} ${y}`;
          }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="inventoryLevel"
          stroke="hsl(var(--chart-1))"
          strokeWidth={2}
          dot={false}
          name="Inventory Level"
        />
        <Line
          type="monotone"
          dataKey="forecastDemand"
          stroke="hsl(var(--chart-2))"
          strokeWidth={2}
          dot={false}
          name="Forecast Demand"
        />
        <Line
          type="monotone"
          dataKey="safetyStockThreshold"
          stroke="hsl(var(--chart-3))"
          strokeWidth={2}
          strokeDasharray="6 3"
          dot={false}
          name="Safety Stock Threshold"
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
