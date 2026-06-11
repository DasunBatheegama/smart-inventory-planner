import * as React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { inventoryHealth } from "@/data/mock-dashboard";

export function InventoryHealth() {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Inventory Health</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className="flex h-32 w-32 items-center justify-center rounded-full border-8 border-primary/20 relative">
            <span className="text-3xl font-bold">{inventoryHealth.score}</span>
            <svg className="absolute inset-0 h-full w-full -rotate-90 transform" viewBox="0 0 100 100">
              <circle
                cx="50"
                cy="50"
                r="46"
                fill="none"
                stroke="currentColor"
                strokeWidth="8"
                strokeDasharray="289"
                strokeDashoffset={289 - (289 * inventoryHealth.score) / 100}
                className="text-primary"
              />
            </svg>
          </div>
          
          <div className="w-full space-y-2 mt-4">
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
                Healthy
              </span>
              <span className="font-medium">{inventoryHealth.categories.healthy}%</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-amber-500"></span>
                Low Stock
              </span>
              <span className="font-medium">{inventoryHealth.categories.lowStock}%</span>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="flex items-center gap-2">
                <span className="h-2 w-2 rounded-full bg-rose-500"></span>
                Overstock
              </span>
              <span className="font-medium">{inventoryHealth.categories.overstock}%</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}