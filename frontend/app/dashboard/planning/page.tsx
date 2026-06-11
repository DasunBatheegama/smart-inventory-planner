"use client";

import { useEffect, useState, useMemo } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/dashboard/stat-card";
import { InventoryFilters } from "@/components/inventory/inventory-filters";
import { InventoryChart } from "@/components/inventory/inventory-chart";
import { InventoryHealth } from "@/components/inventory/inventory-health";
import { InventoryMetrics } from "@/components/inventory/inventory-metrics";
import { InventoryTable } from "@/components/inventory/inventory-table";
import { InventoryRisk } from "@/components/inventory/inventory-risk";
import { InventoryRecommendations } from "@/components/inventory/inventory-recommendations";
import { PurchasePlanning } from "@/components/inventory/purchase-planning";
import { inventoryService } from "@/services/inventory.service";
import {
  InventoryPlanItem,
  InventoryMetrics as Metrics,
  InventoryHealth as Health,
  RiskProduct,
  Recommendation,
  PurchasePlan,
  TrendDataPoint,
  InventoryFilters as Filters,
} from "@/types/inventory";
import {
  mockProducts,
  mockCategories,
  mockSuppliers,
  mockStatuses,
} from "@/data/mock-inventory";
import {
  DollarSign,
  Package,
  HeartPulse,
  CalendarDays,
  Calculator,
  Download,
  RefreshCw,
  ShoppingCart,
  Info,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const defaultFilters: Filters = {
  product: "all",
  category: "All Categories",
  supplier: "All Suppliers",
  status: "all",
};

export default function InventoryPlanningPage() {
  const [filters, setFilters] = useState<Filters>(defaultFilters);
  const [planItems, setPlanItems] = useState<InventoryPlanItem[]>([]);
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [health, setHealth] = useState<Health | null>(null);
  const [riskProducts, setRiskProducts] = useState<RiskProduct[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [purchasePlans, setPurchasePlans] = useState<PurchasePlan[]>([]);
  const [trendData, setTrendData] = useState<TrendDataPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [hasForecast] = useState(true);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [plan, met, h, risk, rec, purch, trend] = await Promise.all([
        inventoryService.calculateInventoryPlan(filters),
        inventoryService.getInventoryMetrics(),
        inventoryService.getInventoryHealth(),
        inventoryService.getRiskProducts(),
        inventoryService.getRecommendations(),
        inventoryService.getPurchasePlans(),
        inventoryService.getTrendData(),
      ]);
      setPlanItems(plan);
      setMetrics(met);
      setHealth(h);
      setRiskProducts(risk);
      setRecommendations(rec);
      setPurchasePlans(purch);
      setTrendData(trend);
    } catch (error) {
      console.error("Failed to load inventory plan:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const recalculate = async () => {
    setLoading(true);
    try {
      const plan = await inventoryService.calculateInventoryPlan(filters);
      setPlanItems(plan);
      const met = await inventoryService.getInventoryMetrics();
      setMetrics(met);
    } catch (error) {
      console.error("Failed to recalculate:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const csv = await inventoryService.exportPlan();
      const blob = new Blob([csv], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "inventory-plan.csv";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to export plan:", error);
    } finally {
      setExporting(false);
    }
  };

  const stockoutRisks = useMemo(
    () => riskProducts.filter((r) => r.riskType === "stockout"),
    [riskProducts]
  );
  const overstockRisks = useMemo(
    () => riskProducts.filter((r) => r.riskType === "overstock"),
    [riskProducts]
  );
  const slowMovingRisks = useMemo(
    () => riskProducts.filter((r) => r.riskType === "slow-moving"),
    [riskProducts]
  );

  if (!hasForecast) {
    return (
      <div className="flex-1 space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            Inventory Planning
          </h2>
          <p className="text-muted-foreground mt-2">
            Optimize inventory levels and purchasing decisions using
            forecast-driven planning.
          </p>
        </div>
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed p-16 text-center">
          <CalendarDays className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-xl font-semibold">No Forecast Available</h3>
          <p className="text-muted-foreground mt-2 max-w-md">
            Generate a forecast before creating an inventory plan.
          </p>
          <Link
            href="/dashboard/forecasting"
            className="inline-flex items-center justify-center rounded-lg bg-primary text-primary-foreground text-sm font-medium h-8 gap-1.5 px-2.5 mt-6 hover:bg-primary/80 transition-all"
          >
            Go to Forecasting
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 space-y-6">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            Inventory Planning
          </h2>
          <p className="text-muted-foreground mt-1">
            Optimize inventory levels and purchasing decisions using
            forecast-driven planning.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={recalculate} disabled={loading}>
            <Calculator className="mr-2 h-4 w-4" />
            {loading ? "Calculating..." : "Recalculate"}
          </Button>
          <Button variant="outline" onClick={handleExport} disabled={exporting}>
            <Download className="mr-2 h-4 w-4" />
            {exporting ? "Exporting..." : "Export Plan"}
          </Button>
          <Button
            variant="outline"
            onClick={() => {
              setFilters(defaultFilters);
              loadAll();
            }}
            disabled={loading}
          >
            <ShoppingCart className="mr-2 h-4 w-4" />
            Purchase Recommendations
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

      {/* Forecast Dependency Notice */}
      <Card className="border-blue-500/20 bg-blue-500/5">
        <CardContent className="flex items-start gap-3 py-4">
          <Info className="h-5 w-5 text-blue-500 shrink-0 mt-0.5" />
          <p className="text-sm text-blue-700 dark:text-blue-300">
            Inventory recommendations are generated using forecast demand.
            Ensure forecasts are up-to-date for accurate planning.
          </p>
        </CardContent>
      </Card>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Inventory Value"
          value={
            metrics
              ? `$${metrics.totalInventoryValue.toLocaleString()}`
              : "—"
          }
          trend="+3.2%"
          trendUp={true}
          icon={DollarSign}
        />
        <StatCard
          title="Products Requiring Reorder"
          value={metrics ? String(metrics.productsRequiringReorder) : "—"}
          trend={metrics && metrics.productsRequiringReorder > 4 ? "+High" : "Low"}
          trendUp={metrics ? metrics.productsRequiringReorder > 4 : false}
          icon={Package}
        />
        <StatCard
          title="Inventory Health Score"
          value={metrics ? `${metrics.healthScore}%` : "—"}
          trend={metrics && metrics.healthScore >= 70 ? "+Good" : "+Fair"}
          trendUp={metrics ? metrics.healthScore >= 70 : true}
          icon={HeartPulse}
        />
        <StatCard
          title="Days of Inventory Remaining"
          value={metrics ? String(metrics.daysOfInventoryRemaining) : "—"}
          trend={metrics && metrics.daysOfInventoryRemaining > 30 ? "+Adequate" : "-Low"}
          trendUp={metrics ? metrics.daysOfInventoryRemaining > 30 : true}
          icon={CalendarDays}
        />
      </div>

      {/* Filters */}
      <div className="bg-background rounded-xl border border-border shadow-sm p-4 sm:p-6">
        <InventoryFilters
          products={mockProducts}
          categories={mockCategories}
          suppliers={mockSuppliers}
          statuses={mockStatuses}
          filters={filters}
          onFiltersChange={setFilters}
        />
      </div>

      {/* Health + Chart */}
      <div className="grid gap-4 lg:grid-cols-3">
        {health && (
          <div className="lg:col-span-1">
            <InventoryHealth data={health} />
          </div>
        )}
        <div className="lg:col-span-2 bg-background rounded-xl border border-border shadow-sm p-4 sm:p-6">
          <h3 className="text-lg font-semibold mb-4">
            Inventory & Demand Trend
          </h3>
          {loading ? (
            <div className="h-[320px] flex items-center justify-center text-muted-foreground">
              Loading trend data...
            </div>
          ) : (
            <InventoryChart data={trendData} />
          )}
        </div>
      </div>

      {/* Metrics Dashboard */}
      <div className="bg-background rounded-xl border border-border shadow-sm p-4 sm:p-6">
        <h3 className="text-lg font-semibold mb-4">
          Inventory Metrics Dashboard
        </h3>
        {loading ? (
          <div className="h-24 flex items-center justify-center text-muted-foreground">
            Loading metrics...
          </div>
        ) : (
          <InventoryMetrics items={planItems} />
        )}
      </div>

      {/* Risk + Recommendations + Purchase Planning */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <InventoryRisk
          stockout={stockoutRisks}
          overstock={overstockRisks}
          slowMoving={slowMovingRisks}
        />
        <InventoryRecommendations data={recommendations} />
        <PurchasePlanning data={purchasePlans} />
      </div>

      {/* Table */}
      <div className="bg-background rounded-xl border border-border shadow-sm p-4 sm:p-6">
        <h3 className="text-lg font-semibold mb-4">Inventory Planning Table</h3>
        {loading ? (
          <div className="h-48 flex items-center justify-center text-muted-foreground">
            Loading inventory data...
          </div>
        ) : (
          <InventoryTable data={planItems} />
        )}
      </div>
    </div>
  );
}
