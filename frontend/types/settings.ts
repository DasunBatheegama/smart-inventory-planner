export type SettingsSectionKey =
  | "general"
  | "inventory"
  | "forecasting"
  | "notifications"
  | "appearance"
  | "account";

export interface CompanySettings {
  companyName: string;
  industry: string;
  country: string;
  currency: string;
  timezone: string;
}

export interface InventorySettings {
  defaultLeadTime: number;
  safetyStockMethod: "Fixed" | "Percentage" | "Demand Variability";
  reorderStrategy: "Reorder Point" | "Periodic Review";
  serviceLevel: number;
  reviewPeriod: "Daily" | "Weekly" | "Monthly";
}

export interface ForecastSettings {
  method: "Moving Average" | "Exponential Smoothing";
  horizon: number;
  minimumHistoricalData: number;
  confidenceThreshold: number;
}

export interface NotificationSettings {
  lowStock: boolean;
  stockoutRisk: boolean;
  overstock: boolean;
  forecastAlerts: boolean;
  aiRecommendations: boolean;
  email: boolean;
  inApp: boolean;
}

export interface AppearanceSettings {
  theme: "Light" | "Dark" | "System";
  density: "Comfortable" | "Compact";
  language: "English";
}

export interface AccountSettings {
  name: string;
  email: string;
  role: string;
  accountCreated: string;
}

export interface SettingsState {
  company: CompanySettings;
  inventory: InventorySettings;
  forecasting: ForecastSettings;
  notifications: NotificationSettings;
  appearance: AppearanceSettings;
  account: AccountSettings;
}

export interface SettingsSection {
  id: SettingsSectionKey;
  label: string;
}
