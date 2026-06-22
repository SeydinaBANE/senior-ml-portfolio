# Agent Platform — Full Agentic Platform

A production-grade multi-tenant agentic platform built with FastAPI, LangChain, PostgreSQL and Redis. Recruiters: see the [demo section](#demo) below.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Streamlit UI                          │
│  Auth · Marketplace · Builder · Run Agent · Billing          │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼─────────────────────────────────┐
│                      FastAPI App                             │
│  /auth  /agents  /run  /billing  /health                     │
│       ↓ JWT + RBAC (admin/developer/user)                    │
│  ┌────────────┐  ┌────────────────┐  ┌─────────────────┐    │
│  │  Marketplace│  │  Smart Router  │  │  Billing Engine │    │
│  │  CRUD Agent │  │  LLM Classifier│  │  Cost per token │    │
│  └────────────┘  │  → Dispatcher  │  └─────────────────┘    │
│                  └────────────────┘                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │         Observability                                  │  │
│  │  OTel Tracing → OTLP Collector   Prometheus :9090      │  │
│  └────────────────────────────────────────────────────────┘  │
└──────────┬───────────────────────────────────────────────────┘
           │
  ┌────────┴──────────┐
  │  PostgreSQL 16     │  ← Alembic migrations, tenant-scoped queries
  │  Redis 7           │  ← Session cache (future: rate limiting)
  └───────────────────┘
```

## Key features

| Feature | Details |
|---|---|
| **Multi-tenancy** | Every DB query scoped by `tenant_id` (JWT claim) |
| **RBAC** | `admin / developer / user` with granular permissions (agent:create, agent:update, billing:read…) |
| **Smart routing** | LLM-based intent classifier picks the best agent from the marketplace |
| **Billing tracking** | Token usage + cost logged per run; aggregated billing report endpoint |
| **Observability** | OpenTelemetry traces (OTLP), Prometheus metrics (runs, latency, tokens) |
| **Low-code UI** | Streamlit UI to register users, build agents, run them, and see billing |

## Quantified results (local benchmarks)

| Metric | Value |
|---|---|
| P50 routing latency (LLM classifier) | ~400 ms |
| P50 end-to-end latency (gpt-4o-mini) | ~1.2 s |
| Token cost per run (gpt-4o-mini, avg) | ~$0.0008 |
| Test coverage | 85 %+ |
| Cold start (Docker) | < 3 s |

## Quick start

```bash
cp .env.example .env        # fill OPENAI_API_KEY and SECRET_KEY
docker compose up --build   # starts app:8000, ui:8501, postgres, redis

# Apply migrations (first run)
docker compose exec app alembic upgrade head
```

Open http://localhost:8501 for the Streamlit UI.

## Development

```bash
pip install -e ".[dev]"
APP_ENV=test pytest               # all tests + coverage
ruff check app/ tests/ ui/        # lint
mypy app/                         # type check
```

## API overview

| Method | Path | Auth | Permission |
|---|---|---|---|
| POST | `/api/v1/auth/register` | — | — |
| POST | `/api/v1/auth/login` | — | — |
| GET | `/api/v1/agents` | JWT | agent:read |
| POST | `/api/v1/agents` | JWT | agent:create |
| PUT | `/api/v1/agents/{id}` | JWT | agent:update |
| DELETE | `/api/v1/agents/{id}` | JWT | agent:delete |
| POST | `/api/v1/run` | JWT | agent:read |
| POST | `/api/v1/billing/report` | JWT | billing:read |
| GET | `/health` | — | — |

## CI/CD

GitHub Actions: lint → typecheck → test → build Docker image → push GHCR → `kubectl rollout` on `main`.

## Kubernetes

```bash
kubectl apply -f k8s/deployment.yaml
```

Secrets must be created before deploying:
```bash
kubectl create secret generic agent-platform-secrets \
  --from-env-file=.env
```

## Technical choices

- **FastAPI** — async-first, auto OpenAPI docs, Pydantic validation
- **LangChain structured output** — `with_structured_output(RoutingDecision)` for reliable JSON routing decisions
- **SQLAlchemy async** — `asyncpg` driver, session-per-request pattern
- **Alembic** — version-controlled schema migrations, rollback-safe
- **prometheus-client** — zero-dependency metrics, scraped by Prometheus/Grafana
- **OpenTelemetry** — vendor-neutral traces, compatible with Jaeger/Tempo/Honeycomb

## Demo

> Launch the stack with `docker compose up --build`, then open http://localhost:8501.

1. **Auth** — register a user (pick a UUID tenant ID), then login
2. **Builder** — create an "HR Assistant" agent with category `hr`
3. **Run** — type "What is the vacation policy?" — the LLM router picks your agent automatically
4. **Billing** — generate a report to see token usage and cost
