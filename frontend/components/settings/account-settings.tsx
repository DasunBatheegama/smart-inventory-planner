"use client";

import * as React from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { AlertTriangle, KeyRound, LogOut, Save, ShieldAlert, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { AccountSettings } from "@/types/settings";
import { DeleteAccountDialog } from "@/components/settings/delete-account-dialog";

const accountSchema = z.object({
  name: z.string().trim().min(1, "Name is required."),
  email: z.string().trim().email("Please enter a valid email."),
  role: z.string().trim().min(1, "Role is required."),
  accountCreated: z.string().trim().min(1, "Account created date is required."),
});

interface AccountSettingsFormProps {
  data: AccountSettings;
  onSave: (values: AccountSettings) => Promise<void>;
  onDirtyChange?: (dirty: boolean) => void;
}

export function AccountSettingsForm({ data, onSave, onDirtyChange }: AccountSettingsFormProps) {
  const form = useForm<AccountSettings>({
    resolver: zodResolver(accountSchema),
    defaultValues: data,
    mode: "onChange",
  });

  React.useEffect(() => {
    form.reset(data);
  }, [data, form]);

  React.useEffect(() => {
    onDirtyChange?.(form.formState.isDirty);
  }, [form.formState.isDirty, onDirtyChange]);

  const onSubmit = async (values: AccountSettings) => {
    await onSave(values);
    form.reset(values);
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center gap-2">
          <div className="rounded-md bg-sky-500/10 p-2 text-sky-600">
            <UserRound className="h-4 w-4" />
          </div>
          <div>
            <CardTitle>Account Information</CardTitle>
            <CardDescription>Review your profile and security details.</CardDescription>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-6">
        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="name">User Name</Label>
              <Input id="name" {...form.register("name")} />
              {form.formState.errors.name && (
                <p className="text-sm text-destructive">{form.formState.errors.name.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" {...form.register("email")} />
              {form.formState.errors.email && (
                <p className="text-sm text-destructive">{form.formState.errors.email.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="role">Role</Label>
              <Input id="role" {...form.register("role")} />
              {form.formState.errors.role && (
                <p className="text-sm text-destructive">{form.formState.errors.role.message}</p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="accountCreated">Account Created</Label>
              <Input id="accountCreated" type="date" {...form.register("accountCreated")} />
              {form.formState.errors.accountCreated && (
                <p className="text-sm text-destructive">{form.formState.errors.accountCreated.message}</p>
              )}
            </div>
          </div>

          <div className="flex flex-col-reverse gap-3 sm:flex-row sm:justify-end">
            <Button type="button" variant="outline" className="gap-2">
              <KeyRound className="h-4 w-4" />
              Change Password
            </Button>
            <Button type="button" variant="outline" className="gap-2">
              <LogOut className="h-4 w-4" />
              Sign Out
            </Button>
            <Button type="submit" disabled={form.formState.isSubmitting || !form.formState.isDirty} className="gap-2">
              <Save className="h-4 w-4" />
              {form.formState.isSubmitting ? "Saving..." : "Save Account Settings"}
            </Button>
          </div>
        </form>

        <div className="rounded-xl border border-destructive/20 bg-destructive/5 p-4">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="flex items-center gap-2 text-base font-semibold text-destructive">
                <ShieldAlert className="h-4 w-4" />
                Delete Account
              </h3>
              <p className="mt-2 text-sm text-muted-foreground">
                Deleting your account permanently removes your InventIQ account and associated data.
              </p>
            </div>
            <DeleteAccountDialog />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
