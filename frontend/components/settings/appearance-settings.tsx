"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { Palette, Save } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AppearanceSettings } from "@/types/settings";

interface AppearanceSettingsFormProps {
  data: AppearanceSettings;
  onSave: (values: AppearanceSettings) => Promise<void>;
  onDirtyChange?: (dirty: boolean) => void;
}

export function AppearanceSettingsForm({ data, onSave, onDirtyChange }: AppearanceSettingsFormProps) {
  const { setTheme } = useTheme();
  const form = useForm<AppearanceSettings>({
    defaultValues: data,
    mode: "onChange",
  });

  React.useEffect(() => {
    form.reset(data);
  }, [data, form]);

  React.useEffect(() => {
    onDirtyChange?.(form.formState.isDirty);
  }, [form.formState.isDirty, onDirtyChange]);

  const onSubmit = async (values: AppearanceSettings) => {
    if (values.theme === "Light") {
      setTheme("light");
    } else if (values.theme === "Dark") {
      setTheme("dark");
    } else {
      setTheme("system");
    }

    await onSave(values);
    form.reset(values);
  };

  const currentTheme = form.watch("theme");

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="rounded-md bg-cyan-500/10 p-2 text-cyan-600">
            <Palette className="h-4 w-4" />
          </div>
          <div>
            <CardTitle>Appearance</CardTitle>
            <CardDescription>Adjust the dashboard look and language to fit your workflow.</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <Label>Theme</Label>
            <Select value={currentTheme} onValueChange={(value) => form.setValue("theme", value as AppearanceSettings["theme"], { shouldDirty: true })}>
              <SelectTrigger className="w-full"><SelectValue placeholder="Select theme" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="Light">Light</SelectItem>
                <SelectItem value="Dark">Dark</SelectItem>
                <SelectItem value="System">System</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label>Dashboard Density</Label>
            <Select value={form.watch("density")} onValueChange={(value) => form.setValue("density", value as AppearanceSettings["density"], { shouldDirty: true })}>
              <SelectTrigger className="w-full"><SelectValue placeholder="Select density" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="Comfortable">Comfortable</SelectItem>
                <SelectItem value="Compact">Compact</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2 md:col-span-2">
            <Label>Language</Label>
            <Select value={form.watch("language")} onValueChange={(value) => form.setValue("language", value as AppearanceSettings["language"], { shouldDirty: true })}>
              <SelectTrigger className="w-full"><SelectValue placeholder="Select language" /></SelectTrigger>
              <SelectContent>
                <SelectItem value="English">English</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="rounded-xl border bg-gradient-to-br from-background via-muted/60 to-primary/5 p-4">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-sm font-medium">Preview</span>
            <span className="rounded-full border px-2 py-0.5 text-xs text-muted-foreground">{currentTheme}</span>
          </div>
          <div className="rounded-lg border bg-card p-4 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium">Inventory Overview</p>
                <p className="text-xs text-muted-foreground">January 2026</p>
              </div>
              <div className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
            </div>
            <div className="mt-4 grid grid-cols-3 gap-2 text-xs text-muted-foreground">
              <div className="rounded-md bg-muted p-2">Stock: 82%</div>
              <div className="rounded-md bg-muted p-2">Orders: 14</div>
              <div className="rounded-md bg-muted p-2">Alerts: 3</div>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <Button type="button" onClick={form.handleSubmit(onSubmit)} disabled={form.formState.isSubmitting || !form.formState.isDirty} className="gap-2">
            <Save className="h-4 w-4" />
            {form.formState.isSubmitting ? "Saving..." : "Save Appearance Settings"}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
