import * as React from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MoveUpRight, MoveDownRight } from "lucide-react";
import { cn } from "@/lib/utils";

interface StatCardProps {
  title: string;
  value: string;
  trend: string;
  trendUp: boolean;
  icon: React.ElementType;
}

export function StatCard({ title, value, trend, trendUp, icon: Icon }: StatCardProps) {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className="flex items-center text-xs text-muted-foreground mt-1 gap-1">
          <span className={cn("flex items-center", trendUp ? "text-emerald-500" : "text-rose-500")}>
            {trendUp ? <MoveUpRight className="h-3 w-3 mr-1" /> : <MoveDownRight className="h-3 w-3 mr-1" />}
            {trend}
          </span>
          <span className="text-muted-foreground ml-1">from last month</span>
        </p>
      </CardContent>
    </Card>
  );
}