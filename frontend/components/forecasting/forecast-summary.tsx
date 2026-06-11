"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, ArrowUp, ArrowDown, Minus } from "lucide-react";
import { cn } from "@/lib/utils";
import { ForecastSummary as Summary } from "@/types/forecast";

interface ForecastSummaryProps {
  data: Summary;
}

export function ForecastSummary({ data }: ForecastSummaryProps) {
  const TrendIcon =
    data.trendDirection === "up"
      ? ArrowUp
      : data.trendDirection === "down"
        ? ArrowDown
        : Minus;

  const trendColor =
    data.trendDirection === "up"
      ? "text-emerald-500"
      : data.trendDirection === "down"
        ? "text-rose-500"
        : "text-muted-foreground";

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-primary" />
          Forecast Summary
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-muted-foreground">Current Monthly Demand</p>
            <p className="text-2xl font-bold">{data.currentMonthlyDemand.toLocaleString()}</p>
          </div>
          <div>
            <p className="text-sm text-muted-foreground">Forecasted Demand</p>
            <p className="text-2xl font-bold">{data.forecastedDemand.toLocaleString()}</p>
          </div>
        </div>

        <div className="flex items-center justify-between rounded-lg border p-4">
          <div>
            <p className="text-sm text-muted-foreground">Growth</p>
            <p className="text-xl font-bold">{data.growth}%</p>
          </div>
          <div className="flex items-center gap-2">
            <TrendIcon className={cn("h-5 w-5", trendColor)} />
            <span className={cn("text-sm font-medium capitalize", trendColor)}>
              {data.trendDirection}
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
