"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Database, CheckCircle2, XCircle } from "lucide-react";

interface ContextItem {
  name: string;
  connected: boolean;
}

const contextItems: ContextItem[] = [
  { name: "Products", connected: true },
  { name: "Sales Data", connected: true },
  { name: "Forecasting Results", connected: true },
  { name: "Planning Results", connected: true },
  { name: "Alerts", connected: true },
];

export function InventoryContext() {
  return (
    <Card>
      <CardHeader className="p-4 pb-2">
        <CardTitle className="text-sm font-medium flex items-center gap-2">
          <Database className="h-4 w-4 text-primary" />
          Inventory Context
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 pt-2 space-y-2">
        {contextItems.map((item) => (
          <div key={item.name} className="flex items-center justify-between">
            <span className="text-xs text-muted-foreground">{item.name}</span>
            <Badge
              variant="outline"
              className={cn(
                "text-xs gap-1",
                item.connected
                  ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                  : "bg-rose-500/10 text-rose-600 dark:text-rose-400"
              )}
            >
              {item.connected ? (
                <CheckCircle2 className="h-3 w-3" />
              ) : (
                <XCircle className="h-3 w-3" />
              )}
              {item.connected ? "Connected" : "Not Connected"}
            </Badge>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
