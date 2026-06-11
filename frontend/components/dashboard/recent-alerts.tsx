import * as React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { recentAlerts } from "@/data/mock-dashboard";
import { AlertCircle, AlertTriangle, Info } from "lucide-react";

const getAlertIcon = (type: string) => {
  switch (type) {
    case 'stockout':
      return <AlertCircle className="h-4 w-4 text-rose-500" />;
    case 'low_stock':
      return <AlertTriangle className="h-4 w-4 text-amber-500" />;
    case 'overstock':
      return <Info className="h-4 w-4 text-blue-500" />;
    default:
      return <Info className="h-4 w-4 text-muted-foreground" />;
  }
};

const getAlertBadgeVariant = (type: string): "destructive" | "default" | "secondary" => {
  switch (type) {
    case 'stockout':
      return "destructive";
    case 'low_stock':
      return "default"; // or implement warning variant
    case 'overstock':
      return "secondary";
    default:
      return "secondary";
  }
};

export function RecentAlerts() {
  return (
    <Card className="col-span-2">
      <CardHeader>
        <CardTitle>Needs Attention</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recentAlerts.map((alert) => (
            <div key={alert.id} className="flex items-start justify-between border-b pb-4 last:border-0 last:pb-0">
              <div className="flex items-start gap-4">
                <div className="rounded-full bg-muted p-2 mt-0.5">
                  {getAlertIcon(alert.type)}
                </div>
                <div className="space-y-1">
                  <p className="text-sm font-medium leading-none">{alert.title}</p>
                  <p className="text-sm text-muted-foreground">{alert.description}</p>
                </div>
              </div>
              <div className="flex flex-col items-end gap-2 shrink-0">
                <Badge variant={getAlertBadgeVariant(alert.type)} className="uppercase text-[10px]">
                  {alert.type.replace('_', ' ')}
                </Badge>
                <p className="text-xs text-muted-foreground">{alert.time}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}