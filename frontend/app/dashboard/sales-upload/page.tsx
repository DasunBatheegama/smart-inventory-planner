"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import Papa from "papaparse";
import { Upload, Database, CalendarClock, BrainCircuit, UploadIcon } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatCard } from "@/components/dashboard/stat-card";
import { UploadZone } from "@/components/sales-upload/upload-zone";
import { TemplateDownload } from "@/components/sales-upload/template-download";
import { ValidationSummary } from "@/components/sales-upload/validation-summary";
import { UploadPreview } from "@/components/sales-upload/upload-preview";
import { UploadHistoryTable } from "@/components/sales-upload/upload-history";
import { ForecastReadinessWidget } from "@/components/sales-upload/forecast-readiness";
import { Separator } from "@/components/ui/separator";
import { salesService } from "@/services/sales.service";
import { SalesRecord, UploadHistory, ValidationResult, ForecastReadiness, SalesStats } from "@/types/sales";
import { mockSalesRecords } from "@/data/mock-sales";

function computeStats(history: UploadHistory[]): SalesStats {
  const totalUploads = history.length;
  const totalRecords = history.reduce((sum, h) => sum + h.recordsImported, 0);
  const successful = history.filter((h) => h.status === "success");
  const lastUpload = successful.length > 0 ? successful[0].uploadDate : null;
  const forecastReady = successful.length >= 3;
  return { totalUploads, totalRecords, lastUploadDate: lastUpload, forecastReady };
}

function computeForecastReadiness(history: UploadHistory[], latestRecords: SalesRecord[]): ForecastReadiness {
  const successfulUploads = history.filter((h) => h.status === "success");
  if (successfulUploads.length === 0 && latestRecords.length === 0) {
    return { daysAvailable: 0, productsCovered: 0, missingDataWarnings: 0, score: 0, recommendations: ["Upload at least 3 months of sales data for better forecast accuracy."] };
  }
  const records = latestRecords.length > 0 ? latestRecords : mockSalesRecords;
  const uniqueDates = new Set(records.map((r) => r.date));
  const uniqueSkus = new Set(records.map((r) => r.sku));
  const daysAvailable = uniqueDates.size;
  const productsCovered = uniqueSkus.size;
  const missingDataWarnings = Math.max(0, 90 - daysAvailable);
  const score = Math.min(100, Math.round((daysAvailable / 90) * 50 + (productsCovered / 5) * 30 + (successfulUploads.length >= 3 ? 20 : 0)));
  const recommendations: string[] = [];
  if (daysAvailable < 90) recommendations.push("Upload at least 3 months of sales data for better forecast accuracy.");
  if (productsCovered < 5) recommendations.push("Include more SKUs to improve demand prediction coverage.");
  if (missingDataWarnings > 0) recommendations.push("Consider filling in missing date ranges for continuous forecasting.");
  return { daysAvailable, productsCovered, missingDataWarnings, score, recommendations };
}

export default function SalesUploadPage() {
  const [uploadHistory, setUploadHistory] = useState<UploadHistory[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [parsedRecords, setParsedRecords] = useState<SalesRecord[]>([]);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);
  const [importStep, setImportStep] = useState<"idle" | "parsing" | "validated" | "importing" | "done">("idle");
  const [isImporting, setIsImporting] = useState(false);
  const [latestRecords, setLatestRecords] = useState<SalesRecord[]>([]);

  const loadHistory = useCallback(async () => {
    setLoading(true);
    try {
      const data = await salesService.getUploadHistory();
      setUploadHistory(data);
    } catch (err) {
      console.error("Failed to load upload history:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  const stats = useMemo(() => computeStats(uploadHistory), [uploadHistory]);
  const forecastReadiness = useMemo(() => computeForecastReadiness(uploadHistory, latestRecords), [uploadHistory, latestRecords]);

  const handleFileSelect = (file: File) => {
    setSelectedFile(file);
    setImportStep("parsing");
    setValidationResult(null);
    setParsedRecords([]);

    if (!file.name.endsWith(".csv")) {
      setImportStep("idle");
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      const csv = e.target?.result as string;
      const result = Papa.parse<Record<string, string>>(csv, { header: true, skipEmptyLines: true });
      const headers = result.meta.fields || [];

      if (!headers.includes("Date") || !headers.includes("SKU") || !headers.includes("Quantity Sold")) {
        setValidationResult({
          validRecords: [],
          invalidRecords: [{ row: 0, field: "columns", message: "Missing required columns. Expected: Date, SKU, Quantity Sold" }],
          totalRecords: 0,
          validCount: 0,
          invalidCount: 1,
        });
        setImportStep("validated");
        return;
      }

      const records: SalesRecord[] = result.data
        .filter((row) => row.Date && row.SKU && row["Quantity Sold"])
        .map((row) => ({
          date: row.Date.trim(),
          sku: row.SKU.trim(),
          quantitySold: parseInt(row["Quantity Sold"], 10),
        }));

      const validation = salesService.validateSalesData(records);
      setParsedRecords(records);
      setValidationResult(validation);
      setImportStep("validated");
    };
    reader.readAsText(file);
  };

  const handleImport = async () => {
    if (!selectedFile || !validationResult) return;
    setIsImporting(true);
    try {
      const entry = await salesService.uploadSalesFile(selectedFile, validationResult.validRecords);
      setUploadHistory((prev) => [entry, ...prev]);
      setLatestRecords((prev) => [...validationResult.validRecords, ...prev].slice(0, 100));
      setImportStep("done");
      setSelectedFile(null);
      setParsedRecords([]);
      setValidationResult(null);
    } catch (err) {
      console.error("Import failed:", err);
    } finally {
      setIsImporting(false);
    }
  };

  const handleCancel = () => {
    setSelectedFile(null);
    setParsedRecords([]);
    setValidationResult(null);
    setImportStep("idle");
  };

  const handleDelete = async (id: string) => {
    await salesService.deleteUpload(id);
    setUploadHistory((prev) => prev.filter((u) => u.id !== id));
  };

  const handleViewDetails = (id: string) => {
    const entry = uploadHistory.find((u) => u.id === id);
    if (entry) {
      alert(`Upload Details:\n\nFile: ${entry.fileName}\nDate: ${new Date(entry.uploadDate).toLocaleString()}\nRecords: ${entry.recordsImported}\nStatus: ${entry.status}`);
    }
  };

  const hasUploads = uploadHistory.length > 0;

  return (
    <div className="flex-1 space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">Sales Data Upload</h2>
          <p className="text-muted-foreground mt-1">
            Upload historical sales data to generate demand forecasts and inventory recommendations
          </p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Uploads"
          value={String(stats.totalUploads)}
          trend={stats.totalUploads > 0 ? `${stats.totalUploads} file(s)` : "No uploads"}
          trendUp={stats.totalUploads > 0}
          icon={Upload}
        />
        <StatCard
          title="Total Sales Records"
          value={String(stats.totalRecords)}
          trend={stats.totalRecords > 0 ? `${stats.totalRecords} entries` : "No data"}
          trendUp={stats.totalRecords > 0}
          icon={Database}
        />
        <StatCard
          title="Last Upload Date"
          value={stats.lastUploadDate ? new Date(stats.lastUploadDate).toLocaleDateString() : "N/A"}
          trend={stats.lastUploadDate ? new Date(stats.lastUploadDate).toLocaleDateString("en-US", { month: "short", day: "numeric" }) : "Never"}
          trendUp={!!stats.lastUploadDate}
          icon={CalendarClock}
        />
        <StatCard
          title="Forecast Ready"
          value={stats.forecastReady ? "Ready" : "Not Ready"}
          trend={stats.forecastReady ? "3+ uploads" : "Need more data"}
          trendUp={stats.forecastReady}
          icon={BrainCircuit}
        />
      </div>

      {!hasUploads && importStep === "idle" ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-16">
            <UploadIcon className="mb-4 h-16 w-16 text-muted-foreground/40" />
            <p className="text-lg font-medium text-foreground mb-1">
              Upload your first sales file to start forecasting demand.
            </p>
            <p className="text-sm text-muted-foreground mb-6 max-w-md text-center">
              Drag and drop a CSV file below to get started with demand forecasting and inventory planning.
            </p>
            <UploadZone onFileSelect={handleFileSelect} selectedFile={selectedFile} />
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="space-y-4">
            <UploadZone
              onFileSelect={handleFileSelect}
              disabled={importStep === "parsing" || importStep === "importing"}
              selectedFile={selectedFile}
            />
          </div>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Example Upload Format</CardTitle>
              <TemplateDownload />
            </CardHeader>
            <CardContent>
              <p className="mb-3 text-xs text-muted-foreground">
                Your CSV file must include these columns:
              </p>
              <div className="rounded-lg border bg-muted/30 overflow-x-auto">
                <table className="w-full text-xs">
                  <thead>
                    <tr className="border-b bg-muted/50">
                      <th className="px-3 py-2 text-left font-medium text-muted-foreground">Date</th>
                      <th className="px-3 py-2 text-left font-medium text-muted-foreground">SKU</th>
                      <th className="px-3 py-2 text-left font-medium text-muted-foreground">Quantity Sold</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr className="border-b"><td className="px-3 py-1.5">2025-01-01</td><td className="px-3 py-1.5">SKU-1001</td><td className="px-3 py-1.5">25</td></tr>
                    <tr className="border-b"><td className="px-3 py-1.5">2025-01-02</td><td className="px-3 py-1.5">SKU-1002</td><td className="px-3 py-1.5">18</td></tr>
                    <tr className="border-b"><td className="px-3 py-1.5">2025-01-03</td><td className="px-3 py-1.5">SKU-1001</td><td className="px-3 py-1.5">12</td></tr>
                    <tr><td className="px-3 py-1.5">2025-01-04</td><td className="px-3 py-1.5">SKU-1003</td><td className="px-3 py-1.5">30</td></tr>
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {validationResult && importStep === "validated" && (
        <div className="space-y-6">
          <ValidationSummary
            validCount={validationResult.validCount}
            invalidCount={validationResult.invalidCount}
            status={validationResult.invalidCount > 0 ? "invalid" : "valid"}
            onImport={handleImport}
            onCancel={handleCancel}
            isImporting={isImporting}
          />
          <UploadPreview records={parsedRecords} />
        </div>
      )}

      {importStep === "importing" && (
        <ValidationSummary
          validCount={validationResult?.validCount ?? 0}
          invalidCount={validationResult?.invalidCount ?? 0}
          status="validating"
          onImport={() => {}}
          onCancel={() => {}}
          isImporting
        />
      )}

      <Separator />

      {hasUploads && (
        <div className="space-y-6">
          <div>
            <h3 className="text-xl font-semibold tracking-tight">Upload History</h3>
            <p className="text-sm text-muted-foreground mt-0.5">View and manage your past sales data uploads</p>
          </div>
          {loading ? (
            <div className="h-32 flex items-center justify-center text-muted-foreground">Loading history...</div>
          ) : (
            <UploadHistoryTable
              data={uploadHistory}
              onViewDetails={handleViewDetails}
              onDelete={handleDelete}
            />
          )}
        </div>
      )}

      {hasUploads && (
        <ForecastReadinessWidget data={forecastReadiness} />
      )}
    </div>
  );
}
