export type InventoryStatus =
  | "healthy"
  | "reorder-soon"
  | "reorder-now"
  | "critical";

export type HealthStatus = "excellent" | "good" | "warning" | "critical";

export type RiskType = "stockout" | "overstock" | "slow-moving";

export interface InventoryPlanItem {
  sku: string;
  productName: string;
  category: string;
  supplier: string;
  currentStock: number;
  forecastDemand: number;
  safetyStock: number;
  reorderPoint: number;
  eoq: number;
  recommendedOrder: number;
  daysRemaining: number;
  status: InventoryStatus;
}

export interface InventoryMetrics {
  totalInventoryValue: number;
  productsRequiringReorder: number;
  healthScore: number;
  daysOfInventoryRemaining: number;
}

export interface InventoryHealth {
  score: number;
  status: HealthStatus;
  breakdown: {
    healthy: number;
    lowStock: number;
    overstock: number;
    slowMoving: number;
  };
}

export interface RiskProduct {
  product: string;
  sku: string;
  currentStock: number;
  forecastDemand: number;
  riskType: RiskType;
}

export interface Recommendation {
  sku: string;
  productName: string;
  action: string;
  quantity: number;
  daysUntilAction: number;
}

export interface PurchasePlanItem {
  supplier: string;
  productName: string;
  sku: string;
  quantity: number;
  unitCost: number;
  estimatedCost: number;
}

export interface PurchasePlan {
  supplier: string;
  items: PurchasePlanItem[];
  totalQuantity: number;
  totalCost: number;
}

export interface TrendDataPoint {
  month: string;
  inventoryLevel: number;
  forecastDemand: number;
  safetyStockThreshold: number;
}

export interface InventoryFilters {
  product: string;
  category: string;
  supplier: string;
  status: string;
}
