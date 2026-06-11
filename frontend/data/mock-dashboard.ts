import { Package, DollarSign, AlertTriangle, TrendingUp } from "lucide-react";

export const kpiData = [
  {
    title: "Total Products",
    value: "12,345",
    trend: "+12.5%",
    trendUp: true,
    icon: Package,
  },
  {
    title: "Inventory Value",
    value: "$1.4M",
    trend: "+4.2%",
    trendUp: true,
    icon: DollarSign,
  },
  {
    title: "Low Stock Items",
    value: "34",
    trend: "-2.5%",
    trendUp: false,
    icon: AlertTriangle,
  },
  {
    title: "Forecast Accuracy",
    value: "94.2%",
    trend: "+1.2%",
    trendUp: true,
    icon: TrendingUp,
  },
];

export const recentAlerts = [
  {
    id: 1,
    title: "Low Stock: Widget A",
    description: "Only 12 units remaining. Forecasted to stockout in 3 days.",
    type: "low_stock",
    time: "2 hours ago"
  },
  {
    id: 2,
    title: "Overstock: Widget B",
    description: "500 units stranded. Suggested action: run promotion.",
    type: "overstock",
    time: "5 hours ago"
  },
  {
    id: 3,
    title: "Stockout Risk: Widget C",
    description: "Supplier delay expected. Restock immediately.",
    type: "stockout",
    time: "1 day ago"
  }
];

export const inventoryHealth = {
  score: 85,
  categories: {
    healthy: 75,
    lowStock: 15,
    overstock: 10,
  }
};

export const forecastSummary = {
  nextMonthDemand: "14,500 units",
  topGrowing: [
    { name: "Wireless Headphones", growth: "+45%" },
    { name: "Ergonomic Chair", growth: "+32%" },
    { name: "Mechanical Keyboard", growth: "+28%" }
  ]
};

export const recentActivity = [
  {
    id: 1,
    action: "Forecast Generated",
    details: "Q3 Demand Forecast completed across all categories.",
    time: "10 mins ago"
  },
  {
    id: 2,
    action: "Sales Data Uploaded",
    details: "May 2026 POS data synced successfully.",
    time: "1 hour ago"
  },
  {
    id: 3,
    action: "Product Created",
    details: "SKU X-99 added to electronics category.",
    time: "3 hours ago"
  }
];