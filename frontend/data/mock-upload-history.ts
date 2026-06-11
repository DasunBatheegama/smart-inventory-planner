import { UploadHistory } from "@/types/sales";

export const mockUploadHistory: UploadHistory[] = [
  {
    id: "upl-001",
    fileName: "sales_january_2025.csv",
    uploadDate: "2025-02-01T10:30:00Z",
    recordsImported: 30,
    status: "success",
  },
  {
    id: "upl-002",
    fileName: "sales_february_2025.xlsx",
    uploadDate: "2025-03-01T14:15:00Z",
    recordsImported: 20,
    status: "success",
  },
  {
    id: "upl-003",
    fileName: "sales_march_2025.csv",
    uploadDate: "2025-04-02T09:45:00Z",
    recordsImported: 0,
    status: "failed",
  },
  {
    id: "upl-004",
    fileName: "sales_april_2025.csv",
    uploadDate: "2025-05-01T16:20:00Z",
    recordsImported: 28,
    status: "success",
  },
  {
    id: "upl-005",
    fileName: "sales_may_2025.csv",
    uploadDate: "2025-06-01T11:00:00Z",
    recordsImported: 25,
    status: "processing",
  },
];
