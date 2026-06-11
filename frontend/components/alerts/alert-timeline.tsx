"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import { Alert } from "@/types/alert";
import {
  PackageX,
  AlertCircle,
  ShoppingCart,
  Layers,
  Clock,
  TrendingDown,
  History,
} from "lucide-react";

interface AlertTimelineProps {
  alerts: Alert[];
}

const typeIcons = {
  "low-stock": PackageX,
  "stockout-risk": AlertCircle,
  "reorder-required": ShoppingCart,
  overstock: Layers,
  "slow-moving": Clock,
  "forecast-anomaly": TrendingDown,
};

const severityDot = {
  critical: "bg-rose-500",
  warning: "bg-amber-500",
  info: "bg-blue-500",
};

export function AlertTimeline({ alerts }: AlertTimelineProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <History className="h-5 w-5 text-primary" />
          Alert Timeline
        </CardTitle>
      </CardHeader>
      <CardContent className="max-h-[320px] overflow-y-auto space-y-0">
        {alerts.map((alert, i) => {
          const Icon = typeIcons[alert.type];
          const timeAgo = getTimeAgo(alert.createdAt);
          return (
            <div key={alert.id}>
              <div className="flex gap-3 py-3">
                <div className="flex flex-col items-center">
                  <span
                    className={cn(
                      "h-2.5 w-2.5 rounded-full mt-1.5 shrink-0",
                      severityDot[alert.severity]
                    )}
                  />
                  {i < alerts.length - 1 && (
                    <div className="w-px flex-1 bg-border mt-1" />
                  )}
                </div>
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <Icon className="h-3.5 w-3.5 text-muted-foreground shrink-0" />
                    <span className="text-sm font-medium">
                      {alert.productName}
                    </span>
                    <span className="text-xs text-muted-foreground ml-auto shrink-0">
                      {timeAgo}
                    </span>
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5 line-clamp-1">
                    {alert.message}
                  </p>
                </div>
              </div>
              {i < alerts.length - 1 && <Separator />}
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
}

function getTimeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const hours = Math.floor(diff / (1000 * 60 * 60));
  if (hours < 1) return "Just now";
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  if (days === 1) return "1d ago";
  return `${days}d ago`;
}
