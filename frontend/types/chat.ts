export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: string;
}

export interface Conversation {
  id: string;
  title: string;
  lastMessage: string;
  updatedAt: string;
  messages: ChatMessage[];
}

export interface AiMetrics {
  totalProductsAnalyzed: number;
  activeAlerts: number;
  inventoryHealthScore: number;
  forecastAccuracy: number;
}

export interface InventorySummary {
  totalProducts: number;
  inventoryValue: number;
  activeAlerts: number;
  reorderRequired: number;
}

export interface AiRecommendation {
  id: string;
  sku: string;
  productName: string;
  action: string;
  daysUntilAction: number;
}
