import {
  InventoryPlanItem,
  InventoryMetrics,
  InventoryHealth,
  RiskProduct,
  Recommendation,
  PurchasePlan,
  TrendDataPoint,
} from "@/types/inventory";

export const mockInventoryPlan: InventoryPlanItem[] = [
  { sku: "SKU-1001", productName: "Wireless Headphones", category: "Electronics", supplier: "TechSupply Co.", currentStock: 1200, forecastDemand: 1850, safetyStock: 278, reorderPoint: 555, eoq: 620, recommendedOrder: 650, daysRemaining: 19, status: "reorder-soon" },
  { sku: "SKU-1002", productName: "Ergonomic Chair", category: "Furniture", supplier: "OfficePro Ltd.", currentStock: 410, forecastDemand: 1050, safetyStock: 158, reorderPoint: 315, eoq: 430, recommendedOrder: 640, daysRemaining: 12, status: "reorder-now" },
  { sku: "SKU-1003", productName: "Mechanical Keyboard", category: "Electronics", supplier: "TechSupply Co.", currentStock: 2100, forecastDemand: 1550, safetyStock: 233, reorderPoint: 465, eoq: 560, recommendedOrder: 0, daysRemaining: 41, status: "healthy" },
  { sku: "SKU-1004", productName: "Standing Desk", category: "Furniture", supplier: "OfficePro Ltd.", currentStock: 320, forecastDemand: 950, safetyStock: 143, reorderPoint: 285, eoq: 390, recommendedOrder: 630, daysRemaining: 10, status: "critical" },
  { sku: "SKU-1005", productName: "USB-C Hub", category: "Accessories", supplier: "ConnectWorld Inc.", currentStock: 1350, forecastDemand: 2200, safetyStock: 330, reorderPoint: 660, eoq: 740, recommendedOrder: 850, daysRemaining: 18, status: "reorder-soon" },
  { sku: "SKU-1006", productName: "Monitor Arm", category: "Accessories", supplier: "ConnectWorld Inc.", currentStock: 890, forecastDemand: 1800, safetyStock: 270, reorderPoint: 540, eoq: 610, recommendedOrder: 910, daysRemaining: 15, status: "reorder-now" },
  { sku: "SKU-1007", productName: "Noise Cancelling Earbuds", category: "Electronics", supplier: "TechSupply Co.", currentStock: 2300, forecastDemand: 1450, safetyStock: 218, reorderPoint: 435, eoq: 520, recommendedOrder: 0, daysRemaining: 48, status: "healthy" },
  { sku: "SKU-1008", productName: "Desk Lamp", category: "Furniture", supplier: "OfficePro Ltd.", currentStock: 180, forecastDemand: 1200, safetyStock: 180, reorderPoint: 360, eoq: 490, recommendedOrder: 1020, daysRemaining: 5, status: "critical" },
  { sku: "SKU-1009", productName: "Laptop Stand", category: "Accessories", supplier: "ConnectWorld Inc.", currentStock: 1100, forecastDemand: 1500, safetyStock: 225, reorderPoint: 450, eoq: 530, recommendedOrder: 400, daysRemaining: 22, status: "healthy" },
  { sku: "SKU-1010", productName: "Webcam 4K", category: "Electronics", supplier: "TechSupply Co.", currentStock: 650, forecastDemand: 950, safetyStock: 143, reorderPoint: 285, eoq: 380, recommendedOrder: 300, daysRemaining: 20, status: "reorder-soon" },
  { sku: "SKU-1011", productName: "Smart Power Strip", category: "Electronics", supplier: "TechSupply Co.", currentStock: 450, forecastDemand: 1100, safetyStock: 165, reorderPoint: 330, eoq: 440, recommendedOrder: 650, daysRemaining: 12, status: "reorder-now" },
  { sku: "SKU-1012", productName: "Cable Management Kit", category: "Accessories", supplier: "ConnectWorld Inc.", currentStock: 2800, forecastDemand: 800, safetyStock: 120, reorderPoint: 240, eoq: 320, recommendedOrder: 0, daysRemaining: 105, status: "healthy" },
];

export const mockInventoryMetrics: InventoryMetrics = {
  totalInventoryValue: 284500,
  productsRequiringReorder: 6,
  healthScore: 72,
  daysOfInventoryRemaining: 28,
};

export const mockInventoryHealth: InventoryHealth = {
  score: 72,
  status: "good",
  breakdown: {
    healthy: 45,
    lowStock: 30,
    overstock: 15,
    slowMoving: 10,
  },
};

export const mockRiskProducts: RiskProduct[] = [
  { product: "Desk Lamp", sku: "SKU-1008", currentStock: 180, forecastDemand: 1200, riskType: "stockout" },
  { product: "Standing Desk", sku: "SKU-1004", currentStock: 320, forecastDemand: 950, riskType: "stockout" },
  { product: "Cable Management Kit", sku: "SKU-1012", currentStock: 2800, forecastDemand: 800, riskType: "overstock" },
  { product: "Noise Cancelling Earbuds", sku: "SKU-1007", currentStock: 2300, forecastDemand: 1450, riskType: "overstock" },
  { product: "Monitor Arm", sku: "SKU-1006", currentStock: 890, forecastDemand: 1800, riskType: "slow-moving" },
  { product: "Smart Power Strip", sku: "SKU-1011", currentStock: 450, forecastDemand: 1100, riskType: "slow-moving" },
];

export const mockRecommendations: Recommendation[] = [
  { sku: "SKU-1008", productName: "Desk Lamp", action: "Order 1,020 units to replenish stock. Inventory at critical level.", quantity: 1020, daysUntilAction: 2 },
  { sku: "SKU-1004", productName: "Standing Desk", action: "Place urgent order for 630 units. Only 10 days of stock remaining.", quantity: 630, daysUntilAction: 3 },
  { sku: "SKU-1002", productName: "Ergonomic Chair", action: "Order 640 units within the week to maintain service level.", quantity: 640, daysUntilAction: 5 },
  { sku: "SKU-1011", productName: "Smart Power Strip", action: "Replenish 650 units to meet upcoming forecast demand.", quantity: 650, daysUntilAction: 5 },
  { sku: "SKU-1001", productName: "Wireless Headphones", action: "Schedule order for 650 units before stock drops below reorder point.", quantity: 650, daysUntilAction: 7 },
  { sku: "SKU-1012", productName: "Cable Management Kit", action: "Reduce future purchases — excess stock of 2,800 units with declining demand.", quantity: 0, daysUntilAction: 30 },
  { sku: "SKU-1007", productName: "Noise Cancelling Earbuds", action: "Consider promotion — overstocked with 2,300 units.", quantity: 0, daysUntilAction: 14 },
];

export const mockPurchasePlans: PurchasePlan[] = [
  {
    supplier: "TechSupply Co.",
    items: [
      { supplier: "TechSupply Co.", productName: "Wireless Headphones", sku: "SKU-1001", quantity: 650, unitCost: 45, estimatedCost: 29250 },
      { supplier: "TechSupply Co.", productName: "Smart Power Strip", sku: "SKU-1011", quantity: 650, unitCost: 22, estimatedCost: 14300 },
      { supplier: "TechSupply Co.", productName: "Webcam 4K", sku: "SKU-1010", quantity: 300, unitCost: 85, estimatedCost: 25500 },
    ],
    totalQuantity: 1600,
    totalCost: 69050,
  },
  {
    supplier: "OfficePro Ltd.",
    items: [
      { supplier: "OfficePro Ltd.", productName: "Ergonomic Chair", sku: "SKU-1002", quantity: 640, unitCost: 210, estimatedCost: 134400 },
      { supplier: "OfficePro Ltd.", productName: "Standing Desk", sku: "SKU-1004", quantity: 630, unitCost: 350, estimatedCost: 220500 },
      { supplier: "OfficePro Ltd.", productName: "Desk Lamp", sku: "SKU-1008", quantity: 1020, unitCost: 38, estimatedCost: 38760 },
    ],
    totalQuantity: 2290,
    totalCost: 393660,
  },
  {
    supplier: "ConnectWorld Inc.",
    items: [
      { supplier: "ConnectWorld Inc.", productName: "USB-C Hub", sku: "SKU-1005", quantity: 850, unitCost: 28, estimatedCost: 23800 },
      { supplier: "ConnectWorld Inc.", productName: "Monitor Arm", sku: "SKU-1006", quantity: 910, unitCost: 55, estimatedCost: 50050 },
    ],
    totalQuantity: 1760,
    totalCost: 73850,
  },
];

export const mockTrendData: TrendDataPoint[] = [
  { month: "2024-07", inventoryLevel: 12400, forecastDemand: 11000, safetyStockThreshold: 3600 },
  { month: "2024-08", inventoryLevel: 11800, forecastDemand: 11500, safetyStockThreshold: 3600 },
  { month: "2024-09", inventoryLevel: 12500, forecastDemand: 10800, safetyStockThreshold: 3700 },
  { month: "2024-10", inventoryLevel: 11200, forecastDemand: 12000, safetyStockThreshold: 3700 },
  { month: "2024-11", inventoryLevel: 10500, forecastDemand: 12800, safetyStockThreshold: 3800 },
  { month: "2024-12", inventoryLevel: 9800, forecastDemand: 13500, safetyStockThreshold: 3800 },
  { month: "2025-01", inventoryLevel: 10800, forecastDemand: 12200, safetyStockThreshold: 3900 },
  { month: "2025-02", inventoryLevel: 11500, forecastDemand: 11800, safetyStockThreshold: 3900 },
  { month: "2025-03", inventoryLevel: 11000, forecastDemand: 12500, safetyStockThreshold: 4000 },
  { month: "2025-04", inventoryLevel: 10200, forecastDemand: 13000, safetyStockThreshold: 4000 },
  { month: "2025-05", inventoryLevel: 9500, forecastDemand: 13800, safetyStockThreshold: 4100 },
  { month: "2025-06", inventoryLevel: 8800, forecastDemand: 14200, safetyStockThreshold: 4100 },
];

export const mockProducts = [
  { id: "all", name: "All Products" },
  ...mockInventoryPlan.map((p) => ({ id: p.sku, name: p.productName })),
];

export const mockCategories = [
  "All Categories",
  ...new Set(mockInventoryPlan.map((p) => p.category)),
];

export const mockSuppliers = [
  "All Suppliers",
  ...new Set(mockInventoryPlan.map((p) => p.supplier)),
];

export const mockStatuses = [
  { value: "all", label: "All Statuses" },
  { value: "healthy", label: "Healthy" },
  { value: "reorder-soon", label: "Reorder Soon" },
  { value: "reorder-now", label: "Reorder Now" },
  { value: "critical", label: "Critical" },
];
