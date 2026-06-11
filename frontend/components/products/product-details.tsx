"use client";

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Separator } from "@/components/ui/separator";
import { Product } from "@/types/product";
import { StatusBadge } from "./status-badge";
import { Package, DollarSign, Clock, Truck, BarChart3, TrendingUp } from "lucide-react";

interface ProductDetailsProps {
  product: Product | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function ProductDetails({ product, open, onOpenChange }: ProductDetailsProps) {
  if (!product) return null;

  const value = product.currentStock * product.unitCost;

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-md overflow-y-auto">
        <SheetHeader className="mb-6">
          <div className="flex items-center justify-between mt-4">
            <SheetTitle className="text-2xl">{product.name}</SheetTitle>
            <StatusBadge status={product.status} />
          </div>
          <SheetDescription>SKU: {product.sku}</SheetDescription>
        </SheetHeader>

        <div className="space-y-6">
          {/* Inventory Metrics */}
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-4 uppercase tracking-wider">Inventory Metrics</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex flex-col space-y-1 bg-muted/50 p-3 rounded-md">
                <span className="text-xs text-muted-foreground flex items-center"><Package className="w-3 h-3 mr-1" /> Current Stock</span>
                <span className="text-xl font-bold">{product.currentStock}</span>
              </div>
              <div className="flex flex-col space-y-1 bg-muted/50 p-3 rounded-md">
                <span className="text-xs text-muted-foreground flex items-center"><BarChart3 className="w-3 h-3 mr-1" /> Reorder Point</span>
                <span className="text-xl font-bold">{product.reorderPoint}</span>
              </div>
              <div className="flex flex-col space-y-1 bg-muted/50 p-3 rounded-md">
                <span className="text-xs text-muted-foreground flex items-center"><AlertCircle className="w-3 h-3 mr-1" /> Safety Stock</span>
                <span className="text-xl font-bold">{product.safetyStock}</span>
              </div>
              <div className="flex flex-col space-y-1 bg-muted/50 p-3 rounded-md">
                <span className="text-xs text-muted-foreground flex items-center"><DollarSign className="w-3 h-3 mr-1" /> Total Value</span>
                <span className="text-xl font-bold">${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
              </div>
            </div>
          </div>

          <Separator />

          {/* Product Information */}
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-4 uppercase tracking-wider">Product Information</h3>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Category</span>
                <span className="text-sm font-medium">{product.category}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground">Unit Cost</span>
                <span className="text-sm font-medium">${product.unitCost.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground flex items-center"><Truck className="w-4 h-4 mr-2" /> Supplier</span>
                <span className="text-sm font-medium">{product.supplier}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-muted-foreground flex items-center"><Clock className="w-4 h-4 mr-2" /> Lead Time</span>
                <span className="text-sm font-medium">{product.leadTime} Days</span>
              </div>
            </div>
          </div>

          <Separator />

          {/* AI Forecast Placeholder */}
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-4 uppercase tracking-wider flex items-center">
              <TrendingUp className="w-4 h-4 mr-2 text-primary" /> Forecast Summary
            </h3>
            <div className="bg-primary/5 border border-primary/20 rounded-md p-4">
              <p className="text-sm text-muted-foreground leading-relaxed">
                Connect your data source to generate AI-driven inventory forecasts. InventIQ will predict demand trends, recommend reorder dates, and optimize safety stock dynamically.
              </p>
            </div>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}

// Quick fallback for icon not imported
function AlertCircle(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <circle cx="12" cy="12" r="10" />
      <line x1="12" y1="8" x2="12" y2="12" />
      <line x1="12" y1="16" x2="12.01" y2="16" />
    </svg>
  )
}
