# Intel Agent — Production AI Agent on Kubernetes

A production-grade competitive intelligence and document summarization agent demonstrating end-to-end observability, CI/CD, and Kubernetes deployment.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client (HTTP)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                ┌───────▼────────┐
                │   FastAPI app  │  port 8000
                │  (uvicorn)     │
                └───┬───────┬───┘
                    │       │
         ┌──────────▼──┐ ┌──▼──────────────┐
         │  Summarizer  │ │ Intel Agent      │
         │  (LangChain) │ │ (LangChain +    │
         └──────────────┘ │  DuckDuckGo)    │
                          └─────────────────┘
                    │
        ┌───────────▼─────────────────┐
        │        Observability        │
        │  ┌──────────┐ ┌──────────┐  │
        │  │  OTel    │ │Prometheus│  │
        │  │Collector │ │(port 9090│  │
        │  └────┬─────┘ └────┬─────┘  │
        │       │             │        │
        │  ┌────▼──┐   ┌─────▼──────┐ │
        │  │Jaeger │   │  Grafana   │ │
        │  │:16686 │   │   :3000    │ │
        │  └───────┘   └────────────┘ │
        └─────────────────────────────┘
                    │
        ┌───────────▼───────────┐
        │      Langfuse         │  LLM traces
        │  (cloud.langfuse.com) │
        └───────────────────────┘
```

### Two agents

| Endpoint | Agent | Description |
|---|---|---|
| `POST /api/v1/summarize` | Summarizer | Structured summary with key points, conclusion, sentiment |
| `POST /api/v1/intelligence` | Intel | Competitive report from live DuckDuckGo search + GPT-4o |

### Observability stack

| Layer | Tool | What it captures |
|---|---|---|
| Distributed tracing | OpenTelemetry → Jaeger | Per-request spans, LLM call latency |
| LLM tracing | Langfuse | Prompts, completions, token cost per call |
| Metrics | Prometheus + Grafana | Latency (p50/p95), token rate, error rate |
| Structured logs | structlog (JSON) | Every request with context variables |

## Quickstart (local)

```bash
cp .env.example .env
# Fill in OPENAI_API_KEY (and optionally LANGFUSE_* keys)

docker compose up --build
```

| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Grafana | http://localhost:3000 (admin/admin) |
| Jaeger | http://localhost:16686 |
| Prometheus | http://localhost:9091 |

Try it:
```bash
curl -X POST http://localhost:8000/api/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{"content": "Your document text here (min 100 chars)...", "language": "en"}'

curl -X POST http://localhost:8000/api/v1/intelligence \
  -H "Content-Type: application/json" \
  -d '{"query": "OpenAI GPT-5 competitors 2025"}'
```

## Development

```bash
pip install -e ".[dev]"
APP_ENV=test pytest           # 11 tests, 89% coverage
ruff check app/ tests/        # lint
mypy app/                     # type check (strict)
```

## CI/CD

```
Push to main
    └─► CI (GitHub Actions)
            ├─ ruff check
            ├─ mypy --strict
            ├─ pytest --cov
            └─ docker build + push to GHCR
                    └─► CD (GitHub Actions)
                            ├─ helm upgrade --install intel-agent
                            ├─ kubectl rollout status
                            └─ smoke test (exec into pod)
```

See `.github/workflows/ci.yml` and `.github/workflows/cd.yml`.

## Kubernetes deployment (Helm)

```bash
# Development
helm upgrade --install intel-agent ./helm/intel-agent \
  --set secrets.OPENAI_API_KEY="$OPENAI_API_KEY"

# Production (2+ replicas, HPA, TLS ingress)
helm upgrade --install intel-agent ./helm/intel-agent \
  --values ./helm/intel-agent/values.yaml \
  --values ./helm/intel-agent/values.prod.yaml \
  --set image.tag=$(git rev-parse HEAD) \
  --set secrets.OPENAI_API_KEY="$OPENAI_API_KEY" \
  --set secrets.LANGFUSE_PUBLIC_KEY="$LANGFUSE_PUBLIC_KEY" \
  --set secrets.LANGFUSE_SECRET_KEY="$LANGFUSE_SECRET_KEY" \
  --namespace intel-agent --create-namespace
```

Production values (`values.prod.yaml`): 2 replicas minimum, HPA up to 8, TLS via cert-manager, 2 vCPU / 2 Gi limit.

## Metrics & benchmarks

| Metric | Observed value |
|---|---|
| Summarization latency p50 | ~1.8 s (GPT-4o, 500-word doc) |
| Summarization latency p95 | ~4.2 s |
| Intelligence latency p50 | ~3.5 s (search + LLM) |
| Token cost per summarization | ~250–400 tokens |
| Token cost per intelligence report | ~300–600 tokens |
| Test coverage | 89% |
| Docker image size | ~280 MB (multi-stage) |

## Technical choices

| Choice | Rationale |
|---|---|
| FastAPI + uvicorn | Async-native, automatic OpenAPI docs, production-proven |
| structlog (JSON) | Machine-parseable logs compatible with any log aggregator |
| OTel → Jaeger | Vendor-neutral tracing; swap exporter for Datadog/Tempo without code change |
| Prometheus scrape annotations | Zero-config scraping in Kubernetes via pod annotations |
| Helm + values.prod.yaml | Single chart, environment overrides, GitOps-friendly |
| Multi-stage Dockerfile | Builder installs deps; runtime image has no build tools (~2× smaller) |
| Pydantic v2 + mypy strict | Type errors caught at development time, not production |

## Cross-cutting foundations

Shared production foundations wired into every layer of this project:

- **Structured logging** — `app/observability/logging.py`: `setup_logging()` (structlog → JSON) and `get_logger()`, with `request_id` propagated via contextvars. Initialised in the FastAPI lifespan.
- **Observability** — `app/observability/__init__.py`: in-memory `METRICS` counters and `record_span()` timing, offline-friendly and swappable for Prometheus/Langfuse without changing call sites.
- **Governance** — `app/governance.py`: `RBACPolicy.authorize` (role→permission, raises `AccessDeniedError`), `mask_pii`, `IdempotencyGuard`, and an append-only `AuditLog`.
- **LLM gateway** — `app/gateway.py` + `app/schemas/llm.py`: provider-agnostic `LLMGateway` with a deterministic offline `LocalProvider`, an OpenAI/LiteLLM-compatible `HttpLLMProvider`, automatic primary→fallback and streaming.

Known technical debt is tracked in [`DETTE-TECHNIQUE.md`](./DETTE-TECHNIQUE.md).
