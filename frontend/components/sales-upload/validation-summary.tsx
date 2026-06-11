"use client";

import { CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

interface ValidationSummaryProps {
  validCount: number;
  invalidCount: number;
  status: "idle" | "validating" | "valid" | "invalid";
  onImport: () => void;
  onCancel: () => void;
  isImporting?: boolean;
}

export function ValidationSummary({
  validCount,
  invalidCount,
  status,
  onImport,
  onCancel,
  isImporting,
}: ValidationSummaryProps) {
  if (status === "idle") return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Import Summary</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap items-center gap-6">
          <div className="flex items-center gap-2">
            {status === "validating" ? (
              <Loader2 className="h-5 w-5 animate-spin text-muted-foreground" />
            ) : (
              <CheckCircle2 className="h-5 w-5 text-emerald-500" />
            )}
            <span className="text-sm">
              <strong className="text-foreground">{validCount}</strong>{" "}
              <span className="text-muted-foreground">Valid Records</span>
            </span>
          </div>

          <div className="flex items-center gap-2">
            {invalidCount > 0 ? (
              <AlertCircle className="h-5 w-5 text-rose-500" />
            ) : (
              <CheckCircle2 className="h-5 w-5 text-emerald-500" />
            )}
            <span className="text-sm">
              <strong className="text-foreground">{invalidCount}</strong>{" "}
              <span className="text-muted-foreground">Invalid Records</span>
            </span>
          </div>

          <Badge
            variant={
              status === "valid" || status === "validating"
                ? "secondary"
                : "destructive"
            }
          >
            {status === "validating"
              ? "Validating..."
              : status === "invalid"
              ? "Has Errors"
              : "Ready to Import"}
          </Badge>
        </div>

        <div className="mt-4 flex gap-3">
          <Button
            onClick={onImport}
            disabled={status !== "valid" || isImporting}
          >
            {isImporting ? (
              <>
                <Loader2 className="mr-1.5 h-4 w-4 animate-spin" />
                Importing...
              </>
            ) : (
              "Import Data"
            )}
          </Button>
          <Button variant="outline" onClick={onCancel} disabled={isImporting}>
            Cancel
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
