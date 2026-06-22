# Research Agent — Architecture

## Overview

Stateless LangGraph pipeline with 5 nodes (plan → search → verify → write → review). No database. Integrates Tavily, Gmail, Calendar, Notion, Slack. No auth on API endpoints.

## Code map

| Path | Responsibility |
|---|---|
| `app/main.py` | FastAPI app, router registration (no lifespan, no middleware) |
| `app/config.py` | `Settings` — Tavily/Notion/Slack keys, Google OAuth paths, retrieval params |
| `app/api/routes/health.py` | `GET /health` |
| `app/api/routes/research.py` | `POST /api/v1/research` — runs `compiled_graph.ainvoke()`, optional Slack/Notion distribution |
| `app/api/routes/tools.py` | `GET /api/v1/tools/status` — checks which env vars are set |
| `app/schemas/research.py` | `ResearchRequest` (topic, post_to_slack, save_to_notion), `ResearchReport` |
| `app/agent/state.py` | `ResearchState(BaseModel)` — topic, search_queries, raw_results, verified_sources, messages, report_draft, iteration, next |
| `app/agent/graph.py` | LangGraph `StateGraph` — 5 nodes + conditional edge + review loop. Singleton `compiled_graph` |
| `app/tools/search.py` | `web_search()` — TavilyClient; `search_tool` — LangChain @tool |
| `app/tools/verifier.py` | `fetch_page_text()` (httpx+BeautifulSoup), `verify_source()` (LLM checks claim support) |
| `app/tools/gmail.py` | `send_email_tool`, `read_recent_emails_tool` — Gmail API via google-api-python-client |
| `app/tools/calendar.py` | `list_upcoming_events_tool`, `create_event_tool` — Google Calendar API |
| `app/tools/notion.py` | `create_notion_page_tool`, `search_notion_tool` — Notion REST API via httpx |
| `app/tools/slack.py` | `post_slack_message_tool`, `post_report_to_slack_tool` — Slack Block Kit |
| `ui/streamlit_app.py` | Single-page UI: tool status sidebar, topic input, report output with source cards |

## Graph pipeline

```
plan ──► search ──► verify ──► write ──► review ──► END
                                    ▲         │
                                    └── rejected ─┘ (max 1 retry)
```

- **plan_node**: `ChatOpenAI.with_structured_output(_QueryPlan)` → generates up to `max_search_queries` (default 5) diverse search queries
- **search_node**: Parallel `asyncio.gather` of Tavily searches. Filters by `min_source_confidence` (0.6)
- **verify_node**: Deduplicates by URL → parallel `verify_source()` calls. Keeps only sources with `supports=True AND confidence >= 0.6`
- **write_node**: LLM writes structured report with executive summary, findings, analysis, citations
- **review_node**: If `iteration >= 1`, auto-approve. Otherwise LLM reviews draft → approve or reject with feedback. On reject, routes back to write_node

## Source verification

1. `fetch_page_text(url)`: httpx GET → BeautifulSoup → strip script/style/nav/footer → max 3000 chars
2. `verify_source(url, claim)`: LLM with structured output (`_VerifySchema`: supports, confidence, excerpt)
3. Threshold: only `supports=True AND confidence >= 0.6` are kept

Graceful degradation: if page fetch fails, returns `unverified` (not fatal).

## Tool integrations

| Service | Client | Auth | LangChain @tool |
|---|---|---|---|
| Tavily | `TavilyClient` | API key | `search_tool` |
| Gmail | `googleapiclient.discovery.build` | OAuth2 (token file) | `send_email_tool`, `read_recent_emails_tool` |
| Calendar | `googleapiclient.discovery.build` | OAuth2 (same token) | `list_upcoming_events_tool`, `create_event_tool` |
| Notion | `httpx.AsyncClient` | Bearer token | `create_notion_page_tool`, `search_notion_tool` |
| Slack | `slack_sdk.AsyncWebClient` | Bot token | `post_slack_message_tool`, `post_report_to_slack_tool` |

Google OAuth2 token is auto-refreshed but initial auth must be done externally (no `/auth/google/callback` route implemented).

## Tests

| File | Tests | What |
|---|---|---|
| `conftest.py` | — | `client` (ASGITransport), sets env vars |
| `test_agent/test_researcher.py` | 2 | plan_node generates queries, verify_node filters low confidence |
| `test_tools/test_search.py` | 2 | Confidence filtering, missing API key RuntimeError |
| `test_tools/test_verifier.py` | 2 | Supports claim, fetch failure returns unverified |

No API endpoint tests. No Gmail/Calendar/Notion/Slack tool tests.
