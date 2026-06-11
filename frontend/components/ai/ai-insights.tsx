"use client";

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  Package,
  DollarSign,
  AlertTriangle,
  ShoppingCart,
  Lightbulb,
} from "lucide-react";
import { InventorySummary, AiRecommendation } from "@/types/chat";

interface AiInsightsProps {
  summary: InventorySummary | null;
  recommendations: AiRecommendation[];
}

export function AiInsights({ summary, recommendations }: AiInsightsProps) {
  return (
    <div className="space-y-4">
      <Card>
        <CardHeader className="p-4 pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Package className="h-4 w-4 text-primary" />
            Inventory Summary
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 pt-2 space-y-3">
          {summary && (
            <>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Package className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Total Products</span>
                </div>
                <span className="text-sm font-semibold">{summary.totalProducts}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <DollarSign className="h-4 w-4 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">Inventory Value</span>
                </div>
                <span className="text-sm font-semibold">
                  ${summary.inventoryValue.toLocaleString()}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-rose-500" />
                  <span className="text-xs text-muted-foreground">Active Alerts</span>
                </div>
                <span className="text-sm font-semibold">{summary.activeAlerts}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <ShoppingCart className="h-4 w-4 text-amber-500" />
                  <span className="text-xs text-muted-foreground">Reorder Required</span>
                </div>
                <span className="text-sm font-semibold">{summary.reorderRequired}</span>
              </div>
            </>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="p-4 pb-2">
          <CardTitle className="text-sm font-medium flex items-center gap-2">
            <Lightbulb className="h-4 w-4 text-amber-500" />
            Recent AI Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent className="p-4 pt-2 space-y-2">
          {recommendations.map((r) => (
            <div
              key={r.id}
              className="rounded-lg border p-2.5 text-xs"
            >
              <div className="flex items-start justify-between gap-2">
                <div className="min-w-0">
                  <span className="font-medium">{r.productName}</span>
                  <p className="text-muted-foreground mt-0.5">{r.action}</p>
                </div>
                <Badge
                  variant="outline"
                  className={cn(
                    "shrink-0 text-xs",
                    r.daysUntilAction <= 3
                      ? "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                      : r.daysUntilAction <= 7
                        ? "bg-amber-500/10 text-amber-600 dark:text-amber-400"
                        : "text-muted-foreground"
                  )}
                >
                  {r.daysUntilAction}d
                </Badge>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
