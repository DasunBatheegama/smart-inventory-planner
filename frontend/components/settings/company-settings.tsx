"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { Building2, Save, X } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CompanySettings } from "@/types/settings";

const companySchema = z.object({
  companyName: z.string().trim().min(1, "Company name is required."),
  industry: z.string().trim().min(1, "Industry is required."),
  country: z.string().trim().min(2, "Country is required."),
  currency: z.string().trim().toUpperCase().regex(/^[A-Z]{3}$/, "Currency must be a valid ISO code."),
  timezone: z.string().trim().min(1, "Time zone is required."),
});

interface CompanySettingsFormProps {
  data: CompanySettings;
  onSave: (values: CompanySettings) => Promise<void>;
  onDirtyChange?: (dirty: boolean) => void;
}

export function CompanySettingsForm({ data, onSave, onDirtyChange }: CompanySettingsFormProps) {
  const form = useForm<CompanySettings>({
    resolver: zodResolver(companySchema),
    defaultValues: data,
    mode: "onChange",
  });

  React.useEffect(() => {
    form.reset(data);
  }, [data, form]);

  React.useEffect(() => {
    onDirtyChange?.(form.formState.isDirty);
  }, [form.formState.isDirty, onDirtyChange]);

  const onSubmit = async (values: CompanySettings) => {
    await onSave(values);
    form.reset(values);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="rounded-md bg-primary/10 p-2 text-primary">
            <Building2 className="h-4 w-4" />
          </div>
          <div>
            <CardTitle>Company Profile</CardTitle>
            <CardDescription>Update your organization details for planning and reporting.</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="companyName">Company Name</Label>
              <Input id="companyName" {...form.register("companyName")} placeholder="ABC Retail" />
              {form.formState.errors.companyName && (
                <p className="text-sm text-destructive">{form.formState.errors.companyName.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="industry">Industry</Label>
              <Input id="industry" {...form.register("industry")} placeholder="Retail" />
              {form.formState.errors.industry && (
                <p className="text-sm text-destructive">{form.formState.errors.industry.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="country">Country</Label>
              <Input id="country" {...form.register("country")} placeholder="Sri Lanka" />
              {form.formState.errors.country && (
                <p className="text-sm text-destructive">{form.formState.errors.country.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="currency">Currency</Label>
              <Input id="currency" {...form.register("currency")} placeholder="USD" maxLength={3} className="uppercase" />
              {form.formState.errors.currency && (
                <p className="text-sm text-destructive">{form.formState.errors.currency.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="timezone">Time Zone</Label>
              <Input id="timezone" {...form.register("timezone")} placeholder="Asia/Colombo" />
              {form.formState.errors.timezone && (
                <p className="text-sm text-destructive">{form.formState.errors.timezone.message}</p>
              )}
            </div>
          </div>

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="outline" onClick={() => form.reset(data)} className="gap-2">
              <X className="h-4 w-4" />
              Cancel
            </Button>
            <Button type="submit" disabled={form.formState.isSubmitting || !form.formState.isDirty} className="gap-2">
              <Save className="h-4 w-4" />
              {form.formState.isSubmitting ? "Saving..." : "Save Changes"}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
