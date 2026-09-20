import { SettingsState } from "@/types/settings";

export const mockSettings: SettingsState = {
  company: {
    companyName: "ABC Retail",
    industry: "Retail",
    country: "Sri Lanka",
    currency: "USD",
    timezone: "Asia/Colombo",
  },
  inventory: {
    defaultLeadTime: 10,
    safetyStockMethod: "Percentage",
    reorderStrategy: "Reorder Point",
    serviceLevel: 95,
    reviewPeriod: "Weekly",
  },
  forecasting: {
    method: "Exponential Smoothing",
    horizon: 3,
    minimumHistoricalData: 60,
    confidenceThreshold: 85,
  },
  notifications: {
    lowStock: true,
    stockoutRisk: true,
    overstock: false,
    forecastAlerts: true,
    aiRecommendations: true,
    email: true,
    inApp: true,
  },
  appearance: {
    theme: "System",
    density: "Comfortable",
    language: "English",
  },
  account: {
    name: "John Smith",
    email: "john@example.com",
    role: "Administrator",
    accountCreated: "2024-01-15",
  },
};
