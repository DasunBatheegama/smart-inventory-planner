import {
  Conversation,
  ChatMessage,
  AiMetrics,
  InventorySummary,
  AiRecommendation,
} from "@/types/chat";
import {
  mockConversations,
  mockAiMetrics,
  mockInventorySummary,
  mockAiRecommendations,
  mockQuickResponses,
} from "@/data/mock-chat";

class AiService {
  private conversations: Conversation[] = [...mockConversations];

  async getConversations(): Promise<Conversation[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...this.conversations]), 300)
    );
  }

  async getConversation(id: string): Promise<Conversation | undefined> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const conv = this.conversations.find((c) => c.id === id);
        resolve(conv ? { ...conv, messages: [...conv.messages] } : undefined);
      }, 200)
    );
  }

  async createConversation(title?: string): Promise<Conversation> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const conv: Conversation = {
          id: `conv-${Date.now()}`,
          title: title || "New Conversation",
          lastMessage: "",
          updatedAt: new Date().toISOString(),
          messages: [],
        };
        this.conversations.unshift(conv);
        resolve({ ...conv });
      }, 300)
    );
  }

  async deleteConversation(id: string): Promise<void> {
    return new Promise((resolve) =>
      setTimeout(() => {
        this.conversations = this.conversations.filter((c) => c.id !== id);
        resolve();
      }, 200)
    );
  }

  async renameConversation(id: string, title: string): Promise<void> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const conv = this.conversations.find((c) => c.id === id);
        if (conv) conv.title = title;
        resolve();
      }, 200)
    );
  }

  async sendMessage(
    conversationId: string,
    content: string
  ): Promise<{ userMessage: ChatMessage; aiResponse: ChatMessage }> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const conv = this.conversations.find((c) => c.id === conversationId);
        if (!conv) {
          resolve({ userMessage: {} as ChatMessage, aiResponse: {} as ChatMessage });
          return;
        }

        const userMsg: ChatMessage = {
          id: `msg-${Date.now()}-user`,
          role: "user",
          content,
          createdAt: new Date().toISOString(),
        };

        const lower = content.toLowerCase();
        let matched = mockQuickResponses.find((r) =>
          r.keywords.some((k) => lower.includes(k))
        );
        let aiContent = matched
          ? matched.response
          : `I've analyzed your inventory data based on your question: "${content}"

Here's what I found:

- Your inventory currently has **12 products** tracked across 3 categories and 3 suppliers.
- There are **14 active alerts** including 5 critical items requiring immediate attention.
- The overall **inventory health score** is **72%** (Good).

Would you like me to:
1. Show which products need reordering?
2. Explain current forecast accuracy?
3. Summarize active alerts?
4. Identify inventory risks?

Just ask!`;

        const aiMsg: ChatMessage = {
          id: `msg-${Date.now()}-ai`,
          role: "assistant",
          content: aiContent,
          createdAt: new Date().toISOString(),
        };

        conv.messages.push(userMsg, aiMsg);
        conv.lastMessage = aiContent.slice(0, 80) + "...";
        conv.updatedAt = new Date().toISOString();
        if (
          conv.title === "New Conversation" &&
          content.length < 50
        ) {
          conv.title = content.slice(0, 40);
        }

        resolve({ userMessage: userMsg, aiResponse: aiMsg });
      }, 1000)
    );
  }

  async getAiMetrics(): Promise<AiMetrics> {
    return new Promise((resolve) =>
      setTimeout(() => resolve({ ...mockAiMetrics }), 300)
    );
  }

  async getInventorySummary(): Promise<InventorySummary> {
    return new Promise((resolve) =>
      setTimeout(() => resolve({ ...mockInventorySummary }), 300)
    );
  }

  async getAiRecommendations(): Promise<AiRecommendation[]> {
    return new Promise((resolve) =>
      setTimeout(() => resolve([...mockAiRecommendations]), 300)
    );
  }

  async exportConversation(conversationId: string): Promise<string> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const conv = this.conversations.find((c) => c.id === conversationId);
        if (!conv) {
          resolve("No conversation found.");
          return;
        }
        const lines = conv.messages.map(
          (m) => `[${m.role.toUpperCase()}] ${m.content}`
        );
        resolve(
          `# ${conv.title}\n\nExported: ${new Date().toISOString()}\n\n${lines.join("\n\n")}`
        );
      }, 400)
    );
  }

  async clearConversation(conversationId: string): Promise<void> {
    return new Promise((resolve) =>
      setTimeout(() => {
        const conv = this.conversations.find((c) => c.id === conversationId);
        if (conv) {
          conv.messages = [];
          conv.lastMessage = "";
        }
        resolve();
      }, 200)
    );
  }
}

export const aiService = new AiService();
