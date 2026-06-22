# Enterprise Agent — Architecture

## Overview

Multi-agent assistant using a LangGraph `StateGraph` with a supervisor node that dispatches to three specialist agents (RAG, Tool, Memory). PostgreSQL + pgvector for vector search, Redis for short-term cache, JWT auth for multi-tenancy.

## Graph topology

```
supervisor ──(conditional)──► rag ──► supervisor
                            ├── tool ──► supervisor
                            ├── memory ──► supervisor
                            └── __end__
```

The supervisor uses `ChatOpenAI.with_structured_output(RoutingDecision)` to pick the next node. Loop guard: max 5 iterations (`AgentState.iteration_count`).

## Code map

| Path | Responsibility |
|---|---|
| `app/main.py` | FastAPI app, lifespan (tracing init, engine dispose), router wiring |
| `app/config.py` | `Settings` from pydantic-settings; validates prod secrets |
| `app/api/deps.py` | `get_current_tenant` — JWT → `tenant_id: UUID` |
| `app/api/routes/chat.py` | `POST /api/v1/chat` — guardrails → save msg → `compiled_graph.ainvoke()` → save response |
| `app/api/routes/health.py` | `GET /health` |
| `app/schemas/chat.py` | `ChatRequest` (message, session_id), `ChatResponse` (answer, sources, tenant_id) |
| `app/db/models.py` | `Tenant`, `Document` (with pgvector), `ConversationMessage` |
| `app/db/session.py` | Async engine + `async_sessionmaker` |
| `app/agents/state.py` | `AgentState(BaseModel)` — messages (add_messages reducer), tenant_id, session_id, next_agent, context_chunks, iteration_count |
| `app/agents/graph.py` | `build_graph()` → 4 nodes + conditional edge; singleton `compiled_graph` |
| `app/agents/supervisor.py` | `RoutingDecision(BaseModel)` — next agent; routes to `__end__` at iteration 5 |
| `app/agents/specialized/rag_agent.py` | `rag_node` — embed query → pgvector cosine search → LLM answer |
| `app/agents/specialized/tool_agent.py` | `tool_node` — bind DuckDuckGo + SQL tools → execute → synthesize |
| `app/agents/specialized/memory_agent.py` | `memory_node` — load last 20 messages → LLM with history |
| `app/rag/retriever.py` | `retrieve()` (cosine `<=>` + tenant filter), `index_document()` (embed + insert) |
| `app/memory/persistent.py` | `load_session_history()`, `save_message()` — PostgreSQL |
| `app/memory/cache.py` | `cache_get/set` — Redis with 5-min TTL |
| `app/tools/search.py` | `web_search_tool` — DuckDuckGo instant answer API |
| `app/tools/database.py` | `query_database_tool` — SELECT-only SQL execution |
| `app/security/auth.py` | `create_access_token()`, `decode_token()` — HS256 JWT |
| `app/security/guardrails.py` | Regex prompt injection filter (6 patterns, max 4000 chars) |
| `app/observability/tracing.py` | OTel TracerProvider + optional Langfuse init |

## Key data flow

```
POST /api/v1/chat
  → JWT auth (tenant_id from token)
  → guardrails.validate_input(message)
  → save user message to conversation_messages
  → AgentState(messages=[HumanMessage], tenant_id, session_id)
  → compiled_graph.ainvoke(initial_state)
     → supervisor → rag/tool/memory → ... → supervisor → __end__
  → extract last AIMessage
  → save assistant message
  → return ChatResponse
```

## Multi-tenancy

Every DB query includes `WHERE tenant_id = :tenant_id`. The tenant_id comes from the JWT, never from user input.

## Tests

| File | Tests | What |
|---|---|---|
| `conftest.py` | — | `tenant_id`, `auth_headers`, `client` (ASGITransport) |
| `test_api/test_chat.py` | 3 | Nominal, injection 400, missing auth |
| `test_security/test_auth.py` | 4 | Roundtrip, invalid, tampered, distinct tenants |
| `test_security/test_guardrails.py` | 7 | Each pattern blocked, max length |
| `test_rag/test_retriever.py` | 2 | Returns chunks, empty on no results |
| `test_memory/test_persistent.py` | 3 | Save commits, load chronological, empty |
| `test_tools/test_search.py` | 3 | Answer, fallback, no results |
| `test_agents/test_supervisor.py` | 2 | Routes to rag, stops at max iterations |

All external calls mocked. No live DB/Redis/OpenAI needed.
