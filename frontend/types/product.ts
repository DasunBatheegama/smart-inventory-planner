export type ProductStatus = 'in-stock' | 'low-stock' | 'out-of-stock';

export interface Product {
  id: string;
  sku: string;
  name: string;
  category: string;
  currentStock: number;
  unitCost: number;
  leadTime: number; // in days
  supplier: string;
  reorderPoint: number;
  safetyStock: number;
  status: ProductStatus;
}
