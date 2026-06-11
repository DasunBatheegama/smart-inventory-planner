"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { ProductFormValues, productFormSchema } from "@/types/product-form";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";

interface ProductFormProps {
  initialValues?: Partial<ProductFormValues>;
  onSubmit: (data: ProductFormValues) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function ProductForm({ initialValues, onSubmit, onCancel, isLoading }: ProductFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProductFormValues>({
    resolver: zodResolver(productFormSchema),
    defaultValues: {
      sku: initialValues?.sku || "",
      name: initialValues?.name || "",
      category: initialValues?.category || "",
      currentStock: initialValues?.currentStock || 0,
      unitCost: initialValues?.unitCost || 0,
      leadTime: initialValues?.leadTime || 0,
      supplier: initialValues?.supplier || "",
      reorderPoint: initialValues?.reorderPoint || 0,
      safetyStock: initialValues?.safetyStock || 0,
    },
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="sku">SKU</Label>
          <Input id="sku" {...register("sku")} placeholder="e.g. SKU-1234" />
          {errors.sku && <p className="text-sm text-red-500">{errors.sku.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="name">Product Name</Label>
          <Input id="name" {...register("name")} placeholder="e.g. Wireless Mouse" />
          {errors.name && <p className="text-sm text-red-500">{errors.name.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="category">Category</Label>
          <Input id="category" {...register("category")} placeholder="e.g. Electronics" />
          {errors.category && <p className="text-sm text-red-500">{errors.category.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="supplier">Supplier</Label>
          <Input id="supplier" {...register("supplier")} placeholder="e.g. Acme Corp" />
          {errors.supplier && <p className="text-sm text-red-500">{errors.supplier.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="currentStock">Current Stock</Label>
          <Input id="currentStock" type="number" {...register("currentStock")} />
          {errors.currentStock && <p className="text-sm text-red-500">{errors.currentStock.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="unitCost">Unit Cost ($)</Label>
          <Input id="unitCost" type="number" step="0.01" {...register("unitCost")} />
          {errors.unitCost && <p className="text-sm text-red-500">{errors.unitCost.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="leadTime">Lead Time (Days)</Label>
          <Input id="leadTime" type="number" {...register("leadTime")} />
          {errors.leadTime && <p className="text-sm text-red-500">{errors.leadTime.message}</p>}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="reorderPoint">Reorder Point</Label>
          <Input id="reorderPoint" type="number" {...register("reorderPoint")} />
          {errors.reorderPoint && <p className="text-sm text-red-500">{errors.reorderPoint.message}</p>}
        </div>

        <div className="space-y-2">
          <Label htmlFor="safetyStock">Safety Stock</Label>
          <Input id="safetyStock" type="number" {...register("safetyStock")} />
          {errors.safetyStock && <p className="text-sm text-red-500">{errors.safetyStock.message}</p>}
        </div>
      </div>

      <div className="flex justify-end space-x-2 pt-4">
        <Button type="button" variant="outline" onClick={onCancel}>
          Cancel
        </Button>
        <Button type="submit" disabled={isLoading}>
          {isLoading ? "Saving..." : "Save Product"}
        </Button>
      </div>
    </form>
  );
}
