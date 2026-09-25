import {
  API_BASE_URL,
  API_ENDPOINTS,
  CHAT_REQUEST_TIMEOUT_MS,
} from "@/lib/api-config";
import type { ChatRequest, ChatResponse } from "@/types/chat";

export type AiErrorKind =
  | "unavailable"
  | "timeout"
  | "not_configured"
  | "unroutable"
  | "invalid_request"
  | "agent_error"
  | "provider_error"
  | "invalid_response"
  | "unknown";

export class AiServiceError extends Error {
  readonly kind: AiErrorKind;
  readonly status?: number;

  constructor(kind: AiErrorKind, message: string, status?: number) {
    super(message);
    this.name = "AiServiceError";
    this.kind = kind;
    this.status = status;
  }
}

const STATUS_ERRORS: Record<number, { kind: AiErrorKind; message: string }> =
  {
    400: {
      kind: "invalid_request",
      message: "That request was not valid. Please rephrase your question.",
    },
    404: {
      kind: "unroutable",
      message:
        "No inventory agent could handle that question. Try asking about stock levels, demand forecasts, or purchase planning.",
    },
    422: {
      kind: "invalid_request",
      message: "Please enter a question of at least 3 characters.",
    },
    500: {
      kind: "agent_error",
      message:
        "The inventory agent hit an unexpected error. Please try again.",
    },
    502: {
      kind: "provider_error",
      message:
        "The AI provider is temporarily unavailable. Please try again shortly.",
    },
    503: {
      kind: "not_configured",
      message:
        "AI is not configured on the server. An administrator needs to set the LLM API key.",
    },
    504: {
      kind: "timeout",
      message: "The AI took too long to respond. Please try again.",
    },
  };

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === "string");
}

function isChatResponse(value: unknown): value is ChatResponse {
  if (!isRecord(value)) return false;
  if (typeof value.conversation_id !== "string") return false;
  if (typeof value.answer !== "string") return false;
  if (!isStringArray(value.agents_used)) return false;
  if (value.supporting_data !== null && !isRecord(value.supporting_data)) {
    return false;
  }
  if (value.recommendations !== undefined && !isStringArray(value.recommendations)) {
    return false;
  }
  return true;
}

async function postChat(payload: ChatRequest): Promise<ChatResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), CHAT_REQUEST_TIMEOUT_MS);

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${API_ENDPOINTS.chat}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
      signal: controller.signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw new AiServiceError(
        "timeout",
        "The request timed out before the server responded. Please try again."
      );
    }
    throw new AiServiceError(
      "unavailable",
      `Could not reach the InventIQ API at ${API_BASE_URL}. Make sure the backend is running.`
    );
  } finally {
    clearTimeout(timeout);
  }

  if (!response.ok) {
    const mapped = STATUS_ERRORS[response.status];
    if (mapped) {
      throw new AiServiceError(mapped.kind, mapped.message, response.status);
    }
    throw new AiServiceError(
      "unknown",
      `The server returned an unexpected error (${response.status}).`,
      response.status
    );
  }

  let body: unknown;
  try {
    body = await response.json();
  } catch {
    throw new AiServiceError(
      "invalid_response",
      "The server returned a response that could not be read as JSON."
    );
  }

  if (!isChatResponse(body)) {
    throw new AiServiceError(
      "invalid_response",
      "The server returned an unexpected response shape."
    );
  }

  return {
    conversation_id: body.conversation_id,
    answer: body.answer,
    agents_used: body.agents_used,
    supporting_data: body.supporting_data,
    recommendations: body.recommendations ?? [],
  };
}

export const aiService = {
  sendChatMessage(
    message: string,
    conversationId?: string,
    productId?: string
  ): Promise<ChatResponse> {
    const payload: ChatRequest = { message };
    if (conversationId) payload.conversation_id = conversationId;
    if (productId) payload.product_id = productId;
    return postChat(payload);
  },
};
