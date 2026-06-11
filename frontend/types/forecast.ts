export interface ForecastData {
  date: string;
  actualSales: number;
  forecastSales: number;
}

export interface ForecastResult {
  month: string;
  forecastQuantity: number;
  confidence: number;
  method: string;
}

export interface GrowthProduct {
  product: string;
  currentDemand: number;
  forecastDemand: number;
  growth: number;
}

export interface RiskProduct {
  product: string;
  forecastDemand: number;
  currentInventory: number;
  riskLevel: "high" | "medium" | "low";
}

export interface ForecastAccuracy {
  mape: number;
  mae: number;
  confidenceScore: number;
  status: "excellent" | "good" | "fair" | "poor";
}

export interface ForecastSummary {
  currentMonthlyDemand: number;
  forecastedDemand: number;
  growth: number;
  trendDirection: "up" | "down" | "stable";
}

export interface ForecastControls {
  productId: string;
  category: string;
  horizon: number;
  method: "moving-average" | "exponential-smoothing";
}
