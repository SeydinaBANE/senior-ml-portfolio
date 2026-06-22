# Intel Agent — Architecture

## Overview

Stateless FastAPI app with two LLM-based agents (summarizer + intelligence search). No database. Full observability: OTel → Jaeger, Prometheus metrics, structlog JSON logging, Langfuse for LLM traces.

## Code map

| Path | Responsibility |
|---|---|
| `app/main.py` | FastAPI app + lifespan (logging, metrics server, tracing init) |
| `app/config.py` | `Settings` — env-driven, including OTLP endpoint and Langfuse keys |
| `app/api/routes/health.py` | `GET /health` — returns `{"status": "ok", "version": "0.1.0"}` |
| `app/api/routes/summarize.py` | `POST /api/v1/summarize` — validates `SummaryRequest` → calls `summarize_document()` |
| `app/api/routes/intelligence.py` | `POST /api/v1/intelligence` — validates `IntelRequest` → calls `gather_intelligence()` |
| `app/schemas/summarize.py` | `SummaryRequest` (content 100-50000 chars, language), `SummaryResponse` |
| `app/schemas/intelligence.py` | `IntelRequest` (query 3-500 chars), `IntelResponse` |
| `app/agent/summarizer.py` | `summarize_document()` — ChatOpenAI call with system prompt, records latency + token metrics |
| `app/agent/intelligence.py` | `gather_intelligence()` — DuckDuckGo search → LLM report generation, handles search failure gracefully |
| `app/observability/tracing.py` | OTel `TracerProvider` with `OTLPSpanExporter` (skips in test env) + Langfuse init |
| `app/observability/metrics.py` | `summarization_latency`, `intelligence_requests_total`, `tokens_consumed_total` — served on port 9090 |
| `app/observability/logging.py` | structlog with `JSONRenderer` + timestamps |

## Key agents

### Summarizer (`app/agent/summarizer.py`)
- Module-level `_llm = ChatOpenAI(model=settings.openai_model)`
- System prompt asks for structured summary with key points, conclusion, sentiment
- Records `summarization_latency_seconds` histogram and `tokens_consumed_total` counter
- Returns `SummaryResponse(summary, tokens_used, latency_ms, model)`

### Intelligence agent (`app/agent/intelligence.py`)
- Module-level `_llm` + `_search = DuckDuckGoSearchRun()`
- Runs web search → LLM produces competitive report
- On search failure: returns report from LLM knowledge alone, increments `intelligence_requests_total{status="search_error"}`
- Returns `IntelResponse(query, report, tokens_used, sources_searched)`

## Observability

- **Tracing**: OTel spans auto-instrumented via `OpenTelemetryInstrumentor().instrument_fastapi()`. Custom spans on summarizer/intel calls. Exported via gRPC to OTel Collector → Jaeger.
- **Metrics**: Prometheus HTTP server on port 9090 (separate from app port 8000). 3 metrics: latency histogram, requests counter, tokens counter.
- **Logging**: structlog JSON output to stdout. `setup_logging()` called at app startup.
- **Langfuse**: Optional. If `LANGFUSE_PUBLIC_KEY` is set, initializes Langfuse for LLM trace visualization.

## Helm chart

| File | Resource |
|---|---|
| `helm/intel-agent/Chart.yaml` | Chart metadata (v0.1.0) |
| `templates/deployment.yaml` | Deployment with Prometheus annotations, probes, ConfigMap + Secret refs |
| `templates/service.yaml` | ClusterIP, ports 80→8000 (http), 9090→9090 (metrics) |
| `templates/ingress.yaml` | Conditional TLS ingress with cert-manager |
| `templates/hpa.yaml` | Conditional HPA (CPU + memory) |
| `templates/configmap.yaml` | Non-sensitive env vars |
| `templates/secret.yaml` | Sensitive env vars (stringData) |
| `values.yaml` | Defaults: 1 replica, 250m/512Mi requests, 1/1Gi limits |
| `values.prod.yaml` | Production: 2 replicas min, HPA 2–8, ingress enabled, 500m/1Gi requests, 2/2Gi limits |

## CI/CD

CI (`.github/workflows/ci.yml`): `ruff format --check` → `ruff check` → `mypy` → `pytest --cov` → docker build+push to GHCR.

CD (`.github/workflows/cd.yml`): triggered on CI success on `main` → `helm upgrade --atomic` with production values → rollout status → smoke test (pod exec `/health`).

## Tests

| File | Tests | What |
|---|---|---|
| `conftest.py` | — | Sets `OPENAI_API_KEY=sk-test-key`, `APP_ENV=test`; provides `async_client` |
| `test_api/test_summarize.py` | 3 | API happy path, short content rejection (422), health endpoint |
| `test_api/test_intelligence.py` | 3 | API happy path, short query (422), empty query (422) |
| `test_agent/test_summarizer.py` | 2 | Returns correct response, tracks metrics |
| `test_agent/test_intelligence.py` | 3 | Returns response, handles search failure gracefully, tracks tokens |

All external calls mocked. No live LLM or search calls.
