"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ShoppingCart } from "lucide-react";
import { PurchasePlan } from "@/types/inventory";

interface PurchasePlanningProps {
  data: PurchasePlan[];
}

export function PurchasePlanning({ data }: PurchasePlanningProps) {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ShoppingCart className="h-5 w-5 text-primary" />
          Purchase Planning
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {data.map((plan) => (
            <div key={plan.supplier} className="rounded-lg border p-3">
              <div className="flex items-center justify-between mb-2">
                <h4 className="text-sm font-semibold">{plan.supplier}</h4>
                <Badge variant="secondary" className="text-xs">
                  {plan.totalQuantity} units
                </Badge>
              </div>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Product</TableHead>
                    <TableHead className="text-right">Qty</TableHead>
                    <TableHead className="text-right">Cost</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {plan.items.map((item) => (
                    <TableRow key={item.sku}>
                      <TableCell className="text-sm">
                        {item.productName}
                      </TableCell>
                      <TableCell className="text-right text-sm">
                        {item.quantity.toLocaleString()}
                      </TableCell>
                      <TableCell className="text-right text-sm font-medium">
                        ${item.estimatedCost.toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
              <div className="flex justify-between pt-2 mt-2 border-t text-sm">
                <span className="text-muted-foreground">Total</span>
                <span className="font-semibold">
                  ${plan.totalCost.toLocaleString()}
                </span>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
