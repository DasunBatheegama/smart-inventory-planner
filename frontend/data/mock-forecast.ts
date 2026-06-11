import {
  ForecastData,
  ForecastResult,
  GrowthProduct,
  RiskProduct,
  ForecastAccuracy,
  ForecastSummary,
} from "@/types/forecast";

export const mockProducts = [
  { id: "prod-1", name: "Wireless Headphones", category: "Electronics" },
  { id: "prod-2", name: "Ergonomic Chair", category: "Furniture" },
  { id: "prod-3", name: "Mechanical Keyboard", category: "Electronics" },
  { id: "prod-4", name: "Standing Desk", category: "Furniture" },
  { id: "prod-5", name: "USB-C Hub", category: "Accessories" },
  { id: "prod-6", name: "Monitor Arm", category: "Accessories" },
  { id: "prod-7", name: "Noise Cancelling Earbuds", category: "Electronics" },
  { id: "prod-8", name: "Desk Lamp", category: "Furniture" },
  { id: "prod-9", name: "Laptop Stand", category: "Accessories" },
  { id: "prod-10", name: "Webcam 4K", category: "Electronics" },
];

export const mockCategories = ["Electronics", "Furniture", "Accessories"];

export const mockForecastData: ForecastData[] = [
  { date: "2024-01", actualSales: 1200, forecastSales: 1180 },
  { date: "2024-02", actualSales: 1350, forecastSales: 1300 },
  { date: "2024-03", actualSales: 1100, forecastSales: 1120 },
  { date: "2024-04", actualSales: 1450, forecastSales: 1400 },
  { date: "2024-05", actualSales: 1600, forecastSales: 1550 },
  { date: "2024-06", actualSales: 1550, forecastSales: 1580 },
  { date: "2024-07", actualSales: 1700, forecastSales: 1650 },
  { date: "2024-08", actualSales: 1800, forecastSales: 1750 },
  { date: "2024-09", actualSales: 1650, forecastSales: 1680 },
  { date: "2024-10", actualSales: 1900, forecastSales: 1850 },
  { date: "2024-11", actualSales: 2100, forecastSales: 2050 },
  { date: "2024-12", actualSales: 2400, forecastSales: 2350 },
  { date: "2025-01", actualSales: 2000, forecastSales: 2100 },
  { date: "2025-02", actualSales: 1950, forecastSales: 2000 },
  { date: "2025-03", actualSales: 2200, forecastSales: 2150 },
  { date: "2025-04", actualSales: 2350, forecastSales: 2300 },
  { date: "2025-05", actualSales: 2500, forecastSales: 2450 },
  { date: "2025-06", actualSales: 2400, forecastSales: 2480 },
  { date: "2025-07", actualSales: 2600, forecastSales: 2550 },
  { date: "2025-08", actualSales: 2750, forecastSales: 2700 },
  { date: "2025-09", actualSales: 2600, forecastSales: 2650 },
  { date: "2025-10", actualSales: 2900, forecastSales: 2850 },
  { date: "2025-11", actualSales: 3100, forecastSales: 3050 },
  { date: "2025-12", actualSales: 3400, forecastSales: 3350 },
];

export const mockForecastProjection: ForecastData[] = [
  { date: "2026-01", actualSales: 0, forecastSales: 3200 },
  { date: "2026-02", actualSales: 0, forecastSales: 3150 },
  { date: "2026-03", actualSales: 0, forecastSales: 3300 },
  { date: "2026-04", actualSales: 0, forecastSales: 3450 },
  { date: "2026-05", actualSales: 0, forecastSales: 3600 },
  { date: "2026-06", actualSales: 0, forecastSales: 3550 },
];

export const mockForecastResults: ForecastResult[] = [
  { month: "Jan 2026", forecastQuantity: 3200, confidence: 92, method: "Exponential Smoothing" },
  { month: "Feb 2026", forecastQuantity: 3150, confidence: 90, method: "Exponential Smoothing" },
  { month: "Mar 2026", forecastQuantity: 3300, confidence: 88, method: "Exponential Smoothing" },
  { month: "Apr 2026", forecastQuantity: 3450, confidence: 85, method: "Exponential Smoothing" },
  { month: "May 2026", forecastQuantity: 3600, confidence: 82, method: "Exponential Smoothing" },
  { month: "Jun 2026", forecastQuantity: 3550, confidence: 80, method: "Exponential Smoothing" },
  { month: "Jul 2026", forecastQuantity: 3700, confidence: 78, method: "Exponential Smoothing" },
  { month: "Aug 2026", forecastQuantity: 3850, confidence: 75, method: "Exponential Smoothing" },
  { month: "Sep 2026", forecastQuantity: 3750, confidence: 73, method: "Exponential Smoothing" },
  { month: "Oct 2026", forecastQuantity: 3900, confidence: 70, method: "Exponential Smoothing" },
  { month: "Nov 2026", forecastQuantity: 4050, confidence: 68, method: "Exponential Smoothing" },
  { month: "Dec 2026", forecastQuantity: 4200, confidence: 65, method: "Exponential Smoothing" },
];

export const mockGrowthProducts: GrowthProduct[] = [
  { product: "Noise Cancelling Earbuds", currentDemand: 850, forecastDemand: 1450, growth: 70.6 },
  { product: "Wireless Headphones", currentDemand: 1200, forecastDemand: 1850, growth: 54.2 },
  { product: "Webcam 4K", currentDemand: 620, forecastDemand: 950, growth: 53.2 },
  { product: "Mechanical Keyboard", currentDemand: 1100, forecastDemand: 1550, growth: 40.9 },
  { product: "Ergonomic Chair", currentDemand: 780, forecastDemand: 1050, growth: 34.6 },
];

export const mockRiskProducts: RiskProduct[] = [
  { product: "Desk Lamp", forecastDemand: 1200, currentInventory: 320, riskLevel: "high" },
  { product: "Standing Desk", forecastDemand: 950, currentInventory: 410, riskLevel: "high" },
  { product: "Monitor Arm", forecastDemand: 1800, currentInventory: 890, riskLevel: "medium" },
  { product: "USB-C Hub", forecastDemand: 2200, currentInventory: 1350, riskLevel: "medium" },
  { product: "Laptop Stand", forecastDemand: 1500, currentInventory: 1100, riskLevel: "low" },
];

export const mockForecastAccuracy: ForecastAccuracy = {
  mape: 7.2,
  mae: 142,
  confidenceScore: 88,
  status: "good",
};

export const mockForecastSummary: ForecastSummary = {
  currentMonthlyDemand: 2900,
  forecastedDemand: 3200,
  growth: 10.3,
  trendDirection: "up",
};
