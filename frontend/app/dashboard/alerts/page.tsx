"use client";

import { useEffect, useState, useMemo } from "react";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/dashboard/stat-card";
import { AlertsFilters } from "@/components/alerts/alerts-filters";
import { AlertCard } from "@/components/alerts/alert-card";
import { CriticalAlerts } from "@/components/alerts/critical-alerts";
import { RiskSummary } from "@/components/alerts/risk-summary";
import { Recommendations } from "@/components/alerts/recommendations";
import { AlertTimeline } from "@/components/alerts/alert-timeline";
import { AlertsTable } from "@/components/alerts/alerts-table";
import { alertService } from "@/services/alert.service";
import {
  Alert,
  AlertMetrics,
  AlertCategoryData,
  Recommendation,
  AlertFilters as Filters,
} from "@/types/alert";
import {
  mockProducts,
  mockSuppliers,
  mockAlertTypes,
  mockSeverities,
  mockDateRanges,
} from "@/data/mock-alerts";
import {
  Bell,
  AlertTriangle,
  ShoppingCart,
  Layers,
  CheckCheck,
  Download,
  RefreshCw,
} from "lucide-react";

const defaultFilters: Filters = {
  type: "all",
  severity: "all",
  product: "all",
  supplier: "All Suppliers",
  dateRange: "all",
  search: "",
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [metrics, setMetrics] = useState<AlertMetrics | null>(null);
  const [categoryData, setCategoryData] = useState<AlertCategoryData[]>([]);
  const [severityData, setSeverityData] = useState<AlertCategoryData[]>([]);
  const [timeline, setTimeline] = useState<Alert[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [hasAlerts] = useState(true);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [alertList, met, catData, sevData, tl, recs] =
        await Promise.all([
          alertService.getAlerts(filters),
          alertService.getAlertMetrics(),
          alertService.getAlertCategoryData(),
          alertService.getAlertSeverityData(),
          alertService.getAlertTimeline(),
          alertService.getRecommendations(),
        ]);
      setAlerts(alertList);
      setMetrics(met);
      setCategoryData(catData);
      setSeverityData(sevData);
      setTimeline(tl);
      setRecommendations(recs);
    } catch (error) {
      console.error("Failed to load alerts:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  useEffect(() => {
    const timer = setTimeout(() => {
      alertService.getAlerts(filters).then(setAlerts);
    }, 200);
    return () => clearTimeout(timer);
  }, [filters]);

  const handleMarkAllRead = async () => {
    await alertService.markAllAsRead();
    loadAll();
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const csv = await alertService.exportAlerts();
      const blob = new Blob([csv], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "alerts-export.csv";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to export alerts:", error);
    } finally {
      setExporting(false);
    }
  };

  const handleMarkRead = async (id: string) => {
    await alertService.markAsRead(id);
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id ? { ...a, status: "acknowledged" as const } : a
      )
    );
  };

  const handleResolve = async (id: string) => {
    await alertService.resolveAlert(id);
    setAlerts((prev) =>
      prev.map((a) =>
        a.id === id ? { ...a, status: "resolved" as const } : a
      )
    );
  };

  const activeAlerts = useMemo(
    () => alerts.filter((a) => a.status !== "resolved"),
    [alerts]
  );
  const criticalAlerts = useMemo(
    () => alerts.filter((a) => a.status !== "resolved"),
    [alerts]
  );

  if (!hasAlerts) {
    return (
      <div className="flex-1 space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Alerts Center</h2>
          <p className="text-muted-foreground mt-2">
            Monitor inventory risks and take action before problems impact operations.
          </p>
        </div>
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed p-16 text-center">
          <Bell className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-xl font-semibold">No Active Alerts</h3>
          <p className="text-muted-foreground mt-2 max-w-md">
            Your inventory is healthy.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Alerts Center</h2>
          <p className="text-muted-foreground mt-1">
            Monitor inventory risks and take action before problems impact operations.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            onClick={handleMarkAllRead}
            disabled={loading}
          >
            <CheckCheck className="mr-2 h-4 w-4" />
            Mark All Read
          </Button>
          <Button variant="outline" onClick={handleExport} disabled={exporting}>
            <Download className="mr-2 h-4 w-4" />
            {exporting ? "Exporting..." : "Export Alerts"}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            onClick={loadAll}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Active Alerts"
          value={metrics ? String(metrics.totalActive) : "—"}
          trend={metrics && metrics.totalActive > 10 ? "+High" : "Low"}
          trendUp={metrics ? metrics.totalActive > 10 : true}
          icon={Bell}
        />
        <StatCard
          title="Critical Alerts"
          value={metrics ? String(metrics.criticalCount) : "—"}
          trend={metrics && metrics.criticalCount > 3 ? "+Urgent" : "Low"}
          trendUp={metrics ? metrics.criticalCount > 3 : false}
          icon={AlertTriangle}
        />
        <StatCard
          title="Reorder Required"
          value={metrics ? String(metrics.reorderRequired) : "—"}
          trend={metrics && metrics.reorderRequired > 2 ? "+Action" : "Low"}
          trendUp={metrics ? metrics.reorderRequired > 2 : false}
          icon={ShoppingCart}
        />
        <StatCard
          title="Overstock Warnings"
          value={metrics ? String(metrics.overstockWarnings) : "—"}
          trend={metrics && metrics.overstockWarnings > 2 ? "+Watch" : "Low"}
          trendUp={metrics ? metrics.overstockWarnings > 2 : true}
          icon={Layers}
        />
      </div>

      {/* Filters */}
      <div className="bg-background rounded-xl border border-border shadow-sm p-4 sm:p-6">
        <AlertsFilters
          products={mockProducts}
          suppliers={mockSuppliers}
          alertTypes={mockAlertTypes}
          severities={mockSeverities}
          dateRanges={mockDateRanges}
          filters={filters}
          onFiltersChange={setFilters}
        />
      </div>

      {/* Alert Feed + Critical Alerts */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 space-y-3">
          <h3 className="text-lg font-semibold">
            Alert Feed
            {activeAlerts.length > 0 && (
              <span className="text-sm font-normal text-muted-foreground ml-2">
                ({activeAlerts.length} active)
              </span>
            )}
          </h3>
          {loading ? (
            <div className="h-48 flex items-center justify-center text-muted-foreground">
              Loading alerts...
            </div>
          ) : activeAlerts.length === 0 ? (
            <div className="rounded-xl border border-dashed p-12 text-center">
              <Bell className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">No active alerts match your filters.</p>
            </div>
          ) : (
            activeAlerts.map((alert) => (
              <AlertCard
                key={alert.id}
                alert={alert}
                onMarkRead={handleMarkRead}
                onResolve={handleResolve}
              />
            ))
          )}
        </div>
        <div className="space-y-4">
          <CriticalAlerts alerts={alerts} />
        </div>
      </div>

      {/* Risk Summary + Timeline + Recommendations */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <RiskSummary categoryData={categoryData} severityData={severityData} />
        <AlertTimeline alerts={timeline} />
        <Recommendations data={recommendations} />
      </div>

      {/* Alerts Table */}
      <div className="bg-background rounded-xl border border-border shadow-sm p-4 sm:p-6">
        <h3 className="text-lg font-semibold mb-4">All Alerts</h3>
        {loading ? (
          <div className="h-48 flex items-center justify-center text-muted-foreground">
            Loading alerts...
          </div>
        ) : (
          <AlertsTable
            data={alerts}
            onMarkRead={handleMarkRead}
            onResolve={handleResolve}
          />
        )}
      </div>
    </div>
  );
}
