"use client";

import { useEffect, useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { Separator } from "@/components/ui/separator";
import { StatCard } from "@/components/dashboard/stat-card";
import { ChatWindow } from "@/components/ai/chat-window";
import { ChatInput } from "@/components/ai/chat-input";
import { ChatHistory } from "@/components/ai/chat-history";
import { SuggestedPrompts } from "@/components/ai/suggested-prompts";
import { AiInsights } from "@/components/ai/ai-insights";
import { InventoryContext } from "@/components/ai/inventory-context";
import { aiService } from "@/services/ai.service";
import {
  Conversation,
  ChatMessage,
  AiMetrics,
  InventorySummary,
  AiRecommendation,
} from "@/types/chat";
import {
  Bot,
  MessageSquarePlus,
  Trash2,
  Download,
  RefreshCw,
} from "lucide-react";

export default function AiAssistantPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [metrics, setMetrics] = useState<AiMetrics | null>(null);
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [recommendations, setRecommendations] = useState<AiRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [isAiThinking, setIsAiThinking] = useState(false);

  const loadSidebar = useCallback(async () => {
    try {
      const [convos, met, summ, recs] = await Promise.all([
        aiService.getConversations(),
        aiService.getAiMetrics(),
        aiService.getInventorySummary(),
        aiService.getAiRecommendations(),
      ]);
      setConversations(convos);
      setMetrics(met);
      setSummary(summ);
      setRecommendations(recs);
    } catch (error) {
      console.error("Failed to load AI data:", error);
    }
  }, []);

  useEffect(() => {
    loadSidebar();
  }, [loadSidebar]);

  useEffect(() => {
    if (activeId) {
      aiService.getConversation(activeId).then((conv) => {
        if (conv) setMessages(conv.messages);
      });
    } else {
      setMessages([]);
    }
  }, [activeId]);

  const handleNewChat = async () => {
    const conv = await aiService.createConversation();
    setConversations((prev) => [conv, ...prev]);
    setActiveId(conv.id);
    setMessages([]);
  };

  const handleDeleteConversation = async (id: string) => {
    await aiService.deleteConversation(id);
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeId === id) {
      setActiveId(null);
      setMessages([]);
    }
  };

  const handleRenameConversation = async (id: string, title: string) => {
    await aiService.renameConversation(id, title);
    setConversations((prev) =>
      prev.map((c) => (c.id === id ? { ...c, title } : c))
    );
  };

  const handleSendMessage = async (content: string) => {
    if (!activeId) {
      const conv = await aiService.createConversation(
        content.slice(0, 40)
      );
      setConversations((prev) => [conv, ...prev]);
      setActiveId(conv.id);
    }

    const cId = activeId || conversations[0]?.id;
    if (!cId) return;

    setIsAiThinking(true);
    try {
      const { userMessage, aiResponse } = await aiService.sendMessage(
        cId,
        content
      );
      setMessages((prev) => [...prev, userMessage, aiResponse]);
      setConversations((prev) =>
        prev.map((c) =>
          c.id === cId
            ? {
                ...c,
                lastMessage: aiResponse.content.slice(0, 80) + "...",
                updatedAt: new Date().toISOString(),
              }
            : c
        )
      );
    } finally {
      setIsAiThinking(false);
    }
  };

  const handleSelectConversation = (id: string) => {
    setActiveId(id);
  };

  const handleClearConversation = async () => {
    if (!activeId) return;
    await aiService.clearConversation(activeId);
    setMessages([]);
  };

  const handleExportConversation = async () => {
    if (!activeId) return;
    const text = await aiService.exportConversation(activeId);
    const blob = new Blob([text], { type: "text/markdown" });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `chat-${activeId}.md`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handlePromptSelect = (prompt: string) => {
    handleSendMessage(prompt);
  };

  const activeConv = conversations.find((c) => c.id === activeId);

  return (
    <div className="flex-1 flex flex-col h-[calc(100vh-8rem)]">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 shrink-0">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">
            AI Inventory Copilot
          </h2>
          <p className="text-muted-foreground mt-1">
            Ask questions about inventory, forecasts, planning, and stock risks.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={handleNewChat}>
            <MessageSquarePlus className="mr-2 h-4 w-4" />
            New Chat
          </Button>
          {activeId && (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearConversation}
                disabled={messages.length === 0}
              >
                <Trash2 className="mr-2 h-4 w-4" />
                Clear
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleExportConversation}
                disabled={messages.length === 0}
              >
                <Download className="mr-2 h-4 w-4" />
                Export Chat
              </Button>
            </>
          )}
          <Button
            variant="ghost"
            size="icon-sm"
            onClick={loadSidebar}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 mt-6 shrink-0">
        <StatCard
          title="Total Products Analyzed"
          value={metrics ? String(metrics.totalProductsAnalyzed) : "—"}
          trend="+12"
          trendUp={true}
          icon={Bot}
        />
        <StatCard
          title="Active Alerts"
          value={metrics ? String(metrics.activeAlerts) : "—"}
          trend={metrics && metrics.activeAlerts > 10 ? "+High" : "Low"}
          trendUp={metrics ? metrics.activeAlerts > 10 : false}
          icon={Bot}
        />
        <StatCard
          title="Inventory Health Score"
          value={metrics ? `${metrics.inventoryHealthScore}%` : "—"}
          trend={metrics && metrics.inventoryHealthScore >= 70 ? "+Good" : "Fair"}
          trendUp={metrics ? metrics.inventoryHealthScore >= 70 : true}
          icon={Bot}
        />
        <StatCard
          title="Forecast Accuracy"
          value={metrics ? `${metrics.forecastAccuracy}%` : "—"}
          trend="+2.3%"
          trendUp={true}
          icon={Bot}
        />
      </div>

      {/* Main Chat Layout */}
      <div className="flex-1 flex gap-4 mt-6 min-h-0">
        {/* Left Panel - Chat History */}
        <div className="hidden lg:flex w-64 shrink-0 bg-background rounded-xl border border-border shadow-sm overflow-hidden">
          <ChatHistory
            conversations={conversations}
            activeId={activeId}
            onSelect={handleSelectConversation}
            onNew={handleNewChat}
            onRename={handleRenameConversation}
            onDelete={handleDeleteConversation}
          />
        </div>

        {/* Center Panel - Chat */}
        <div className="flex-1 flex flex-col bg-background rounded-xl border border-border shadow-sm overflow-hidden">
          {/* Conversation header */}
          <div className="px-4 py-3 border-b shrink-0">
            <div className="flex items-center gap-2">
              <Bot className="h-5 w-5 text-primary" />
              <h3 className="font-semibold text-sm">
                {activeConv?.title || "AI Inventory Copilot"}
              </h3>
            </div>
          </div>

          {/* Messages */}
          <ChatWindow messages={messages} isLoading={isAiThinking} />

          {/* Suggested Prompts */}
          {messages.length === 0 && !isAiThinking && (
            <SuggestedPrompts
              onSelect={handlePromptSelect}
              disabled={isAiThinking}
            />
          )}

          <Separator />
          {/* Input */}
          <ChatInput onSend={handleSendMessage} disabled={isAiThinking} />
        </div>

        {/* Right Panel - Insights */}
        <div className="hidden xl:flex w-64 shrink-0 overflow-y-auto">
          <div className="space-y-4 w-full">
            <AiInsights
              summary={summary}
              recommendations={recommendations}
            />
            <InventoryContext />
          </div>
        </div>
      </div>
    </div>
  );
}
