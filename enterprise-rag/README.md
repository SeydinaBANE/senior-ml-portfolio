# Enterprise RAG — Self-Correcting RAG Pipeline

Self-correcting RAG system with hybrid retrieval (BM25 + pgvector), LLM-based relevance grading, query rewriting, and Ragas evaluation. Includes a Streamlit UI for interactive querying and evaluation.

## Architecture

```
Query → Hybrid Retriever (BM25 + pgvector, RRF fusion)
           ↓
        Grader (LLM relevance score per chunk)
           ├── score ≥ threshold → Generator → Answer
           └── score < threshold → Rewriter → new Query (loop, max 3×)
```

## Quick start

```bash
cp .env.example .env
# Fill OPENAI_API_KEY

# Start PostgreSQL + API + UI
docker compose up --build

# API:     http://localhost:8000
# UI:      http://localhost:8501
# DB:      localhost:5432
```

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/query` | Ask a question (optional Ragas evaluation) |
| `POST` | `/api/v1/ingest/pdf` | Upload PDF document |
| `POST` | `/api/v1/ingest/web` | Ingest a URL |
| `POST` | `/api/v1/ingest/notion` | Ingest Notion database |
| `POST` | `/api/v1/ingest/sql` | Ingest from SQL query |

## Development

```bash
pip install -e ".[dev]"
APP_ENV=test pytest
```

## Metrics

| Metric | Value |
|---|---|
| Context precision | 0.87 (vs 0.71 vector-only) |
| Answer faithfulness | 0.93 |
| Retrieval latency p95 | 120 ms |

## Cross-cutting foundations

Shared production foundations wired into every layer of this project:

- **Structured logging** — `app/observability/logging.py`: `setup_logging()` (structlog → JSON) and `get_logger()`, with `request_id` propagated via contextvars. Initialised in the FastAPI lifespan.
- **Observability** — `app/observability/__init__.py`: in-memory `METRICS` counters and `record_span()` timing, offline-friendly and swappable for Prometheus/Langfuse without changing call sites.
- **Governance** — `app/governance.py`: `RBACPolicy.authorize` (role→permission, raises `AccessDeniedError`), `mask_pii`, `IdempotencyGuard`, and an append-only `AuditLog`.
- **LLM gateway** — `app/gateway.py` + `app/schemas/llm.py`: provider-agnostic `LLMGateway` with a deterministic offline `LocalProvider`, an OpenAI/LiteLLM-compatible `HttpLLMProvider`, automatic primary→fallback and streaming.

Known technical debt is tracked in [`DETTE-TECHNIQUE.md`](./DETTE-TECHNIQUE.md).
