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
import { AlertTriangle } from "lucide-react";
import { RiskProduct } from "@/types/forecast";
import { cn } from "@/lib/utils";

interface RiskProductsProps {
  data: RiskProduct[];
}

const riskConfig = {
  high: { label: "High", className: "bg-rose-500/10 text-rose-600 dark:text-rose-400" },
  medium: { label: "Medium", className: "bg-amber-500/10 text-amber-600 dark:text-amber-400" },
  low: { label: "Low", className: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400" },
};

export function RiskProducts({ data }: RiskProductsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-rose-500" />
          Top Risk Products
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Product</TableHead>
              <TableHead className="text-right">Forecast Demand</TableHead>
              <TableHead className="text-right">Current Inventory</TableHead>
              <TableHead className="text-right">Risk</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((item) => {
              const config = riskConfig[item.riskLevel];
              return (
                <TableRow key={item.product}>
                  <TableCell className="font-medium">{item.product}</TableCell>
                  <TableCell className="text-right">{item.forecastDemand.toLocaleString()}</TableCell>
                  <TableCell className="text-right">{item.currentInventory.toLocaleString()}</TableCell>
                  <TableCell className="text-right">
                    <Badge className={cn(config.className)} variant="outline">
                      {config.label}
                    </Badge>
                  </TableCell>
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
