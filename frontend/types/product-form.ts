import { z } from "zod";

export const productFormSchema = z.object({
  sku: z.string().min(1, "SKU is required"),
  name: z.string().min(1, "Product name is required"),
  category: z.string().min(1, "Category is required"),
  currentStock: z.coerce.number().min(0, "Stock cannot be negative"),
  unitCost: z.coerce.number().min(0, "Cost cannot be negative"),
  leadTime: z.coerce.number().min(0, "Lead time cannot be negative"),
  supplier: z.string().min(1, "Supplier is required"),
  reorderPoint: z.coerce.number().min(0, "Reorder point cannot be negative"),
  safetyStock: z.coerce.number().min(0, "Safety stock cannot be negative"),
});

export type ProductFormValues = z.infer<typeof productFormSchema>;
