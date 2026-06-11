"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { InventoryHealth as Health } from "@/types/inventory";
import { HeartPulse } from "lucide-react";

interface InventoryHealthProps {
  data: Health;
}

const statusConfig = {
  excellent: {
    label: "Excellent",
    className:
      "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/20",
  },
  good: {
    label: "Good",
    className:
      "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
  },
  warning: {
    label: "Warning",
    className:
      "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
  },
  critical: {
    label: "Critical",
    className:
      "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20",
  },
};

export function InventoryHealth({ data }: InventoryHealthProps) {
  const config = statusConfig[data.status];
  const radius = 56;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (circumference * data.score) / 100;

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <HeartPulse className="h-5 w-5 text-primary" />
          Inventory Health
        </CardTitle>
      </CardHeader>
      <CardContent className="flex flex-col items-center space-y-4">
        <div className="relative flex items-center justify-center">
          <svg width="140" height="140" className="-rotate-90">
            <circle
              cx="70"
              cy="70"
              r={radius}
              fill="none"
              stroke="hsl(var(--muted))"
              strokeWidth="10"
            />
            <circle
              cx="70"
              cy="70"
              r={radius}
              fill="none"
              stroke="currentColor"
              strokeWidth="10"
              strokeLinecap="round"
              strokeDasharray={circumference}
              strokeDashoffset={offset}
              className={
                data.score >= 80
                  ? "text-emerald-500"
                  : data.score >= 60
                    ? "text-blue-500"
                    : data.score >= 40
                      ? "text-amber-500"
                      : "text-rose-500"
              }
            />
          </svg>
          <span className="absolute text-3xl font-bold">{data.score}</span>
        </div>

        <Badge className={cn("px-3 py-1", config.className)} variant="outline">
          {config.label}
        </Badge>

        <div className="w-full space-y-2">
          {[
            { label: "Healthy", value: data.breakdown.healthy, color: "bg-emerald-500" },
            { label: "Low Stock", value: data.breakdown.lowStock, color: "bg-amber-500" },
            { label: "Overstock", value: data.breakdown.overstock, color: "bg-blue-500" },
            { label: "Slow Moving", value: data.breakdown.slowMoving, color: "bg-rose-500" },
          ].map((item) => (
            <div key={item.label} className="flex items-center gap-2 text-sm">
              <span className={cn("h-2.5 w-2.5 rounded-full shrink-0", item.color)} />
              <span className="flex-1 text-muted-foreground">{item.label}</span>
              <span className="font-medium">{item.value}%</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
