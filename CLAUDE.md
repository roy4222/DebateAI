# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**DebateAI** is a multi-agent AI debate platform built with LangGraph, featuring real-time streaming debates between two AI agents (Optimist and Skeptic) on user-provided topics. The project demonstrates complex agent state management, tool use, and real-time streaming in a full-stack application.

**Architecture**: Decoupled frontend (Next.js on Cloudflare Pages) and backend (FastAPI on Google Cloud Run).

**Current Status**: Phase 2 complete (real AI debate with token-level streaming). Phase 3 (web search integration) is next.

## Tech Stack

- **Frontend**: Next.js 16 (App Router), React 19, shadcn/ui, Tailwind CSS 4
- **Backend**: FastAPI, Python 3.11+, uv package manager
- **AI Framework**: LangGraph 1.0+, LangChain, ChatGroq
- **LLM**: Groq API (llama-3.1-8b-instant model for ultra-fast inference)
- **Deployment**: Google Cloud Run (backend), Cloudflare Pages (frontend)
- **Communication**: Server-Sent Events (SSE) for real-time streaming

## Development Commands

### Backend (from `/backend`)

```bash
# Install dependencies using uv
uv sync

# Run locally
uv run uvicorn app.main:app --reload --port 8000

# Build Docker image
docker build -t debate-ai-backend .

# Deploy to Cloud Run
gcloud run deploy debate-api \
  --source . \
  --region asia-east1 \
  --set-env-vars GROQ_API_KEY=${GROQ_API_KEY} \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300
```

### Frontend (from `/frontend`)

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build static export for Cloudflare Pages
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages deploy out --project-name debate-ai
```

### Full Deployment (from root)

```bash
# One-command deployment (frontend only, assumes backend is deployed)
./deploy.sh
```

## Architecture Decisions

### Token-Level Streaming Implementation

**Current approach (Phase 2)**: Direct LLM streaming in `main.py`, with `graph.py` handling only state management and prompt building.

- `main.py` directly calls `llm.astream()` to achieve true token-level streaming
- `graph.py` provides `get_llm()`, `build_prompt()`, `update_state_after_speaker()`, `create_initial_state()`
- LangGraph is imported for ChatGroq but **not used for StateGraph control flow** in Phase 2

**Why**: LangGraph's `astream(stream_mode="messages")` only streams when messages are added to state, not during internal `llm.astream()` calls within nodes. To achieve real token-level streaming (typewriter effect), we bypass LangGraph's control flow.

**Future (Phase 3)**: May reintroduce LangGraph StateGraph for tool calling (web search), but streaming will likely remain in main.py.

### CORS Strategy

Custom `RegexCORSMiddleware` in `backend/app/main.py` supports:
- Regex patterns for `*.pages.dev` and `*.ggff.net` domains
- Localhost development
- Additional origins from `ALLOWED_ORIGINS` env var

### Search Tool Strategy (Phase 3)

Planned: Tavily (primary) + DuckDuckGo (fallback) for text search.
- **NOT using Playwright** in early phases (slow, high memory, incompatible with Cloud Run)
- Playwright reserved for optional Phase 4 "deep research" feature as separate Cloud Function
- See `docs/ARCHITECTURE_DECISIONS.md` for detailed rationale

## Key Files and Structure

### Backend (`/backend`)

```
backend/
├── app/
│   ├── main.py           # FastAPI app, SSE streaming endpoint, CORS
│   └── graph.py          # Debate state management, prompt building
├── Dockerfile            # uv-based containerization
├── pyproject.toml        # Python dependencies (managed by uv)
└── uv.lock               # Dependency lock file
```

- **`app/main.py`**:
  - `start_debate()` endpoint at `POST /debate` returns SSE stream
  - `fake_debate_stream()` for testing without Groq API
  - `real_debate_stream()` implements actual AI debate loop
  - Uses `sse_event()` helper to ensure proper `\n\n` SSE format

- **`app/graph.py`**:
  - `DebateState` TypedDict: messages, topic, current_speaker, round_count, max_rounds
  - `OPTIMIST_SYSTEM`, `SKEPTIC_SYSTEM`: Agent system prompts (enforce 2-3 sentence responses, mandate conflict)
  - Speaker alternation: Optimist → Skeptic → (increment round) → Optimist...

### Frontend (`/frontend`)

```
frontend/
├── app/
│   ├── page.tsx              # Main entry point
│   ├── layout.tsx            # Root layout
│   ├── globals.css           # Tailwind styles
│   ├── components/
│   │   ├── DebateUI.tsx      # Main debate interface (SSE client, state management)
│   │   ├── MessageBubble.tsx # Chat bubble component
│   │   └── TopicForm.tsx     # Topic input form
│   └── lib/
│       └── api.ts            # SSE streaming client, types
├── components/ui/            # shadcn/ui components
├── next.config.ts            # Static export config
└── wrangler.toml             # Cloudflare Pages config
```

- **`app/lib/api.ts`**:
  - `streamDebate()` uses fetch + ReadableStream for POST SSE (not EventSource)
  - Parses `data: {json}\n\n` format
  - Supports AbortSignal for cancellation

- **`app/components/DebateUI.tsx`**:
  - Uses `useRef` for text buffers to avoid React async state issues
  - Handles SSE events: status, speaker, token, speaker_end, complete, error
  - Auto-scrolls to latest message

### Documentation (`/docs`)

- **`IMPLEMENTATION.md`**: Detailed phase-by-phase implementation guide
- **`ARCHITECTURE_DECISIONS.md`**: Technical rationale for key choices (search tools, streaming, deployment)
- **`dev_notes/`**: Daily development logs with troubleshooting notes

## Environment Variables

### Backend

Set in Cloud Run or `.env` file:

- `GROQ_API_KEY`: Groq API key (required for real LLM, gsk_...)
- `GROQ_MODEL`: Model name (default: "llama-3.1-8b-instant")
- `USE_FAKE_STREAM`: Set "true" to use fake debate stream (testing)
- `ALLOWED_ORIGINS`: Comma-separated additional CORS origins (optional)

### Frontend

Set in Cloudflare Pages or `.env.production`:

- `NEXT_PUBLIC_API_URL`: Backend API URL (e.g., https://debate-api-....run.app)

## Development Workflow

### Adding a New Feature

1. Update relevant state in `graph.py` (if state changes needed)
2. Modify streaming logic in `main.py` (if new SSE events needed)
3. Update frontend types in `app/lib/api.ts`
4. Handle new events in `DebateUI.tsx`
5. Test locally: backend on :8000, frontend on :3000
6. Deploy: backend first (Cloud Run), then frontend (Cloudflare Pages)

### Debugging SSE Streaming

Common issues:
- **Frontend not receiving events**: Check SSE format uses literal `\n\n` (use `sse_event()` helper)
- **Tokens not streaming**: Verify `llm.astream()` is called directly in main.py, not inside LangGraph nodes
- **CORS errors**: Check `RegexCORSMiddleware` patterns match your frontend domain

Health check endpoint: `GET /health` returns current config including `has_groq_key`, `use_fake_stream`, `model`.

### Testing Locally

Backend:
```bash
cd backend
# Create .env with GROQ_API_KEY
echo "GROQ_API_KEY=your_key_here" > .env
uv run uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
npm run dev
```

Visit http://localhost:3000 and start a debate.

## Production URLs

- **Frontend**: https://debateai.roy422.ggff.net
- **Backend**: https://debate-api-1046434677262.asia-east1.run.app
- **Health Check**: https://debate-api-1046434677262.asia-east1.run.app/health

## Phase Roadmap

- ✅ **Phase 0**: Project setup, dependencies
- ✅ **Phase 1**: Fake SSE streaming, cloud deployment, CORS setup
- ✅ **Phase 2**: Real AI debate with Groq, token-level streaming
- 🔄 **Phase 3**: Web search integration (Tavily + DuckDuckGo), tool calling, moderator agent
- 🔮 **Phase 4** (optional): Playwright deep scraping as separate Cloud Function

## Important Notes for Future Development

1. **LangGraph StateGraph not currently used**: Phase 2 bypasses StateGraph for direct streaming control. May reintroduce in Phase 3 for tool calling.

2. **SSE format critical**: Always use `sse_event()` helper in backend to ensure proper `\n\n` line endings. Frontend expects `data: {json}\n\n` format.

3. **Agent prompts enforce conflict**: System prompts explicitly forbid agents from agreeing with each other to maintain debate dynamics.

4. **Round counting**: `round_count` increments only after Skeptic speaks. Display uses `round_count + 1` for user-facing round numbers.

5. **uv package manager**: All backend dependency management uses `uv` (not pip). Update `pyproject.toml` and run `uv sync`.

6. **Static export requirement**: Frontend uses `output: 'export'` in next.config.ts for Cloudflare Pages compatibility. No server-side rendering.

7. **Search tool strategy**: Prioritize speed (<1s) over completeness for debate rhythm. Tavily/DDGS text search is sufficient for Phase 3.
