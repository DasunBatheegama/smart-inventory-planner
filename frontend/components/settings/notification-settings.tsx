"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { BellRing, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { NotificationSettings } from "@/types/settings";

interface NotificationSettingsFormProps {
  data: NotificationSettings;
  onSave: (values: NotificationSettings) => Promise<void>;
  onDirtyChange?: (dirty: boolean) => void;
}

export function NotificationSettingsForm({ data, onSave, onDirtyChange }: NotificationSettingsFormProps) {
  const form = useForm<NotificationSettings>({
    defaultValues: data,
    mode: "onChange",
  });

  React.useEffect(() => {
    form.reset(data);
  }, [data, form]);

  React.useEffect(() => {
    onDirtyChange?.(form.formState.isDirty);
  }, [form.formState.isDirty, onDirtyChange]);

  const onSubmit = async (values: NotificationSettings) => {
    await onSave(values);
    form.reset(values);
  };

  const toggle = (key: keyof NotificationSettings) =>
    form.setValue(key, !form.watch(key), { shouldDirty: true });

  const notificationOptions: Array<{ key: keyof NotificationSettings; label: string }> = [
    { key: "lowStock", label: "Low Stock Alerts" },
    { key: "stockoutRisk", label: "Stockout Risk Alerts" },
    { key: "overstock", label: "Overstock Alerts" },
    { key: "forecastAlerts", label: "Forecast Alerts" },
    { key: "aiRecommendations", label: "AI Recommendations" },
    { key: "email", label: "Email Notifications" },
    { key: "inApp", label: "In-App Notifications" },
  ];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="rounded-md bg-amber-500/10 p-2 text-amber-600">
            <BellRing className="h-4 w-4" />
          </div>
          <div>
            <CardTitle>Notifications</CardTitle>
            <CardDescription>Choose which signals and updates you want to receive.</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="space-y-4">
            {notificationOptions.map((option) => (
              <div key={option.key} className="flex items-center justify-between rounded-lg border p-3">
                <Label className="text-sm font-medium">{option.label}</Label>
                <Switch
                  checked={Boolean(form.watch(option.key))}
                  onCheckedChange={() => toggle(option.key)}
                  aria-label={option.label}
                />
              </div>
            ))}
          </div>

          <div className="flex justify-end">
            <Button type="submit" disabled={form.formState.isSubmitting || !form.formState.isDirty} className="gap-2">
              <Save className="h-4 w-4" />
              {form.formState.isSubmitting ? "Saving..." : "Save Notification Settings"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
