"use client";

import { CalendarDays, Package, AlertTriangle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { ForecastReadiness } from "@/types/sales";
import { cn } from "@/lib/utils";

interface ForecastReadinessProps {
  data: ForecastReadiness;
}

export function ForecastReadinessWidget({ data }: ForecastReadinessProps) {
  const scoreColor =
    data.score >= 80
      ? "text-emerald-500"
      : data.score >= 50
      ? "text-amber-500"
      : "text-rose-500";

  return (
    <Card>
      <CardHeader>
        <CardTitle>Forecast Readiness</CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="flex items-center gap-3">
            <CalendarDays className="h-8 w-8 text-primary" />
            <div>
              <p className="text-2xl font-bold">{data.daysAvailable}</p>
              <p className="text-xs text-muted-foreground">Days Available</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Package className="h-8 w-8 text-primary" />
            <div>
              <p className="text-2xl font-bold">{data.productsCovered}</p>
              <p className="text-xs text-muted-foreground">Products Covered</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-8 w-8 text-amber-500" />
            <div>
              <p className="text-2xl font-bold">{data.missingDataWarnings}</p>
              <p className="text-xs text-muted-foreground">Missing Data</p>
            </div>
          </div>
        </div>

        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Readiness Score</span>
            <span className={cn("text-lg font-bold", scoreColor)}>
              {data.score}%
            </span>
          </div>
          <Progress value={data.score} className="h-2.5" />
        </div>

        {data.recommendations.length > 0 && (
          <div className="rounded-lg bg-muted p-3">
            <p className="text-xs font-medium text-muted-foreground mb-1">
              Recommendations
            </p>
            <ul className="space-y-1">
              {data.recommendations.map((rec, i) => (
                <li key={i} className="text-xs text-muted-foreground flex items-start gap-1.5">
                  <span className="mt-0.5 block h-1 w-1 rounded-full bg-primary shrink-0" />
                  {rec}
                </li>
              ))}
            </ul>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
