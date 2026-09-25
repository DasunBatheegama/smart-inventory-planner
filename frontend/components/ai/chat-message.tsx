"use client";

import * as React from "react";
import { cn } from "@/lib/utils";
import type { ChatMessage as ChatMessageType } from "@/types/chat";
import { Bot, User } from "lucide-react";
import { AgentIndicator } from "./agent-indicator";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";

interface ChatMessageProps {
  message: ChatMessageType;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={cn(
        "flex gap-3 py-4",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {!isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary/10">
          <Bot className="h-4 w-4 text-primary" />
        </div>
      )}

      <div
        className={cn(
          "max-w-[80%] rounded-xl px-4 py-3",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-muted/50 border"
        )}
      >
        {isUser ? (
          <p className="text-sm whitespace-pre-wrap">{message.content}</p>
        ) : (
          <div className="space-y-3">
            <div className="text-sm">
              <FormattedContent content={message.content} />
            </div>
            {message.recommendations && message.recommendations.length > 0 && (
              <div className="rounded-lg border bg-background/60 p-3">
                <p className="mb-2 text-xs font-semibold text-muted-foreground">
                  Recommendations
                </p>
                <ul className="ml-4 space-y-1.5 list-disc">
                  {message.recommendations.map((recommendation, index) => (
                    <li key={index} className="text-sm">
                      {renderInline(recommendation)}
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <AgentIndicator agentsUsed={message.agentsUsed} />
          </div>
        )}
        <p
          className={cn(
            "text-xs mt-2",
            isUser
              ? "text-primary-foreground/60"
              : "text-muted-foreground"
          )}
        >
          {new Date(message.createdAt).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>

      {isUser && (
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary">
          <User className="h-4 w-4 text-primary-foreground" />
        </div>
      )}
    </div>
  );
}

function FormattedContent({ content }: { content: string }) {
  const lines = content.split("\n");
  const elements: React.ReactElement[] = [];
  let inTable = false;
  let tableRows: string[][] = [];
  let tableHeaders: string[] = [];

  const flushTable = () => {
    if (tableRows.length === 0) return;
    const hasHeader = tableHeaders.length > 0;
    const rows = hasHeader ? tableRows.slice(1) : tableRows;
    elements.push(
      <div key={`table-${elements.length}`} className="my-2 overflow-x-auto">
        <Table>
          {hasHeader && (
            <TableHeader>
              <TableRow>
                {tableHeaders.map((h, i) => (
                  <TableHead key={i}>{h.trim()}</TableHead>
                ))}
              </TableRow>
            </TableHeader>
          )}
          <TableBody>
            {rows.map((row, ri) => (
              <TableRow key={ri}>
                {row.map((cell, ci) => (
                  <TableCell key={ci}>{cell.trim()}</TableCell>
                ))}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    );
    tableRows = [];
    tableHeaders = [];
    inTable = false;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();

    if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
      const cells = trimmed.split("|").filter((c) => c.trim());
      if (!inTable) {
        inTable = true;
        tableRows = [];
        tableHeaders = cells;
        tableRows.push(cells);
      } else {
        const isSeparator = cells.every((c) => /^[-:]+$/.test(c.trim()));
        if (!isSeparator) {
          tableRows.push(cells);
        }
      }
      continue;
    } else {
      if (inTable) flushTable();
    }

    if (trimmed === "") {
      elements.push(<div key={`empty-${i}`} className="h-2" />);
      continue;
    }

    if (trimmed.startsWith("## ")) {
      elements.push(
        <h3 key={i} className="text-base font-semibold mt-3 mb-1">
          {renderInline(trimmed.slice(3))}
        </h3>
      );
      continue;
    }

    if (trimmed.startsWith("**") && trimmed.endsWith("**") && !trimmed.includes("|")) {
      elements.push(
        <p key={i} className="font-semibold text-sm mt-2">
          {renderInline(trimmed.replace(/\*\*/g, ""))}
        </p>
      );
      continue;
    }

    if (trimmed.startsWith("- ")) {
      if (
        elements.length > 0 &&
        elements[elements.length - 1].type === "ul"
      ) {
          const prev = elements.pop() as React.ReactElement;
          const children = [...(prev.props as { children: React.ReactElement[] }).children];
        children.push(
          <li key={children.length} className="text-sm ml-4 list-disc">
            {renderInline(trimmed.slice(2))}
          </li>
        );
        elements.push(<ul key={`ul-${i}`}>{children}</ul>);
      } else {
        elements.push(
          <ul key={`ul-${i}`}>
            <li className="text-sm ml-4 list-disc">
              {renderInline(trimmed.slice(2))}
            </li>
          </ul>
        );
      }
      continue;
    }

    if (
      trimmed.startsWith("1. ") ||
      trimmed.startsWith("2. ") ||
      trimmed.startsWith("3. ")
    ) {
      elements.push(
        <p key={i} className="text-sm ml-4">
          {renderInline(trimmed)}
        </p>
      );
      continue;
    }

    elements.push(
      <p key={i} className="text-sm">
        {renderInline(trimmed)}
      </p>
    );
  }

  if (inTable) flushTable();

  return <div className="space-y-1">{elements}</div>;
}

function renderInline(text: string): React.ReactNode {
  const parts: React.ReactNode[] = [];
  let remaining = text;
  let key = 0;

  while (remaining.length > 0) {
    const boldStart = remaining.indexOf("**");
    if (boldStart === -1) {
      parts.push(<span key={key++}>{remaining}</span>);
      break;
    }

    parts.push(<span key={key++}>{remaining.slice(0, boldStart)}</span>);
    remaining = remaining.slice(boldStart + 2);
    const boldEnd = remaining.indexOf("**");
    if (boldEnd === -1) {
      parts.push(<strong key={key++}>{remaining}</strong>);
      break;
    }

    parts.push(<strong key={key++}>{remaining.slice(0, boldEnd)}</strong>);
    remaining = remaining.slice(boldEnd + 2);
  }

  return parts.length > 0 ? <>{parts}</> : text;
}
