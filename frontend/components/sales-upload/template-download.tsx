"use client";

import { FileDown } from "lucide-react";
import { Button } from "@/components/ui/button";

const sampleCsvContent = `Date,SKU,Quantity Sold
2025-01-01,SKU-1001,25
2025-01-02,SKU-1002,18
2025-01-03,SKU-1001,12
2025-01-04,SKU-1003,30
2025-01-05,SKU-1002,22`;

export function TemplateDownload() {
  const handleDownload = () => {
    const blob = new Blob([sampleCsvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "sales_upload_template.csv";
    link.click();
    URL.revokeObjectURL(url);
  };

  return (
    <Button variant="outline" size="sm" onClick={handleDownload}>
      <FileDown className="mr-1.5 h-4 w-4" />
      Download Template
    </Button>
  );
}
