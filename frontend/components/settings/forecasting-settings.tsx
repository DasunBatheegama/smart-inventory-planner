"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { ChartNoAxesCombined, Info, RotateCcw, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { ForecastSettings } from "@/types/settings";

const forecastingSchema = z.object({
  method: z.enum(["Moving Average", "Exponential Smoothing"]),
  horizon: z.coerce.number().min(1),
  minimumHistoricalData: z.coerce.number().min(1),
  confidenceThreshold: z.coerce.number().min(1).max(100),
});

interface ForecastingSettingsFormProps {
  data: ForecastSettings;
  onSave: (values: ForecastSettings) => Promise<void>;
  onDirtyChange?: (dirty: boolean) => void;
}

export function ForecastingSettingsForm({ data, onSave, onDirtyChange }: ForecastingSettingsFormProps) {
  const form = useForm<ForecastSettings>({
    resolver: zodResolver(forecastingSchema) as any,
    defaultValues: data,
    mode: "onChange",
  });

  React.useEffect(() => {
    form.reset(data);
  }, [data, form]);

  React.useEffect(() => {
    onDirtyChange?.(form.formState.isDirty);
  }, [form.formState.isDirty, onDirtyChange]);

  const onSubmit = async (values: ForecastSettings) => {
    await onSave(values);
    form.reset(values);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="rounded-md bg-violet-500/10 p-2 text-violet-600">
            <ChartNoAxesCombined className="h-4 w-4" />
          </div>
          <div>
            <CardTitle>Forecasting Preferences</CardTitle>
            <CardDescription>Control the default configuration used for demand forecasting.</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
          <div className="flex items-start gap-2">
            <Info className="mt-0.5 h-4 w-4 text-primary" />
            <p>Forecasting settings determine the default configuration used when generating demand forecasts.</p>
          </div>
        </div>

        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label>Default Forecast Method</Label>
              <Select value={form.watch("method")} onValueChange={(value) => form.setValue("method", value as ForecastSettings["method"]) }>
                <SelectTrigger className="w-full"><SelectValue placeholder="Select method" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Moving Average">Moving Average</SelectItem>
                  <SelectItem value="Exponential Smoothing">Exponential Smoothing</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Default Forecast Horizon</Label>
              <Select value={String(form.watch("horizon"))} onValueChange={(value) => form.setValue("horizon", Number(value))}>
                <SelectTrigger className="w-full"><SelectValue placeholder="Select horizon" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">1 Month</SelectItem>
                  <SelectItem value="3">3 Months</SelectItem>
                  <SelectItem value="6">6 Months</SelectItem>
                  <SelectItem value="12">12 Months</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Minimum Historical Data</Label>
              <Select value={String(form.watch("minimumHistoricalData"))} onValueChange={(value) => form.setValue("minimumHistoricalData", Number(value))}>
                <SelectTrigger className="w-full"><SelectValue placeholder="Select data length" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="30">30 Days</SelectItem>
                  <SelectItem value="60">60 Days</SelectItem>
                  <SelectItem value="90">90 Days</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="confidenceThreshold">Forecast Confidence Threshold</Label>
              <div className="relative">
                <Input id="confidenceThreshold" type="number" min={1} max={100} step="1" {...form.register("confidenceThreshold")} />
                <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-sm text-muted-foreground">%</span>
              </div>
              {form.formState.errors.confidenceThreshold && (
                <p className="text-sm text-destructive">{form.formState.errors.confidenceThreshold.message}</p>
              )}
            </div>
          </div>

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="outline" onClick={() => form.reset(data)} className="gap-2">
              <RotateCcw className="h-4 w-4" />
              Reset Defaults
            </Button>
            <Button type="submit" disabled={form.formState.isSubmitting || !form.formState.isDirty} className="gap-2">
              <Save className="h-4 w-4" />
              {form.formState.isSubmitting ? "Saving..." : "Save Forecast Settings"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
