"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Info, Package2, RotateCcw, Save } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { InventorySettings } from "@/types/settings";

const inventorySchema = z.object({
  defaultLeadTime: z.coerce.number().min(1, "Lead time must be at least 1 day."),
  safetyStockMethod: z.enum(["Fixed", "Percentage", "Demand Variability"]),
  reorderStrategy: z.enum(["Reorder Point", "Periodic Review"]),
  serviceLevel: z.coerce.number().min(50).max(99.9),
  reviewPeriod: z.enum(["Daily", "Weekly", "Monthly"]),
});

interface InventorySettingsFormProps {
  data: InventorySettings;
  onSave: (values: InventorySettings) => Promise<void>;
  onDirtyChange?: (dirty: boolean) => void;
}

export function InventorySettingsForm({ data, onSave, onDirtyChange }: InventorySettingsFormProps) {
  const form = useForm<InventorySettings>({
    resolver: zodResolver(inventorySchema) as any,
    defaultValues: data,
    mode: "onChange",
  });

  React.useEffect(() => {
    form.reset(data);
  }, [data, form]);

  React.useEffect(() => {
    onDirtyChange?.(form.formState.isDirty);
  }, [form.formState.isDirty, onDirtyChange]);

  const onSubmit = async (values: InventorySettings) => {
    await onSave(values);
    form.reset(values);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="rounded-md bg-emerald-500/10 p-2 text-emerald-600">
            <Package2 className="h-4 w-4" />
          </div>
          <div>
            <CardTitle>Inventory Planning Defaults</CardTitle>
            <CardDescription>Set the baseline planning assumptions for replenishment workflows.</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground">
          <div className="flex items-start gap-2">
            <Info className="mt-0.5 h-4 w-4 text-primary" />
            <p>These settings are used as default values when generating inventory recommendations.</p>
          </div>
        </div>

        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="defaultLeadTime">Default Lead Time</Label>
              <Input id="defaultLeadTime" type="number" min={1} {...form.register("defaultLeadTime")} />
              {form.formState.errors.defaultLeadTime && (
                <p className="text-sm text-destructive">{form.formState.errors.defaultLeadTime.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label>Safety Stock Method</Label>
              <Select value={form.watch("safetyStockMethod")} onValueChange={(value) => form.setValue("safetyStockMethod", value as InventorySettings["safetyStockMethod"]) }>
                <SelectTrigger className="w-full"><SelectValue placeholder="Select method" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Fixed">Fixed</SelectItem>
                  <SelectItem value="Percentage">Percentage</SelectItem>
                  <SelectItem value="Demand Variability">Demand Variability</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label>Reorder Strategy</Label>
              <Select value={form.watch("reorderStrategy")} onValueChange={(value) => form.setValue("reorderStrategy", value as InventorySettings["reorderStrategy"]) }>
                <SelectTrigger className="w-full"><SelectValue placeholder="Select strategy" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Reorder Point">Reorder Point</SelectItem>
                  <SelectItem value="Periodic Review">Periodic Review</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="serviceLevel">Default Service Level</Label>
              <Input id="serviceLevel" type="number" min={50} max={99.9} step="0.1" {...form.register("serviceLevel")} />
              {form.formState.errors.serviceLevel && (
                <p className="text-sm text-destructive">{form.formState.errors.serviceLevel.message}</p>
              )}
            </div>

            <div className="space-y-2 md:col-span-2">
              <Label>Default Inventory Review Period</Label>
              <Select value={form.watch("reviewPeriod")} onValueChange={(value) => form.setValue("reviewPeriod", value as InventorySettings["reviewPeriod"]) }>
                <SelectTrigger className="w-full"><SelectValue placeholder="Select period" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="Daily">Daily</SelectItem>
                  <SelectItem value="Weekly">Weekly</SelectItem>
                  <SelectItem value="Monthly">Monthly</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="outline" onClick={() => form.reset(data)} className="gap-2">
              <RotateCcw className="h-4 w-4" />
              Reset Defaults
            </Button>
            <Button type="submit" disabled={form.formState.isSubmitting || !form.formState.isDirty} className="gap-2">
              <Save className="h-4 w-4" />
              {form.formState.isSubmitting ? "Saving..." : "Save Planning Settings"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
