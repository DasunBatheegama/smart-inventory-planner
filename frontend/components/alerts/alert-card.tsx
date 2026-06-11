"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { Alert } from "@/types/alert";
import {
  PackageX,
  AlertCircle,
  ShoppingCart,
  Layers,
  Clock,
  TrendingDown,
  CheckCircle2,
  Eye,
  CheckCheck,
} from "lucide-react";

interface AlertCardProps {
  alert: Alert;
  onMarkRead: (id: string) => void;
  onResolve: (id: string) => void;
}

const typeConfig = {
  "low-stock": { icon: PackageX, label: "Low Stock" },
  "stockout-risk": { icon: AlertCircle, label: "Stockout Risk" },
  "reorder-required": { icon: ShoppingCart, label: "Reorder Required" },
  overstock: { icon: Layers, label: "Overstock" },
  "slow-moving": { icon: Clock, label: "Slow Moving" },
  "forecast-anomaly": { icon: TrendingDown, label: "Forecast Anomaly" },
};

const severityConfig = {
  critical: "bg-rose-500/10 text-rose-600 dark:text-rose-400 border-rose-500/20",
  warning: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/20",
  info: "bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-500/20",
};

const statusConfig = {
  new: "bg-primary/10 text-primary border-primary/20",
  acknowledged: "bg-muted text-muted-foreground border-border",
  resolved: "bg-muted/50 text-muted-foreground border-border/50",
};

export function AlertCard({ alert, onMarkRead, onResolve }: AlertCardProps) {
  const typeInfo = typeConfig[alert.type];
  const Icon = typeInfo.icon;
  const daysSince = Math.floor(
    (Date.now() - new Date(alert.createdAt).getTime()) / (1000 * 60 * 60 * 24)
  );

  return (
    <Card
      className={cn(
        "border-l-4",
        alert.severity === "critical"
          ? "border-l-rose-500"
          : alert.severity === "warning"
            ? "border-l-amber-500"
            : "border-l-blue-500"
      )}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 min-w-0">
            <Icon className="h-5 w-5 mt-0.5 shrink-0 text-muted-foreground" />
            <div className="min-w-0">
              <div className="flex flex-wrap items-center gap-2 mb-1">
                <Badge
                  variant="outline"
                  className={cn("text-xs", severityConfig[alert.severity])}
                >
                  {alert.severity.charAt(0).toUpperCase() +
                    alert.severity.slice(1)}
                </Badge>
                <Badge
                  variant="outline"
                  className={cn("text-xs", statusConfig[alert.status])}
                >
                  {alert.status.charAt(0).toUpperCase() +
                    alert.status.slice(1)}
                </Badge>
                <span className="text-xs text-muted-foreground">
                  {daysSince === 0 ? "Today" : `${daysSince}d ago`}
                </span>
              </div>
              <h4 className="font-semibold text-sm">
                {alert.productName}{" "}
                <span className="font-normal text-muted-foreground">
                  ({alert.sku})
                </span>
              </h4>
              <p className="text-sm text-muted-foreground mt-1">
                {alert.message}
              </p>
              <p className="text-sm mt-2 flex items-start gap-2">
                <span className="font-medium shrink-0">Action:</span>
                <span>{alert.recommendation}</span>
              </p>
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 mt-3 pt-3 border-t">
          {alert.status === "new" && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onMarkRead(alert.id)}
            >
              <CheckCheck className="mr-1.5 h-3.5 w-3.5" />
              Mark Read
            </Button>
          )}
          {alert.status !== "resolved" && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => onResolve(alert.id)}
            >
              <CheckCircle2 className="mr-1.5 h-3.5 w-3.5" />
              Resolve
            </Button>
          )}
          <Button variant="ghost" size="sm" className="ml-auto">
            <Eye className="mr-1.5 h-3.5 w-3.5" />
            View Details
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
