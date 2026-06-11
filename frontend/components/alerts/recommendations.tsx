"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Recommendation } from "@/types/alert";
import { Lightbulb } from "lucide-react";

interface RecommendationsProps {
  data: Recommendation[];
}

export function Recommendations({ data }: RecommendationsProps) {
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
            key={r.id}
            className={cn(
              "rounded-lg border p-3 text-sm",
              r.severity === "critical"
                ? "border-rose-500/30 bg-rose-500/5"
                : "border-amber-500/20 bg-amber-500/5"
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
                  r.severity === "critical"
                    ? "bg-rose-500/10 text-rose-600 dark:text-rose-400"
                    : "bg-amber-500/10 text-amber-600 dark:text-amber-400"
                )}
              >
                {r.daysUntilAction}d
              </Badge>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
