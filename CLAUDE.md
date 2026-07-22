# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

AidBot is an internal after-sales support Q&A system (售后问答系统) for a company. It provides a chat interface where support staff ask questions and receive RAG-augmented answers drawn from a managed knowledge base.

**Stack:** FastAPI backend → Next.js 15 frontend → PostgreSQL with pgvector (pgvector/pgvector:pg16)

## Commands

### Docker (all-in-one)

```powershell
Copy-Item .env.example .env    # only needed once to override defaults
docker compose up --build
```

- Frontend: http://localhost:3010
- Backend health: http://localhost:8010/health
- Backend API docs: http://localhost:8010/docs

### Local development (backend)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8010
```

### Local development (frontend)

```powershell
cd frontend
npm install
npm run dev          # Next.js dev server on port 3010
npm run build        # production build
npm run lint         # ESLint
npm run typecheck    # tsc --noEmit
```

### Tests

```powershell
cd backend
pytest                              # all tests
pytest tests/test_knowledge.py      # single test file
pytest tests/test_chat_contract.py -v  # verbose
```

Tests use SQLite (configured in `backend/tests/conftest.py`), not the Docker PostgreSQL.

### Graphify knowledge graph

```bash
graphify query "<question>"          # scoped subgraph for codebase questions
graphify path "<A>" "<B>"            # find relationships between concepts
graphify explain "<concept>"         # focused concept lookup
graphify update .                    # regenerate graph after code changes (AST-only, no API cost)
```

## Architecture

### Backend (`backend/app`)

**Entry point:** `main.py` — creates the FastAPI app, registers CORS middleware, and mounts seven API routers. On startup, runs `Base.metadata.create_all()` + `ensure_runtime_schema()` for schema migration.

**API routes** (each in `app/api/<name>.py`):
| Prefix | File | Purpose |
|---|---|---|
| `/health` | `health.py` | Health check |
| `/api/auth` | `auth.py` | Login, token validation, current user |
| `/api/chat` | `chat.py` | Non-streaming + SSE streaming chat |
| `/api/conversations` | `conversations.py` | CRUD with archive/restore/delete |
| `/api/knowledge` | `knowledge.py` | Knowledge spaces, sources, import (manual/markdown/document/reindex) |
| `/api/feedback` | `feedback.py` | User feedback on answers |
| `/api/admin` | `admin.py` | Admin endpoints |

**Auth flow:** Custom HMAC-SHA256 token (not JWT). `core/security.py` — `create_access_token()` encodes claims as base64 JSON + HMAC signature. `get_current_user()` FastAPI dependency validates and returns `CurrentUser`. Seed admin credentials from env (`SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD`).

**LLM provider pattern** (`services/llm_service.py`): `LLMProvider` Protocol with `complete()` + `stream_answer()`. Two implementations:
- `LocalSupportProvider` — deterministic fallback, returns placeholder text, does NOT call any external API
- `OpenAICompatibleProvider` — calls `LLM_BASE_URL/chat/completions` with streaming, used for DeepSeek or any OpenAI-compatible endpoint
- `create_provider()` factory: if `LLM_PROVIDER` is `deepseek`/`openai_compatible` AND `LLM_API_KEY` is set → OpenAI; otherwise → local

**RAG pipeline** (`services/rag_service.py`): Hybrid retrieval combining:
1. Vector similarity: `EmbeddingService` (SHA-256 hash-based 96-dim embeddings, `_tokens()`: word + bigram tokenization)
2. Lexical score: CJK bigram matching + ASCII term overlap
3. Source diversity: first pass picks top result per unique source, then fills remaining slots
4. Markdown cleaning (`_clean_markdown_for_prompt`) strips formatting for LLM context

**Chat service** (`services/chat_service.py`): Orchestrates the full answer flow — resolves or creates conversation, injects last 6 messages as context for follow-up questions (`_question_with_recent_context`), runs RAG retrieval, calls LLM, persists messages. Both sync (`answer`) and SSE streaming (`stream_answer`) paths.

**Knowledge data model** (hierarchy):

```
KnowledgeSpace (visibility: internal|private)
  └── KnowledgeSource (source_type: upload|feishu|manual|ticket, content_format: text|markdown|html|pdf)
        └── KnowledgeDocument (title, content)
              └── KnowledgeChunk (chunk_index, embedding, content)
```

Documents are split on markdown heading boundaries (1800-char chunks with 250-char overlap). `ensure_runtime_schema()` in `core/schema.py` handles additive column migrations (e.g., adding `space_id`, `content_format`, `filename` to `knowledge_sources` at startup).

**Strategy pattern** (`services/strategies/`): Placeholder for future answer routing. `TemplateStrategy` is the phase-0 default; `RAGStrategy` is stubbed for phase 3.

### Frontend (`frontend/src`)

**Framework:** Next.js 15 with React 19, no additional UI libraries — all custom CSS.

**Routing** (App Router):
| Path | File | Auth |
|---|---|---|
| `/login` | `login/page.tsx` + `login-form.tsx` | Public |
| `/` | `page.tsx` (redirects to `/chat`) | Protected |
| `/chat` | `chat/page.tsx` + `workbench.tsx` | Protected |
| `/knowledge` | `knowledge/page.tsx` + `workbench.tsx` | Protected |
| `/feedback` | `feedback/page.tsx` + `workbench.tsx` | Protected |
| `/admin` | `admin/page.tsx` | Protected |

**Auth model:** Server components use `lib/auth.ts` — `requireSession()` reads `aidbot_session` cookie and validates via `/api/auth/me` on the server side, redirecting to `/login` on failure. Client components read the token from cookies and pass it to API functions in `lib/api.ts`.

**API client** (`lib/api.ts`): Dual URL resolution — `NEXT_PUBLIC_API_BASE_URL` for browser (client components), `API_INTERNAL_BASE_URL` for server components. SSE streaming (`askQuestionStream`) parses the `text/event-stream` protocol with `message_start` / `answer_delta` / `final` / `error` events.

**Types** (`lib/types.ts`): Shared TypeScript interfaces for all API contracts — `ChatRequest`, `ChatResponse`, `ChatStreamEvent`, conversation types, knowledge types, feedback types. Must stay in sync with backend Pydantic schemas.

### Environment variables

Key env vars (see `.env.example` for full list):
- `DATABASE_URL` — SQLAlchemy connection string
- `LLM_PROVIDER` — `local` (deterministic fallback) or `deepseek`/`openai_compatible` (real API)
- `LLM_MODEL` — model name sent to the provider
- `LLM_API_KEY` — API key (empty = use local provider regardless of LLM_PROVIDER)
- `AUTH_SECRET_KEY` — HMAC signing key for tokens
- `SEED_ADMIN_EMAIL` / `SEED_ADMIN_PASSWORD` — dev login credentials
- `BACKEND_CORS_ORIGINS` — comma-separated allowed origins
- `NEXT_PUBLIC_API_BASE_URL` — browser-side API URL
- `API_INTERNAL_BASE_URL` — server-side API URL (Docker service name)

### Database

PostgreSQL 16 with pgvector extension. In Docker, tables are auto-created by `Base.metadata.create_all()`. For local pytest, the test suite overrides `DATABASE_URL` to SQLite and creates tables in `conftest.py`.
