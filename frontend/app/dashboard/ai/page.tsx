"use client";

import { useCallback, useRef, useState } from "react";
import { ChatWindow } from "@/components/ai/chat-window";
import { ChatInput } from "@/components/ai/chat-input";
import { ChatError } from "@/components/ai/chat-error";
import { SuggestedPrompts } from "@/components/ai/suggested-prompts";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { aiService, AiServiceError } from "@/services/ai.service";
import type { ChatMessage } from "@/types/chat";
import { Bot, MessageSquarePlus } from "lucide-react";

const FALLBACK_ERROR =
  "Something went wrong while contacting the AI service. Please try again.";

export default function AiAssistantPage() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const lastRequestRef = useRef<string | null>(null);

  const handleNewChat = useCallback(() => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    lastRequestRef.current = null;
  }, []);

  const handleSendMessage = useCallback(
    async (content: string) => {
      const trimmed = content.trim();
      if (!trimmed || isSending) return;

      lastRequestRef.current = trimmed;
      setIsSending(true);
      setError(null);

      const userMessage: ChatMessage = {
        id: `user-${Date.now()}`,
        role: "user",
        content: trimmed,
        createdAt: new Date().toISOString(),
      };
      setMessages((previous) => [...previous, userMessage]);

      try {
        const response = await aiService.sendChatMessage(
          trimmed,
          conversationId ?? undefined
        );
        setConversationId(response.conversation_id);
        setMessages((previous) => [
          ...previous,
          {
            id: `assistant-${Date.now()}`,
            role: "assistant",
            content: response.answer,
            createdAt: new Date().toISOString(),
            agentsUsed: response.agents_used,
            recommendations: response.recommendations,
          },
        ]);
      } catch (caught) {
        setError(
          caught instanceof AiServiceError ? caught.message : FALLBACK_ERROR
        );
      } finally {
        setIsSending(false);
      }
    },
    [conversationId, isSending]
  );

  const handleRetry = useCallback(() => {
    const previousQuestion = lastRequestRef.current;
    if (!previousQuestion) return;
    setMessages((previous) => {
      if (previous.length === 0) return previous;
      const last = previous[previous.length - 1];
      return last.role === "user" ? previous.slice(0, -1) : previous;
    });
    void handleSendMessage(previousQuestion);
  }, [handleSendMessage]);

  const handlePromptSelect = useCallback(
    (prompt: string) => {
      void handleSendMessage(prompt);
    },
    [handleSendMessage]
  );

  return (
    <div className="flex h-[calc(100vh-8rem)] flex-1 flex-col">
      <div className="flex shrink-0 flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            AI Inventory Copilot
          </h2>
          <p className="mt-1 text-muted-foreground">
            Ask questions about inventory, forecasts, planning, and stock risks.
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={handleNewChat}
          disabled={messages.length === 0 && !isSending}
        >
          <MessageSquarePlus className="mr-2 h-4 w-4" />
          New Chat
        </Button>
      </div>

      <div className="mt-6 flex min-h-0 flex-1 flex-col overflow-hidden rounded-xl border border-border bg-background shadow-sm">
        <div className="flex shrink-0 items-center gap-2 border-b px-4 py-3">
          <Bot className="h-5 w-5 text-primary" />
          <h3 className="text-sm font-semibold">AI Inventory Copilot</h3>
        </div>

        <ChatWindow messages={messages} isLoading={isSending} />

        {messages.length === 0 && !isSending && (
          <SuggestedPrompts
            onSelect={handlePromptSelect}
            disabled={isSending}
          />
        )}

        {error && (
          <ChatError
            message={error}
            onRetry={handleRetry}
            onDismiss={() => setError(null)}
          />
        )}

        <Separator />

        <ChatInput onSend={handleSendMessage} disabled={isSending} />
      </div>
    </div>
  );
}
