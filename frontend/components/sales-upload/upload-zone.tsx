"use client";

import { useState, useRef, useCallback } from "react";
import { Upload, FileText, AlertCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  selectedFile: File | null;
}

export function UploadZone({ onFileSelect, disabled, selectedFile }: UploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file && (file.name.endsWith(".csv") || file.name.endsWith(".xlsx"))) {
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelect(file);
  };

  return (
    <div
      data-slot="upload-zone"
      className={cn(
        "flex flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 text-center transition-colors",
        isDragOver
          ? "border-primary bg-primary/5"
          : "border-border hover:border-muted-foreground/40",
        disabled && "pointer-events-none opacity-50"
      )}
      onDragOver={(e) => { e.preventDefault(); setIsDragOver(true); }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
    >
      {selectedFile ? (
        <>
          <FileText className="mb-3 h-10 w-10 text-primary" />
          <p className="mb-1 text-sm font-medium">{selectedFile.name}</p>
          <p className="text-xs text-muted-foreground">
            {(selectedFile.size / 1024).toFixed(1)} KB
          </p>
          <Button
            variant="outline"
            size="sm"
            className="mt-4"
            onClick={() => {
              inputRef.current?.click();
            }}
          >
            Choose Different File
          </Button>
        </>
      ) : (
        <>
          <Upload className="mb-3 h-10 w-10 text-muted-foreground" />
          <p className="mb-1 text-sm font-medium">
            Drag & drop your file here
          </p>
          <p className="mb-4 text-xs text-muted-foreground">
            or click to browse
          </p>
          <Button
            variant="outline"
            size="sm"
            onClick={() => inputRef.current?.click()}
          >
            Browse Files
          </Button>
        </>
      )}
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx"
        className="hidden"
        onChange={handleChange}
      />
      <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
        <span className="inline-flex items-center gap-1">
          <FileText className="h-3.5 w-3.5" /> CSV
        </span>
        <span className="inline-flex items-center gap-1">
          <FileText className="h-3.5 w-3.5" /> XLSX
          <span className="ml-0.5 rounded bg-muted px-1 py-0.5 text-[10px] font-medium text-muted-foreground">
            soon
          </span>
        </span>
        <span className="inline-flex items-center gap-1">
          <AlertCircle className="h-3.5 w-3.5" /> Max: 10MB
        </span>
      </div>
      <p className="mt-2 text-xs text-muted-foreground">
        File must contain Date, SKU, and Quantity Sold columns
      </p>
    </div>
  );
}
