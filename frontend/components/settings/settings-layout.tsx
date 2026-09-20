"use client";

import * as React from "react";
import { Settings2, Sparkles } from "lucide-react";
import { SettingsSidebar } from "@/components/settings/settings-sidebar";
import { CompanySettingsForm } from "@/components/settings/company-settings";
import { InventorySettingsForm } from "@/components/settings/inventory-settings";
import { ForecastingSettingsForm } from "@/components/settings/forecasting-settings";
import { NotificationSettingsForm } from "@/components/settings/notification-settings";
import { AppearanceSettingsForm } from "@/components/settings/appearance-settings";
import { AccountSettingsForm } from "@/components/settings/account-settings";
import { settingsService } from "@/services/settings.service";
import { SettingsState, SettingsSectionKey } from "@/types/settings";

const initialDirtyState: Record<SettingsSectionKey, boolean> = {
  general: false,
  inventory: false,
  forecasting: false,
  notifications: false,
  appearance: false,
  account: false,
};

export function SettingsLayout() {
  const [settings, setSettings] = React.useState<SettingsState | null>(null);
  const [activeSection, setActiveSection] = React.useState<SettingsSectionKey>("general");
  const [dirtyState, setDirtyState] = React.useState(initialDirtyState);
  const [toast, setToast] = React.useState<{ title: string; description: string } | null>(null);

  React.useEffect(() => {
    const loadSettings = async () => {
      const data = await settingsService.getSettings();
      setSettings(data);
    };

    loadSettings();
  }, []);

  React.useEffect(() => {
    if (!toast) {
      return;
    }

    const timeout = window.setTimeout(() => setToast(null), 3000);
    return () => window.clearTimeout(timeout);
  }, [toast]);

  const hasUnsavedChanges = Object.values(dirtyState).some(Boolean);

  const handleDirtyChange = React.useCallback((section: SettingsSectionKey, dirty: boolean) => {
    setDirtyState((prev) => {
      if (prev[section] === dirty) {
        return prev;
      }

      return { ...prev, [section]: dirty };
    });
  }, []);

  const handleSectionChange = (nextSection: SettingsSectionKey) => {
    if (activeSection === nextSection) {
      return;
    }

    if (hasUnsavedChanges) {
      const confirmLeave = window.confirm(
        "You have unsaved changes. Leave this section without saving?",
      );

      if (!confirmLeave) {
        return;
      }
    }

    setActiveSection(nextSection);
  };

  const showToast = (title: string, description: string) => {
    setToast({ title, description });
  };

  if (!settings) {
    return (
      <div className="space-y-6">
        <div className="h-10 w-48 animate-pulse rounded-md bg-muted" />
        <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
          <div className="h-80 animate-pulse rounded-xl bg-muted" />
          <div className="h-96 animate-pulse rounded-xl bg-muted" />
        </div>
      </div>
    );
  }

  const renderSection = () => {
    switch (activeSection) {
      case "general":
        return (
          <CompanySettingsForm
            data={settings.company}
            onSave={async (values) => {
              const updated = await settingsService.updateCompanySettings(values);
              setSettings((prev) => (prev ? { ...prev, company: updated } : prev));
              showToast("Company settings saved", "Your company profile and preferences were updated.");
            }}
            onDirtyChange={(dirty) => handleDirtyChange("general", dirty)}
          />
        );
      case "inventory":
        return (
          <InventorySettingsForm
            data={settings.inventory}
            onSave={async (values) => {
              const updated = await settingsService.updateInventorySettings(values);
              setSettings((prev) => (prev ? { ...prev, inventory: updated } : prev));
              showToast("Planning settings saved", "Your default inventory settings have been updated.");
            }}
            onDirtyChange={(dirty) => handleDirtyChange("inventory", dirty)}
          />
        );
      case "forecasting":
        return (
          <ForecastingSettingsForm
            data={settings.forecasting}
            onSave={async (values) => {
              const updated = await settingsService.updateForecastSettings(values);
              setSettings((prev) => (prev ? { ...prev, forecasting: updated } : prev));
              showToast("Forecast settings saved", "Your forecasting defaults were updated.");
            }}
            onDirtyChange={(dirty) => handleDirtyChange("forecasting", dirty)}
          />
        );
      case "notifications":
        return (
          <NotificationSettingsForm
            data={settings.notifications}
            onSave={async (values) => {
              const updated = await settingsService.updateNotificationSettings(values);
              setSettings((prev) => (prev ? { ...prev, notifications: updated } : prev));
              showToast("Notification settings saved", "Your alert preferences were updated.");
            }}
            onDirtyChange={(dirty) => handleDirtyChange("notifications", dirty)}
          />
        );
      case "appearance":
        return (
          <AppearanceSettingsForm
            data={settings.appearance}
            onSave={async (values) => {
              const updated = await settingsService.updateAppearanceSettings(values);
              setSettings((prev) => (prev ? { ...prev, appearance: updated } : prev));
              showToast("Appearance settings saved", "Your dashboard presentation preferences were updated.");
            }}
            onDirtyChange={(dirty) => handleDirtyChange("appearance", dirty)}
          />
        );
      case "account":
        return (
          <AccountSettingsForm
            data={settings.account}
            onSave={async (values) => {
              const updated = await settingsService.updateAccountSettings(values);
              setSettings((prev) => (prev ? { ...prev, account: updated } : prev));
              showToast("Account settings saved", "Your account information was updated.");
            }}
            onDirtyChange={(dirty) => handleDirtyChange("account", dirty)}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="mb-2 flex items-center gap-2 text-sm font-medium text-primary">
            <Settings2 className="h-4 w-4" />
            Configuration
          </div>
          <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
          <p className="mt-2 text-muted-foreground">
            Manage your InventIQ account and application preferences.
          </p>
        </div>
        <div className="rounded-full border bg-muted/50 px-3 py-1 text-sm text-muted-foreground">
          {hasUnsavedChanges ? "Unsaved changes" : "All changes saved"}
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[260px_1fr]">
        <SettingsSidebar activeSection={activeSection} onSelect={handleSectionChange} />
        <div>{renderSection()}</div>
      </div>

      {toast && (
        <div className="pointer-events-none fixed right-5 bottom-5 z-50 max-w-sm rounded-lg border bg-background p-4 shadow-lg ring-1 ring-border">
          <div className="flex items-start gap-3">
            <div className="mt-0.5 rounded-full bg-emerald-500/10 p-1.5 text-emerald-600">
              <Sparkles className="h-4 w-4" />
            </div>
            <div>
              <p className="font-medium">{toast.title}</p>
              <p className="mt-1 text-sm text-muted-foreground">{toast.description}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
