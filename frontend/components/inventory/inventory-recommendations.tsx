"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Recommendation } from "@/types/inventory";
import { Lightbulb } from "lucide-react";

interface InventoryRecommendationsProps {
  data: Recommendation[];
}

export function InventoryRecommendations({
  data,
}: InventoryRecommendationsProps) {
  const sorted = [...data].sort(
    (a, b) => a.daysUntilAction - b.daysUntilAction
  );

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Lightbulb className="h-5 w-5 text-amber-500" />
          Recommendations
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {sorted.map((r) => (
          <div
            key={r.sku}
            className={cn(
              "rounded-lg border p-3 text-sm",
              r.daysUntilAction <= 3
                ? "border-rose-500/30 bg-rose-500/5"
                : r.daysUntilAction <= 7
                  ? "border-amber-500/30 bg-amber-500/5"
                  : "border-border"
            )}
          >
            <div className="flex items-start justify-between gap-2">
              <div>
                <span className="font-medium">{r.productName}</span>
                <p className="text-muted-foreground mt-1">{r.action}</p>
              </div>
              <Badge
                variant="outline"
                className={cn(
                  "shrink-0",
                  r.daysUntilAction <= 3
                    ? "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                    : r.daysUntilAction <= 7
                      ? "bg-amber-500/10 text-amber-600 dark:text-amber-400"
                      : "text-muted-foreground"
                )}
              >
                {r.daysUntilAction === 30
                  ? `${r.daysUntilAction} days`
                  : `${r.daysUntilAction} day${r.daysUntilAction > 1 ? "s" : ""}`}
              </Badge>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
