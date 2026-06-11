export interface SalesRecord {
  date: string;
  sku: string;
  quantitySold: number;
}

export interface UploadHistory {
  id: string;
  fileName: string;
  uploadDate: string;
  recordsImported: number;
  status: "success" | "failed" | "processing";
}

export interface ValidationError {
  row: number;
  field: string;
  message: string;
}

export interface ValidationResult {
  validRecords: SalesRecord[];
  invalidRecords: ValidationError[];
  totalRecords: number;
  validCount: number;
  invalidCount: number;
}

export interface SalesStats {
  totalUploads: number;
  totalRecords: number;
  lastUploadDate: string | null;
  forecastReady: boolean;
}

export interface ForecastReadiness {
  daysAvailable: number;
  productsCovered: number;
  missingDataWarnings: number;
  score: number;
  recommendations: string[];
}
