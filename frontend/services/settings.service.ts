import { mockSettings } from "@/data/mock-settings";
import {
  AccountSettings,
  AppearanceSettings,
  CompanySettings,
  ForecastSettings,
  InventorySettings,
  NotificationSettings,
  SettingsState,
} from "@/types/settings";

let settingsStore: SettingsState = structuredClone(mockSettings);

export const settingsService = {
  async getSettings(): Promise<SettingsState> {
    return structuredClone(settingsStore);
  },

  async updateCompanySettings(values: CompanySettings): Promise<CompanySettings> {
    settingsStore = {
      ...settingsStore,
      company: { ...values },
    };
    return structuredClone(settingsStore.company);
  },

  async updateInventorySettings(values: InventorySettings): Promise<InventorySettings> {
    settingsStore = {
      ...settingsStore,
      inventory: { ...values },
    };
    return structuredClone(settingsStore.inventory);
  },

  async updateForecastSettings(values: ForecastSettings): Promise<ForecastSettings> {
    settingsStore = {
      ...settingsStore,
      forecasting: { ...values },
    };
    return structuredClone(settingsStore.forecasting);
  },

  async updateNotificationSettings(values: NotificationSettings): Promise<NotificationSettings> {
    settingsStore = {
      ...settingsStore,
      notifications: { ...values },
    };
    return structuredClone(settingsStore.notifications);
  },

  async updateAppearanceSettings(values: AppearanceSettings): Promise<AppearanceSettings> {
    settingsStore = {
      ...settingsStore,
      appearance: { ...values },
    };
    return structuredClone(settingsStore.appearance);
  },

  async updateAccountSettings(values: AccountSettings): Promise<AccountSettings> {
    settingsStore = {
      ...settingsStore,
      account: { ...values },
    };
    return structuredClone(settingsStore.account);
  },
};
