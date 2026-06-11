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
import { TrendingUp } from "lucide-react";
import { GrowthProduct } from "@/types/forecast";
import { cn } from "@/lib/utils";

interface GrowthProductsProps {
  data: GrowthProduct[];
}

export function GrowthProducts({ data }: GrowthProductsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-emerald-500" />
          Top Growth Products
        </CardTitle>
      </CardHeader>
      <CardContent>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Product</TableHead>
              <TableHead className="text-right">Current</TableHead>
              <TableHead className="text-right">Forecast</TableHead>
              <TableHead className="text-right">Growth</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {data.map((item) => (
              <TableRow key={item.product}>
                <TableCell className="font-medium">{item.product}</TableCell>
                <TableCell className="text-right">{item.currentDemand.toLocaleString()}</TableCell>
                <TableCell className="text-right">{item.forecastDemand.toLocaleString()}</TableCell>
                <TableCell className="text-right">
                  <span className={cn(
                    "font-medium",
                    item.growth > 50 ? "text-emerald-500" : "text-blue-500"
                  )}>
                    +{item.growth}%
                  </span>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </CardContent>
    </Card>
  );
}
