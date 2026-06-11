"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { StatCard } from "@/components/dashboard/stat-card";
import { ForecastControls } from "@/components/forecasting/forecast-controls";
import { ForecastChart } from "@/components/forecasting/forecast-chart";
import { ForecastSummary } from "@/components/forecasting/forecast-summary";
import { ForecastAccuracy } from "@/components/forecasting/forecast-accuracy";
import { GrowthProducts } from "@/components/forecasting/growth-products";
import { RiskProducts } from "@/components/forecasting/risk-products";
import { ForecastTable } from "@/components/forecasting/forecast-table";
import { forecastService } from "@/services/forecast.service";
import {
  ForecastData,
  ForecastResult,
  GrowthProduct,
  RiskProduct,
  ForecastAccuracy as Accuracy,
  ForecastSummary as Summary,
  ForecastControls as Controls,
} from "@/types/forecast";
import {
  mockProducts,
  mockCategories,
} from "@/data/mock-forecast";
import { Target, CalendarDays, Clock, ShieldCheck, Wand2, Download, RefreshCw } from "lucide-react";

const defaultControls: Controls = {
  productId: "prod-1",
  category: "all",
  horizon: 6,
  method: "exponential-smoothing",
};

export default function ForecastingPage() {
  const [controls, setControls] = useState<Controls>(defaultControls);
  const [historical, setHistorical] = useState<ForecastData[]>([]);
  const [projection, setProjection] = useState<ForecastData[]>([]);
  const [results, setResults] = useState<ForecastResult[]>([]);
  const [accuracy, setAccuracy] = useState<Accuracy | null>(null);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [growthProducts, setGrowthProducts] = useState<GrowthProduct[]>([]);
  const [riskProducts, setRiskProducts] = useState<RiskProduct[]>([]);
  const [loading, setLoading] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [hasData] = useState(true);

  const loadAll = async () => {
    setLoading(true);
    try {
      const [forecast, res, acc, summ, growth, risk] = await Promise.all([
        forecastService.generateForecast(controls),
        forecastService.getForecastResults(),
        forecastService.getForecastAccuracy(),
        forecastService.getForecastSummary(),
        forecastService.getGrowthProducts(),
        forecastService.getRiskProducts(),
      ]);
      setHistorical(forecast.historical);
      setProjection(forecast.projection);
      setResults(res);
      setAccuracy(acc);
      setSummary(summ);
      setGrowthProducts(growth);
      setRiskProducts(risk);
    } catch (error) {
      console.error("Failed to load forecast data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadAll();
  }, []);

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const forecast = await forecastService.generateForecast(controls);
      setHistorical(forecast.historical);
      setProjection(forecast.projection);
      const res = await forecastService.getForecastResults();
      setResults(res);
    } catch (error) {
      console.error("Failed to generate forecast:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const csv = await forecastService.exportForecast();
      const blob = new Blob([csv], { type: "text/csv" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "forecast-export.csv";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Failed to export forecast:", error);
    } finally {
      setExporting(false);
    }
  };

  if (!hasData) {
    return (
      <div className="flex-1 space-y-6">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Demand Forecasting</h2>
          <p className="text-muted-foreground mt-2">Analyze historical demand and predict future inventory requirements.</p>
        </div>
        <div className="flex flex-col items-center justify-center rounded-xl border border-dashed p-16 text-center">
          <CalendarDays className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-xl font-semibold">No Sales Data Available</h3>
          <p className="text-muted-foreground mt-2 max-w-md">
            Upload sales history before generating forecasts.
          </p>
          <Link
            href="/dashboard/sales-upload"
            className="inline-flex items-center justify-center rounded-lg bg-primary text-primary-foreground text-sm font-medium h-8 gap-1.5 px-2.5 mt-6 hover:bg-primary/80 transition-all"
          >
            Upload Sales Data
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
          <h2 className="text-3xl font-bold tracking-tight">Demand Forecasting</h2>
          <p className="text-muted-foreground mt-1">
            Analyze historical demand and predict future inventory requirements.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={handleGenerate} disabled={loading}>
            <Wand2 className="mr-2 h-4 w-4" />
            {loading ? "Generating..." : "Generate Forecast"}
          </Button>
          <Button variant="outline" onClick={handleExport} disabled={exporting}>
            <Download className="mr-2 h-4 w-4" />
            {exporting ? "Exporting..." : "Export Forecast"}
          </Button>
          <Button variant="ghost" size="icon" onClick={loadAll} disabled={loading}>
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Forecast Accuracy"
          value={accuracy ? `${accuracy.confidenceScore}%` : "—"}
          trend="+2.3%"
          trendUp={true}
          icon={Target}
        />
        <StatCard
          title="Next Month Demand"
          value={summary ? `${summary.forecastedDemand.toLocaleString()} units` : "—"}
          trend="+10.3%"
          trendUp={true}
          icon={CalendarDays}
        />
        <StatCard
          title="Forecast Horizon"
          value={`${controls.horizon} Months`}
          trend="—"
          trendUp={true}
          icon={Clock}
        />
        <StatCard
          title="Forecast Confidence"
          value={accuracy ? `${accuracy.confidenceScore}%` : "—"}
          trend={accuracy && accuracy.confidenceScore >= 80 ? "+High" : "Moderate"}
          trendUp={accuracy ? accuracy.confidenceScore >= 80 : true}
          icon={ShieldCheck}
        />
      </div>

      {/* Forecast Controls */}
      <div className="bg-background rounded-xl border border-border shadow-sm p-4 sm:p-6">
        <ForecastControls
          products={mockProducts}
          categories={mockCategories}
          controls={controls}
          onControlsChange={setControls}
        />
      </div>

      {/* Main Chart + Summary */}
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2 bg-background rounded-xl border border-border shadow-sm p-4 sm:p-6">
          <h3 className="text-lg font-semibold mb-4">Forecast Visualization</h3>
          {loading ? (
            <div className="h-[400px] flex items-center justify-center text-muted-foreground">
              Generating forecast...
            </div>
          ) : (
            <ForecastChart historical={historical} projection={projection} />
          )}
        </div>
        <div>
          {summary && <ForecastSummary data={summary} />}
        </div>
      </div>

      {/* Accuracy + Growth + Risk */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {accuracy && <ForecastAccuracy data={accuracy} />}
        <GrowthProducts data={growthProducts} />
        <RiskProducts data={riskProducts} />
      </div>

      {/* Forecast Table */}
      <ForecastTable data={results} />
    </div>
  );
}
