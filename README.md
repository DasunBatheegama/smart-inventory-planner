# InventIQ — Smart Inventory Planner

InventIQ is a full-stack inventory planning application with an AI assistant. It
combines deterministic forecasting, reorder planning, and alert generation with a
thin LLM layer that *explains* those results in natural language — it never
replaces them.

```
┌──────────────┐   HTTP/JSON    ┌───────────────────────────────────────────────────┐
│  Next.js 16   │ ────────────▶ │  FastAPI backend (:8000)                          │
│  app router   │ ◀──────────── │   POST /api/v1/agents/chat                        │
│  (:3000)      │               │       │                                           │
└──────────────┘               │       ▼                                           │
                               │  ChatService  ── ConversationStore (in-memory)     │
                               │       │                                           │
                               │       ▼                                           │
                               │  AIOrchestrator ── keyword routing                 │
                               │    │      │        │                              │
                               │    ▼      ▼        ▼                              │
                               │ forecast  inventory  insight  (3 allowlisted)      │
                               │  agent     agent      agent                       │
                               │    │         │         │                          │
                               │    ▼         ▼         ▼                          │
                               │  deterministic services: forecasting,            │
                               │  inventory planning, alert generation             │
                               │         │                                         │
                               │         ▼                                         │
                               │  PostgreSQL (inventiq)                             │
                               └───────────────────────────────────────────────────┘
                            ...
                       LLM provider (Groq, backend-only key)
```

The LLM is only ever fed a bounded, real snapshot of the database and is
instructed to *use only that data*. Every number it reports can be traced to a
stored record.

## Stack

| Layer   | Technology                                                                 |
| ------- | -------------------------------------------------------------------------- |
| Backend | Python 3.14, FastAPI, SQLAlchemy 2, Alembic, Pydantic v2, psycopg          |
| Frontend| Next.js 16 (Turbopack), React 19, TypeScript, Tailwind CSS v4, shadcn      |
| DB      | PostgreSQL (`inventiq`)                                                     |
| LLM     | Groq (`openai/gpt-oss-120b`, key stored backend-only in `Backend/.env`)     |

## Repository layout

```
Backend/
  app/api/routes/          HTTP endpoints (agents, products, forecasts, planning, alerts, sales)
  app/agents/              AIOrchestrator + forecast/inventory/insight agents + tools
  app/services/            deterministic planning/forecasting/alerts + ai (LLM, chat)
  app/schemas/             request/response contracts
  alembic/versions/        migrations (head: 0006_add_alerts_table)
  tests/                   pytest suite
frontend/
  app/dashboard/           page routes incl. /dashboard/ai (the AI assistant)
  components/              ui + feature components
  services/  types/  lib/  API clients, contracts, api-config
```

## Prerequisites

- Python 3.14+ and Node.js 20+ (repo tested with npm)
- PostgreSQL running on `localhost:5432`
- A Groq API key (free tier)

## Backend setup

```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate            # (Windows)  /  source .venv/bin/activate
pip install -r requirements.txt
```

Create `Backend/.env` (it is gitignored; see `Backend/.env.example`):

```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/inventiq
Groq_Api_Key=your_key_here
Groq_Model=openai/gpt-oss-120b
Groq_Timeout_Seconds=30
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

Apply migrations and run:

```bash
alembic upgrade head
uvicorn app.main:app --reload        # http://127.0.0.1:8000
# health:  GET /api/v1/health  ->  {"status":"healthy"}
```

## Frontend setup

```bash
cd frontend
npm install
# optional: set NEXT_PUBLIC_API_BASE_URL (defaults to http://localhost:8000)
npm run dev                          # http://localhost:3000
```

API base URL comes from `frontend/lib/api-config.ts` (static
`NEXT_PUBLIC_API_BASE_URL` default `http://localhost:8000`, trailing slash
trimmed). The chat endpoint is `POST {base}/api/v1/agents/chat`.

## Tests and gates

```bash
# Backend (all green)
cd Backend && .venv\Scripts\python.exe -m pytest     # 166 passed, 0 failed

# Frontend
cd frontend && npm run lint && npm run build        # build clean; lint 11 pre-existing errors in untouched modules
```

## AI assistant

**Pipeline:** `Next.js (/dashboard/ai)` → `POST /api/v1/agents/chat` →
`ChatService` (conversation store) → `AIOrchestrator` (deterministic keyword
router, fails closed) → the matching agent → deterministic services →
PostgreSQL → structured JSON response.

**Routing table** (`Backend/app/agents/orchestrator.py`): a message is matched
against a keyword allowlist; zero matches ⇒ `404`, one or more ⇒ those agents
run. Unknown questions never reach the LLM.

| Agent            | Trigger keywords                                                       |
| ---------------- | ---------------------------------------------------------------------- |
| `forecast_agent` | forecast, demand, prediction, predict, sales trend, upcoming demand     |
| `inventory_agent`| reorder, safety stock, inventory, stock, stock level, on hand, in stock |
| `insight_agent`  | focus, prioritize, attention, this week, urgent, recommendation, insight|

**Chat contract** — `ChatRequest`: `message` (3–500 chars, trimmed),
`conversation_id` (optional UUID), `product_id` (optional). `ChatResponse`:
`conversation_id`, `answer`, `agents_used`, `supporting_data`,
`recommendations`. Conversation context is threaded via repeating the same
`conversation_id`.

**HTTP error mapping** for the chat endpoint:

| Code | Meaning                                             |
| ---- | --------------------------------------------------- |
| 422  | message too short / invalid fields                  |
| 404  | question matched no agent                           |
| 502  | LLM provider failure / empty response               |
| 503  | AI not configured (backend key/model missing)       |
| 504  | provider timed out                                  |

All provider errors are converted to safe, generic phrases; raw provider bodies
never reach the client, and the frontend maps statuses to its own messages
(`frontend/services/ai.service.ts`).

### Important constraints

- **Agents explain, not calculate.** Reorder quantities, forecasts, and alerts
  are produced by the deterministic services. The LLM only narrates them.
  "Use only this data" is enforced per agent prompt.
- **Context is bounded.** The provider's free tier caps tokens per minute
  (~7–8k for the available models), so each agent feeds at most the most recent
  record per product (`Backend/app/agents/base.py::latest_per_product`). This
  keeps the payload under the cap without dropping products or inventing data.
- **`product_id` is only set via the request body.** The assistant does not
  parse SKUs out of free-text, so a question naming a specific (possibly
  nonexistent) SKU is answered from the all-products context and the model is
  expected to say honestly that it has no data for that SKU.

## Security notes

- The LLM API key lives only in `Backend/.env` (gitignored). It is never sent to
  the browser; the frontend holds no key.
- CORS allows only the configured frontend origin.
- The orchestrator can only run the three allowlisted agents (forecast,
  inventory, insight) — no arbitrary tool or function execution.
- `git ls-files` tracks no `.env`, key, or credential file (only
  `Backend/.env.example` with placeholders).

## Known limitations (Stage 6C)

- "What are my biggest inventory risks?" routes to `inventory_agent` (keyword
  "inventory"), not `insight_agent` — the Insight Agent is exercised via
  "attention"/"priority" phrasings. Routing is a keyword allowlist by design.
- Free-text SKUs are not extracted; referencing `SKU-001` (not in the seed data)
  yields an honest "no data" answer from whichever agent route fires.
- Groq free tier at ~7–8k TPM limits sustained chat volume to a couple of
  requests per minute; rapid bursts can return 502 until the window resets.

## Recommended next step

Durable conversation storage (the store is in-memory today) and optional SKU
extraction for product-scoped answers would close the two UX gaps above.