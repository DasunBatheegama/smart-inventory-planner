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
  {
    label: "Which products need reordering right now?",
    icon: PackageX,
  },
  {
    label: "Which products are at risk of running out?",
    icon: AlertTriangle,
  },
  { label: "Explain the demand forecast for my products", icon: BarChart3 },
  {
    label: "Generate purchase recommendations for the next month",
    icon: ShoppingCart,
  },
  { label: "Summarize the biggest risks in my inventory", icon: Bell },
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
