import * as React from "react";
import { DashboardLayout } from "@/components/layout/dashboard-layout";
import { Metadata } from "next";

export const metadata: Metadata = {
  title: "Dashboard - InventIQ",
  description: "InventIQ Dashboard Management",
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <DashboardLayout>
      {children}
    </DashboardLayout>
  );
}