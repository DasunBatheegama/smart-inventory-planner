const DEFAULT_API_BASE_URL = "http://localhost:8000";

export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? DEFAULT_API_BASE_URL
).replace(/\/+$/, "");

export const API_ENDPOINTS = {
  chat: "/api/v1/agents/chat",
} as const;

export const CHAT_REQUEST_TIMEOUT_MS = 30_000;
