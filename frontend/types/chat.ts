export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  createdAt: string;
  agentsUsed?: string[];
  recommendations?: string[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: string;
  product_id?: string;
}

export interface ChatResponse {
  conversation_id: string;
  answer: string;
  agents_used: string[];
  supporting_data: Record<string, unknown> | null;
  recommendations: string[];
}
