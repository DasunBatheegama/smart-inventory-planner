import { SalesRecord, UploadHistory, ValidationError, ValidationResult } from "@/types/sales";
import { mockUploadHistory } from "@/data/mock-upload-history";

class SalesService {
  private uploadHistory: UploadHistory[] = [...mockUploadHistory];

  async getUploadHistory(): Promise<UploadHistory[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...this.uploadHistory]), 300)
    );
  }

  async uploadSalesFile(
    _file: File,
    records: SalesRecord[]
  ): Promise<UploadHistory> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const entry: UploadHistory = {
          id: `upl-${Math.random().toString(36).substring(7)}`,
          fileName: _file.name,
          uploadDate: new Date().toISOString(),
          recordsImported: records.length,
          status: "success",
        };
        this.uploadHistory.unshift(entry);
        resolve(entry);
      }, 400)
    );
  }

  async deleteUpload(id: string): Promise<boolean> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const len = this.uploadHistory.length;
        this.uploadHistory = this.uploadHistory.filter((u) => u.id !== id);
        resolve(this.uploadHistory.length < len);
      }, 300)
    );
  }

  validateSalesData(records: SalesRecord[]): ValidationResult {
    const errors: ValidationError[] = [];
    const validRecords: SalesRecord[] = [];

    for (let i = 0; i < records.length; i++) {
      const record = records[i];
      const rowErrors: string[] = [];

      if (!record.date || record.date.trim() === "") {
        rowErrors.push("Date is missing");
      } else if (isNaN(Date.parse(record.date))) {
        rowErrors.push("Invalid date format");
      }

      if (!record.sku || record.sku.trim() === "") {
        rowErrors.push("SKU is missing");
      }

      if (record.quantitySold == null || record.quantitySold < 0) {
        rowErrors.push("Quantity Sold cannot be negative or empty");
      }

      if (rowErrors.length > 0) {
        rowErrors.forEach((msg) => {
          errors.push({ row: i + 1, field: "multiple", message: msg });
        });
      } else {
        validRecords.push(record);
      }
    }

    const seen = new Set<string>();
    const duplicateWarnings: ValidationError[] = [];
    for (const r of validRecords) {
      const key = `${r.date}|${r.sku}`;
      if (seen.has(key)) {
        duplicateWarnings.push({
          row: 0,
          field: "duplicate",
          message: `Duplicate record: ${r.sku} on ${r.date}`,
        });
      }
      seen.add(key);
    }

    return {
      validRecords,
      invalidRecords: errors,
      totalRecords: records.length,
      validCount: validRecords.length,
      invalidCount: errors.length,
    };
  }
}

export const salesService = new SalesService();
