"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import { RiskProduct } from "@/types/inventory";
import { AlertTriangle, PackageOpen, Clock } from "lucide-react";

interface InventoryRiskProps {
  stockout: RiskProduct[];
  overstock: RiskProduct[];
  slowMoving: RiskProduct[];
}

export function InventoryRisk({
  stockout,
  overstock,
  slowMoving,
}: InventoryRiskProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-rose-500" />
          Inventory Risk
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-5">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <PackageOpen className="h-4 w-4 text-rose-500" />
            <span className="text-sm font-medium">Stockout Risk</span>
            <Badge
              variant="outline"
              className="bg-rose-500/10 text-rose-600 dark:text-rose-400 ml-auto"
            >
              {stockout.length}
            </Badge>
          </div>
          {stockout.length === 0 ? (
            <p className="text-xs text-muted-foreground pl-6">None</p>
          ) : (
            <ul className="space-y-1">
              {stockout.map((p) => (
                <li
                  key={p.sku}
                  className="flex justify-between text-sm pl-6"
                >
                  <span>{p.product}</span>
                  <span className="text-muted-foreground">
                    {p.currentStock} units
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <PackageOpen className="h-4 w-4 text-blue-500" />
            <span className="text-sm font-medium">Overstocked</span>
            <Badge
              variant="outline"
              className="bg-blue-500/10 text-blue-600 dark:text-blue-400 ml-auto"
            >
              {overstock.length}
            </Badge>
          </div>
          {overstock.length === 0 ? (
            <p className="text-xs text-muted-foreground pl-6">None</p>
          ) : (
            <ul className="space-y-1">
              {overstock.map((p) => (
                <li
                  key={p.sku}
                  className="flex justify-between text-sm pl-6"
                >
                  <span>{p.product}</span>
                  <span className="text-muted-foreground">
                    {p.currentStock} units
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <div className="flex items-center gap-2 mb-2">
            <Clock className="h-4 w-4 text-amber-500" />
            <span className="text-sm font-medium">Slow Moving</span>
            <Badge
              variant="outline"
              className="bg-amber-500/10 text-amber-600 dark:text-amber-400 ml-auto"
            >
              {slowMoving.length}
            </Badge>
          </div>
          {slowMoving.length === 0 ? (
            <p className="text-xs text-muted-foreground pl-6">None</p>
          ) : (
            <ul className="space-y-1">
              {slowMoving.map((p) => (
                <li
                  key={p.sku}
                  className="flex justify-between text-sm pl-6"
                >
                  <span>{p.product}</span>
                  <span className="text-muted-foreground">
                    {p.currentStock} units
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
