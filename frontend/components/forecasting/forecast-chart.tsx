"use client";

import {
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  ReferenceLine,
} from "recharts";
import { ForecastData } from "@/types/forecast";

interface ForecastChartProps {
  historical: ForecastData[];
  projection: ForecastData[];
}

export function ForecastChart({ historical, projection }: ForecastChartProps) {
  const separatorIndex = historical.length;
  const chartData = [
    ...historical.map((d) => ({ ...d, section: "Historical" })),
    ...projection.map((d) => ({ ...d, section: "Projection" })),
  ];

  return (
    <ResponsiveContainer width="100%" height={400}>
      <ComposedChart data={chartData} margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
        <XAxis
          dataKey="date"
          tick={{ fontSize: 12 }}
          className="text-muted-foreground"
          tickFormatter={(v: string) => {
            const [y, m] = v.split("-");
            const months = ["J","F","M","A","M","J","J","A","S","O","N","D"];
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
            const months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
            return `${months[parseInt(m) - 1]} ${y}`;
          }}
        />
        <Legend />
        <ReferenceLine
          x={historical[historical.length - 1]?.date}
          stroke="hsl(var(--muted-foreground))"
          strokeDasharray="4 4"
          label={{ value: "Forecast Start", position: "top", fontSize: 12 }}
        />
        <Area
          type="monotone"
          dataKey="forecastSales"
          fill="hsl(var(--chart-2))"
          fillOpacity={0.15}
          stroke="none"
          name="Forecast"
        />
        <Line
          type="monotone"
          dataKey="actualSales"
          stroke="hsl(var(--chart-1))"
          strokeWidth={2}
          dot={false}
          name="Historical Sales"
          connectNulls={false}
        />
        <Line
          type="monotone"
          dataKey="forecastSales"
          stroke="hsl(var(--chart-2))"
          strokeWidth={2}
          strokeDasharray="6 3"
          dot={false}
          name="Forecast"
          connectNulls={false}
        />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
