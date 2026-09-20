"use client";

import * as React from "react";
import { Bell, BriefcaseBusiness, BrushCleaning, Database, Palette, Settings2, SlidersHorizontal, UserRound } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { SettingsSection, SettingsSectionKey } from "@/types/settings";

const sections: SettingsSection[] = [
  { id: "general", label: "General" },
  { id: "inventory", label: "Inventory Planning" },
  { id: "forecasting", label: "Forecasting" },
  { id: "notifications", label: "Notifications" },
  { id: "appearance", label: "Appearance" },
  { id: "account", label: "Account" },
];

const icons: Record<SettingsSectionKey, React.ComponentType<{ className?: string }>> = {
  general: Settings2,
  inventory: Database,
  forecasting: SlidersHorizontal,
  notifications: Bell,
  appearance: Palette,
  account: UserRound,
};

interface SettingsSidebarProps {
  activeSection: SettingsSectionKey;
  onSelect: (section: SettingsSectionKey) => void;
}

export function SettingsSidebar({ activeSection, onSelect }: SettingsSidebarProps) {
  return (
    <Card className="h-fit overflow-hidden p-2">
      <div className="space-y-2">
        {sections.map((section) => {
          const Icon = icons[section.id];
          const isActive = activeSection === section.id;

          return (
            <Button
              key={section.id}
              type="button"
              variant={isActive ? "secondary" : "ghost"}
              className={cn(
                "w-full justify-start gap-3 rounded-lg px-3 py-2.5 text-left font-medium",
                isActive && "bg-muted text-foreground shadow-sm",
              )}
              onClick={() => onSelect(section.id)}
            >
              <Icon className="h-4 w-4" />
              <span>{section.label}</span>
            </Button>
          );
        })}
      </div>
    </Card>
  );
}
