# Enterprise RAG — Architecture

## Overview

Self-RAG LangGraph pipeline: hybrid retrieval (BM25 + pgvector with RRF fusion) → LLM relevance grader → query rewriter (loop, max 3×) → answer generator. Four ingestion sources (PDF, web, SQL, Notion). Optional Ragas evaluation.

## Code map

| Path | Responsibility |
|---|---|
| `app/main.py` | FastAPI app + lifespan (engine dispose) |
| `app/config.py` | `Settings` — hybrid weights, retrieval iterations, notion creds |
| `app/api/routes/health.py` | `GET /health` |
| `app/api/routes/query.py` | `POST /api/v1/query` — runs `run_rag()` + optional Ragas eval |
| `app/api/routes/ingest.py` | 4 ingestion endpoints: PDF (multipart), web, notion, SQL |
| `app/schemas/query.py` | `QueryRequest` (question, evaluate flag, ground_truth), `QueryResponse` |
| `app/schemas/ingest.py` | `IngestWebRequest`, `IngestSQLRequest`, `IngestResponse` |
| `app/db/models.py` | `Document` (with pgvector embedding), `EvaluationResult` |
| `app/db/session.py` | Async engine + session |
| `app/rag/pipeline.py` | LangGraph `StateGraph` with 4 nodes (retrieve → grade → generate, or grade → rewrite → retrieve). Singleton `compiled_rag` |
| `app/rag/grader.py` | `GradeResult(BaseModel)` — LLM relevance score per chunk. `filter_relevant_chunks()` runs all chunks in parallel |
| `app/rag/rewriter.py` | `rewrite_query()` — LLM reformulates question for better retrieval |
| `app/rag/generator.py` | `GeneratedAnswer(BaseModel)` — LLM answer + sufficiency check |
| `app/rag/retriever/hybrid.py` | `_reciprocal_rank_fusion()` — RRF with configurable vector (0.6) / BM25 (0.4) weights. Deduplicates by content |
| `app/rag/retriever/vector.py` | `vector_search()` — pgvector cosine distance (`<=>`) converted to similarity score |
| `app/rag/retriever/bm25.py` | `bm25_search()` — loads all documents, builds in-memory BM25Okapi index per call |
| `app/ingestion/store.py` | `ingest_chunks()` — embed all chunks via `OpenAIEmbeddings.aembed_documents()`, INSERT with ON CONFLICT DO NOTHING |
| `app/ingestion/pdf.py` | PyPDF reader + sliding-window chunking (1000 chars, 200 overlap) |
| `app/ingestion/web.py` | httpx + BeautifulSoup, strip script/style/nav/footer |
| `app/ingestion/sql.py` | Dynamic async engine per query, row→text chunk conversion |
| `app/ingestion/notion.py` | Notion API (httpx, `Notion-Version: 2022-06-28`), queries database + page blocks |
| `app/evaluation/ragas_eval.py` | `run_ragas()` — converts samples to HF Dataset, runs faithfulness/answer_relevancy/context_precision metrics. `persist_eval_result()` |
| `ui/streamlit_app.py` | Single-page UI: question input, answer display, context chunks, Ragas bar chart |

## RAG pipeline graph

```
retrieve ──► grade ──► generate ──► END
                │
             rewrite ──► retrieve (loop, max 3×)
```

- **retrieve_node**: calls `hybrid_search(query)` using current_query (or original question)
- **grade_node**: LLM grades each chunk for relevance via `asyncio.gather`. If any relevant → generate. If none relevant + iterations left → rewrite. If none relevant + max iterations → fallback to all chunks
- **rewrite_node**: LLM reformulates query, sets `current_query`, routes back to retrieve
- **generate_node**: LLM produces final answer with structured output

## Hybrid retrieval

- `vector_search`: pgvector cosine similarity, `WHERE embedding <=> :query_emb`
- `bm25_search`: loads all documents, builds BM25Okapi in memory, tokenizes with `str.lower().split()`
- RRF fusion: `score = Σ weight / (k + rank + 1)` where k=60, vector_weight=0.6, bm25_weight=0.4
- Both searches run concurrently via `asyncio.gather`

## Ingestion

| Source | Chunking | Embedding | Storage |
|---|---|---|---|
| PDF | Sliding window 1000/200 chars | OpenAI | pgvector with dedup |
| Web | 1000-char splits | OpenAI | pgvector with dedup |
| SQL | 1 row = 1 chunk | OpenAI | pgvector with dedup |
| Notion | 1 page = 1 chunk | OpenAI | pgvector with dedup |

## Tests

| File | Tests | What |
|---|---|---|
| `conftest.py` | — | `client` fixture (ASGITransport, unused by current tests) |
| `test_rag/test_pipeline.py` | 2 | Happy path (1 iteration), rewrite path (2 iterations) |
| `test_rag/test_hybrid.py` | 2 | RRF deduplication, RRF respects weights |
| `test_evaluation/test_ragas.py` | 1 | Ragas scores extraction |

No ingestion or API tests yet. `test_ingestion/` is empty.

## Notable gaps

- Alembic is in pyproject.toml deps but no migration files exist — tables must be created via `Base.metadata.create_all()`
- No auth/security middleware
- `test_ingestion/` and `test_api/` directories exist but are empty
- No Redis, Langfuse, OTel tracing, or Prometheus metrics

## Cross-cutting foundations

Shared production foundations wired into every layer of this project:

- **Structured logging** — `app/observability/logging.py`: `setup_logging()` (structlog → JSON) and `get_logger()`, with `request_id` propagated via contextvars. Initialised in the FastAPI lifespan.
- **Observability** — `app/observability/__init__.py`: in-memory `METRICS` counters and `record_span()` timing, offline-friendly and swappable for Prometheus/Langfuse without changing call sites.
- **Governance** — `app/governance.py`: `RBACPolicy.authorize` (role→permission, raises `AccessDeniedError`), `mask_pii`, `IdempotencyGuard`, and an append-only `AuditLog`.
- **LLM gateway** — `app/gateway.py` + `app/schemas/llm.py`: provider-agnostic `LLMGateway` with a deterministic offline `LocalProvider`, an OpenAI/LiteLLM-compatible `HttpLLMProvider`, automatic primary→fallback and streaming.

Known technical debt is tracked in [`DETTE-TECHNIQUE.md`](./DETTE-TECHNIQUE.md).
