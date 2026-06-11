import * as React from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { forecastSummary } from "@/data/mock-dashboard";
import { TrendingUp } from "lucide-react";

export function ForecastSummary() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Forecast Summary</CardTitle>
        <CardDescription>Next 30 days projection</CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <p className="text-sm font-medium text-muted-foreground mb-1">Total Expected Demand</p>
          <p className="text-3xl font-bold">{forecastSummary.nextMonthDemand}</p>
        </div>
        
        <div className="space-y-3">
          <p className="text-sm font-medium">Top Growing Categories</p>
          {forecastSummary.topGrowing.map((item, i) => (
            <div key={i} className="flex items-center justify-between">
              <span className="text-sm text-muted-foreground">{item.name}</span>
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-emerald-500">{item.growth}</span>
                <TrendingUp className="h-4 w-4 text-emerald-500" />
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}