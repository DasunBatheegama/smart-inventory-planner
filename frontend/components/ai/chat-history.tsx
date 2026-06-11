"use client";

import { cn } from "@/lib/utils";
import { Conversation } from "@/types/chat";
import { Button } from "@/components/ui/button";
import { MessageSquare, Plus, Pencil, Trash2 } from "lucide-react";
import { useState } from "react";

interface ChatHistoryProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onRename: (id: string, title: string) => void;
  onDelete: (id: string) => void;
}

export function ChatHistory({
  conversations,
  activeId,
  onSelect,
  onNew,
  onRename,
  onDelete,
}: ChatHistoryProps) {
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");

  const handleRename = (id: string) => {
    if (editValue.trim()) {
      onRename(id, editValue.trim());
    }
    setEditingId(null);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (diffDays === 0) return "Today";
    if (diffDays === 1) return "Yesterday";
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  };

  return (
    <div className="flex flex-col h-full">
      <div className="p-3 border-b">
        <Button onClick={onNew} className="w-full justify-start gap-2" size="sm">
          <Plus className="h-4 w-4" />
          New Chat
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto">
        {conversations.length === 0 ? (
          <div className="p-4 text-center text-sm text-muted-foreground">
            No conversations yet
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {conversations.map((conv) => (
              <div
                key={conv.id}
                className={cn(
                  "group relative rounded-lg p-3 cursor-pointer transition-colors",
                  activeId === conv.id
                    ? "bg-accent"
                    : "hover:bg-muted/50"
                )}
                onClick={() => onSelect(conv.id)}
              >
                {editingId === conv.id ? (
                  <div className="flex gap-1">
                    <input
                      className="flex h-7 w-full rounded border border-input bg-background px-2 text-xs"
                      value={editValue}
                      onChange={(e) => setEditValue(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === "Enter") handleRename(conv.id);
                        if (e.key === "Escape") setEditingId(null);
                      }}
                      onBlur={() => handleRename(conv.id)}
                      autoFocus
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                ) : (
                  <>
                    <div className="flex items-start gap-2">
                      <MessageSquare className="h-4 w-4 mt-0.5 shrink-0 text-muted-foreground" />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium truncate">
                          {conv.title}
                        </p>
                        {conv.lastMessage && (
                          <p className="text-xs text-muted-foreground truncate mt-0.5">
                            {conv.lastMessage}
                          </p>
                        )}
                        <p className="text-xs text-muted-foreground/60 mt-1">
                          {formatDate(conv.updatedAt)}
                        </p>
                      </div>
                    </div>

                    <div className="absolute right-2 top-2 hidden group-hover:flex gap-0.5">
                      <button
                        className="flex h-6 w-6 items-center justify-center rounded hover:bg-muted"
                        onClick={(e) => {
                          e.stopPropagation();
                          setEditingId(conv.id);
                          setEditValue(conv.title);
                        }}
                      >
                        <Pencil className="h-3 w-3 text-muted-foreground" />
                      </button>
                      <button
                        className="flex h-6 w-6 items-center justify-center rounded hover:bg-destructive/10"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDelete(conv.id);
                        }}
                      >
                        <Trash2 className="h-3 w-3 text-destructive" />
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
