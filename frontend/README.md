# InventIQ · Frontend

Next.js 16 (Turbopack) + React 19 + TypeScript + Tailwind CSS v4 + shadcn/ui.

The AI-assistant chatbot lives at [/dashboard/ai](http://localhost:3000/dashboard/ai)
and talks to the FastAPI backend at `http://localhost:8000`.

## Routes

| Route                  | Module                                            |
| ---------------------- | ------------------------------------------------- |
| `/dashboard`           | Overview                                          |
| `/dashboard/ai`        | AI inventory assistant (chat)                     |
| `/dashboard/alerts`    | Generated alerts                                  |
| `/dashboard/forecasting` | Forecasts                                        |
| `/dashboard/planning`  | Reorder planning                                  |
| `/dashboard/products`  | Product catalog                                   |
| `/dashboard/sales-upload` | Sales CSV upload                               |
| `/dashboard/settings`  | Settings                                          |

## Getting started

```bash
npm install
npm run dev      # http://localhost:3000
```

The backend must be running on `:8000` (see the repository root README). The API
base URL is resolved in `lib/api-config.ts`:

- `NEXT_PUBLIC_API_BASE_URL` if set (static, inlined at build time), else
  `http://localhost:8000`.

## AI assistant architecture

```
Chat UI (app/dashboard/ai/page.tsx)
  └─ aiService.sendChatMessage()        services/ai.service.ts (typed HTTP +
                                          error mapping, 30s timeout)
       └─ POST {base}/api/v1/agents/chat
            → ChatService → AIOrchestrator → forecast/inventory/insight agent
            → deterministic services → PostgreSQL → structured JSON
```

- `types/chat.ts` — `ChatMessage`, `ChatRequest`, `ChatResponse` contracts.
- `lib/api-config.ts` — base URL + chat endpoint and request timeout.
- `services/ai.service.ts` — HTTP client; every provider/backend status maps to
  a client-authored friendly message (`STATUS_ERRORS`), so raw backend or LLM
  error text never reaches the UI.
- `components/ai/*` — chat window, message bubbles (`agent-indicator`,
  recommendations), suggested prompts, and the error banner with retry.

### Interaction notes

- Each turn may invoke one or more agents; the UI shows `agents_used` as badges
  on the assistant message.
- Repeating the same `conversation_id` across turns enables context.
- Suggested prompts are written to match the backend's keyword router (see the
  root README routing table).

## Checks

```bash
npm run lint     # eslint; 11 pre-existing errors / 23 warnings, none in AI-stage files
npm run build    # production build (clean, TypeScript passes)
```

## Configuration

| Variable                    | Purpose                          | Default                |
| --------------------------- | -------------------------------- | ---------------------- |
| `NEXT_PUBLIC_API_BASE_URL`  | Backend base URL for API calls   | `http://localhost:8000`|

The frontend holds no API keys; the LLM provider key is backend-only.