"use client";

import { Button } from "@/components/ui/button";
import {
  PackageX,
  BarChart3,
  ShoppingCart,
  AlertTriangle,
  Bell,
} from "lucide-react";

interface SuggestedPromptsProps {
  onSelect: (prompt: string) => void;
  disabled?: boolean;
}

const prompts = [
  { label: "Show low stock products", icon: PackageX },
  { label: "Explain forecast accuracy", icon: BarChart3 },
  { label: "Generate purchase recommendations", icon: ShoppingCart },
  { label: "Show inventory risks", icon: AlertTriangle },
  { label: "Summarize active alerts", icon: Bell },
];

export function SuggestedPrompts({
  onSelect,
  disabled,
}: SuggestedPromptsProps) {
  return (
    <div className="flex flex-wrap gap-2 px-4 pb-2">
      {prompts.map((p) => (
        <Button
          key={p.label}
          variant="outline"
          size="sm"
          className="text-xs gap-1.5"
          onClick={() => onSelect(p.label)}
          disabled={disabled}
        >
          <p.icon className="h-3.5 w-3.5" />
          {p.label}
        </Button>
      ))}
    </div>
  );
}
