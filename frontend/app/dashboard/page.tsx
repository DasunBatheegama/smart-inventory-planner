import * as React from "react";
import { kpiData } from "@/data/mock-dashboard";
import { StatCard } from "@/components/dashboard/stat-card";
import { QuickActions } from "@/components/dashboard/quick-actions";
import { InventoryHealth } from "@/components/dashboard/inventory-health";
import { RecentAlerts } from "@/components/dashboard/recent-alerts";
import { ForecastSummary } from "@/components/dashboard/forecast-summary";
import { RecentActivity } from "@/components/dashboard/recent-activity";

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold tracking-tight">Overview</h2>
        <p className="text-muted-foreground mt-2">
          Your inventory pulse and recent planning insights.
        </p>
      </div>
      
      {/* KPI Section */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {kpiData.map((kpi, i) => (
          <StatCard key={i} {...kpi} />
        ))}
      </div>

      {/* Widgets Section 1 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <QuickActions />
        <InventoryHealth />
        <ForecastSummary />
      </div>

      {/* Widgets Section 2 */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <RecentAlerts />
        {/* Placeholder to balance grid out, or make Alerts span 2 cols */}
      </div>

      {/* Recent Activity */}
      <div className="grid gap-4">
        <RecentActivity />
      </div>
    </div>
  );
}