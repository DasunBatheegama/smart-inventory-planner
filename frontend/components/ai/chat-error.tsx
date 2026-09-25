"use client";

import { Button } from "@/components/ui/button";
import { AlertCircle, RotateCw, X } from "lucide-react";

interface ChatErrorProps {
  message: string;
  onRetry?: () => void;
  onDismiss: () => void;
}

export function ChatError({ message, onRetry, onDismiss }: ChatErrorProps) {
  return (
    <div className="mx-4 mb-3 flex items-start gap-3 rounded-lg border border-destructive/40 bg-destructive/10 px-4 py-3">
      <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-destructive" />
      <p className="flex-1 text-sm text-destructive">{message}</p>
      <div className="flex shrink-0 items-center gap-1">
        {onRetry && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onRetry}
            className="h-7 gap-1.5 text-destructive hover:text-destructive"
          >
            <RotateCw className="h-3.5 w-3.5" />
            Retry
          </Button>
        )}
        <Button
          variant="ghost"
          size="icon-sm"
          onClick={onDismiss}
          aria-label="Dismiss error"
          className="h-7 w-7 text-destructive hover:text-destructive"
        >
          <X className="h-3.5 w-3.5" />
        </Button>
      </div>
    </div>
  );
}
