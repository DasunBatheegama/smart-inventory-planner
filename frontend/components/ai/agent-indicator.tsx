"use client";

import { Badge } from "@/components/ui/badge";
import { Cpu } from "lucide-react";

interface AgentIndicatorProps {
  agentsUsed?: string[];
}

function humanizeAgentName(agent: string): string {
  return agent.replace(/_/g, " ").replace(/\b\w/g, (char) => char.toUpperCase());
}

export function AgentIndicator({ agentsUsed }: AgentIndicatorProps) {
  if (!agentsUsed || agentsUsed.length === 0) return null;

  return (
    <div className="mt-3 flex flex-wrap items-center gap-1.5 border-t pt-2">
      <Cpu className="h-3 w-3 text-muted-foreground" />
      <span className="text-xs text-muted-foreground">Agents used</span>
      {agentsUsed.map((agent) => (
        <Badge
          key={agent}
          variant="secondary"
          data-icon="inline-start"
          className="h-4 text-[10px]"
        >
          {humanizeAgentName(agent)}
        </Badge>
      ))}
    </div>
  );
}
