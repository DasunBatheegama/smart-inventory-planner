"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Target } from "lucide-react";
import { ForecastAccuracy as Accuracy } from "@/types/forecast";

interface ForecastAccuracyProps {
  data: Accuracy;
}

const statusConfig = {
  excellent: { label: "Excellent", color: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400" },
  good: { label: "Good", color: "bg-blue-500/10 text-blue-600 dark:text-blue-400" },
  fair: { label: "Fair", color: "bg-amber-500/10 text-amber-600 dark:text-amber-400" },
  poor: { label: "Poor", color: "bg-rose-500/10 text-rose-600 dark:text-rose-400" },
};

export function ForecastAccuracy({ data }: ForecastAccuracyProps) {
  const config = statusConfig[data.status];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5 text-primary" />
          Forecast Accuracy
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-sm text-muted-foreground">MAPE</p>
            <p className="text-xl font-bold">{data.mape}%</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-muted-foreground">MAE</p>
            <p className="text-xl font-bold">{data.mae}</p>
          </div>
          <div className="text-center">
            <p className="text-sm text-muted-foreground">Confidence</p>
            <p className="text-xl font-bold">{data.confidenceScore}%</p>
          </div>
        </div>

        <div className="flex items-center justify-between rounded-lg border p-3">
          <span className="text-sm text-muted-foreground">Accuracy Status</span>
          <Badge className={config.color} variant="outline">
            {config.label}
          </Badge>
        </div>
      </CardContent>
    </Card>
  );
}
