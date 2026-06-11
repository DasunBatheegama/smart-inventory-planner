"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { Alert } from "@/types/alert";
import { AlertTriangle } from "lucide-react";

interface CriticalAlertsProps {
  alerts: Alert[];
}

export function CriticalAlerts({ alerts }: CriticalAlertsProps) {
  const critical = alerts
    .filter((a) => a.severity === "critical" && a.status !== "resolved")
    .slice(0, 5);

  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-rose-500" />
          Critical Alerts
        </CardTitle>
      </CardHeader>
      <CardContent>
        {critical.length === 0 ? (
          <p className="text-sm text-muted-foreground text-center py-8">
            No critical alerts
          </p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Product</TableHead>
                <TableHead className="text-right">Days Remaining</TableHead>
                <TableHead className="text-right">Severity</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {critical.map((a) => (
                <TableRow key={a.id}>
                  <TableCell>
                    <div className="text-sm font-medium">{a.productName}</div>
                    <div className="text-xs text-muted-foreground">{a.sku}</div>
                  </TableCell>
                  <TableCell className="text-right">
                    {a.daysRemaining != null ? (
                      <span
                        className={cn(
                          "font-semibold",
                          a.daysRemaining <= 10
                            ? "text-rose-500"
                            : "text-amber-500"
                        )}
                      >
                        {a.daysRemaining}d
                      </span>
                    ) : (
                      <span className="text-muted-foreground">—</span>
                    )}
                  </TableCell>
                  <TableCell className="text-right">
                    <Badge
                      variant="outline"
                      className="bg-rose-500/10 text-rose-600 dark:text-rose-400"
                    >
                      Critical
                    </Badge>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
