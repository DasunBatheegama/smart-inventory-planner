export type AlertType =
  | "low-stock"
  | "stockout-risk"
  | "reorder-required"
  | "overstock"
  | "slow-moving"
  | "forecast-anomaly";

export type AlertSeverity = "critical" | "warning" | "info";

export type AlertStatus = "new" | "acknowledged" | "resolved";

export interface Alert {
  id: string;
  type: AlertType;
  severity: AlertSeverity;
  sku: string;
  productName: string;
  category: string;
  supplier: string;
  message: string;
  recommendation: string;
  status: AlertStatus;
  createdAt: string;
  daysRemaining?: number;
}

export interface AlertFilters {
  type: string;
  severity: string;
  product: string;
  supplier: string;
  dateRange: string;
  search: string;
}

export interface AlertMetrics {
  totalActive: number;
  criticalCount: number;
  reorderRequired: number;
  overstockWarnings: number;
}

export interface AlertCategoryData {
  name: string;
  value: number;
  color: string;
}

export interface Recommendation {
  id: string;
  sku: string;
  productName: string;
  action: string;
  daysUntilAction: number;
  severity: AlertSeverity;
}
