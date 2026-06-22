# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This workspace is a portfolio preparation kit for a **Senior Agentic AI Engineer** job application. It contains:

- `offre.md` — the full job description (in French) with technical requirements
- `CONSEIL.md` — key advice: emphasize production readiness, quantify results, add demos, write detailed READMEs
- `projet-1.md` through `projet-6.md` — six portfolio project briefs to build and showcase
- `projet-1/` through `projet-6/` — the actual project implementations

## Target role requirements (from `offre.md`)

Core stack: **Python, LangGraph/LangChain, FastAPI, Docker, Kubernetes, CI/CD (GitHub Actions)**

Key themes to demonstrate in every project:
- Production-grade observability: OpenTelemetry, Langfuse, Prometheus + Grafana
- Security: prompt injection protection, multi-tenancy with strong isolation, OWASP Top 10 for LLMs
- Governance: OPA/Rego policy-as-code, audit trails, reproducibility
- Quality: Pydantic structured output, typed Python, tests, CI/CD pipelines

## Project briefs summary

| Dir | Project |
|---|---|
| `projet-1/` | Multi-agent enterprise assistant (LangGraph supervisor + RAG + FastAPI + PostgreSQL + Redis) |
| `projet-2/` | Secure AI agent platform with OPA/Rego policy-as-code, NeMo Guardrails, multi-tenancy |
| `projet-3/` | Production agent on Kubernetes with Helm, GitHub Actions CI/CD, full observability stack |
| `projet-4/` | Enterprise-grade RAG with hybrid search, self-correction, Ragas evaluation |
| `projet-5/` | Full agentic platform (agent marketplace, low-code builder, RBAC, usage tracking) — stub |
| `projet-6/` | Tool-calling agent (Gmail, Calendar, Slack…) — stub |

## Dev commands (apply inside each `projet-N/` directory)

All projects use Python 3.12, `hatchling`, `ruff`, `mypy` (strict), and `pytest-asyncio`.

```bash
pip install -e ".[dev]"                        # install with dev extras
ruff format app/ tests/                        # format (run before lint)
ruff check app/ tests/                         # lint (line-length=100, ruleset: E,F,I,UP,N,S,B,A; S101 ignored)
mypy app/                                      # type check (strict=true)
APP_ENV=test pytest                            # all tests with coverage
APP_ENV=test pytest tests/path/test_file.py    # single test file
APP_ENV=test pytest -k "test_name" -v          # single test by name
docker compose up --build                      # local full stack
```

Projet-1 and projet-4 use Alembic for DB migrations:
```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
```

Projet-4 has a Streamlit evaluation UI: `streamlit run ui/streamlit_app.py`

`APP_ENV=test` is required — the app conditionally skips DB/Redis init in test mode. Tests use `httpx.AsyncClient(transport=ASGITransport(app=app))` — no live server needed. The `auth_headers` fixture in `conftest.py` mints a JWT and must be passed to all authenticated endpoints.

Docker Compose services: `pgvector/pgvector:pg16` (postgres with vector extension), `redis:7-alpine`, and `langfuse/langfuse:latest` on port 3000. Copy `.env.example` → `.env` before `docker compose up`.

CI (projet-3 has the reference workflow at `.github/workflows/ci.yml`) runs lint → typecheck → test → build/push to GHCR on `main`. CD (`.github/workflows/cd.yml`) applies `helm upgrade` after the image push.

## Architecture patterns shared across projects

Every project follows the same layered FastAPI structure:

```
app/
  main.py          — FastAPI app, lifespan (tracing setup, DB teardown)
  config.py        — pydantic-settings, all config from env
  api/             — routers + dependency injection (deps.py)
  schemas/         — Pydantic I/O models
  db/              — SQLAlchemy async models + session
  observability/   — OTel tracing, Prometheus metrics, structured logging
```

### projet-1 — LangGraph supervisor pattern
`app/agents/graph.py` builds a `StateGraph` with a central `supervisor` node that dispatches to specialist nodes (`rag`, `tool`, `memory`) via conditional edges; all specialist nodes loop back to the supervisor. `AgentState` (TypedDict) is the shared state passed through the graph. RAG retriever lives in `app/rag/`, Redis-backed short-term memory in `app/memory/cache.py`, JWT auth + guardrails in `app/security/`.

### projet-2 — OPA policy-as-code + multi-tenancy
`app/core/guardrails/engine.py` chains NeMo Guardrails and `llamaguard.py`. `app/core/policy/opa_client.py` queries the OPA sidecar HTTP API; `app/core/policy/evaluator.py` is the pre-call gate invoked by `app/agents/runner.py` before every tool call. OPA/Rego policies live in `policies/`. `app/core/tenancy/isolation.py` enforces per-tenant DB row-level separation. Audit events written via `app/core/audit/`.

### projet-3 — Kubernetes-first observability
`monitoring/otel-collector.yaml` + `monitoring/prometheus.yml` define the telemetry pipeline. Helm chart in `helm/intel-agent/` with separate `values.prod.yaml`. CD workflow (`.github/workflows/cd.yml`) pushes to GHCR then applies Helm upgrade.

### projet-4 — Self-correcting RAG pipeline
`app/rag/pipeline.py` orchestrates a grader → rewriter → generator loop: `grader.py` scores retrieval relevance, `rewriter.py` reformulates the query on low scores, `generator.py` synthesises the final answer. Multiple ingestion sources in `app/ingestion/` (PDF, web, SQL, Notion). Ragas evaluation harness in `app/evaluation/ragas_eval.py`.

## When building any project here

- Every project README must include: architecture diagram, technical choices rationale, challenges met, and quantified metrics (latency, cost, accuracy, scale)
- Always wire up Docker Compose for local dev and provide a Kubernetes/Helm path for production
- Include a working demo (Streamlit/Gradio UI or recorded Loom) — recruiters won't run your code
- Prioritize `projet-1/` and `projet-2/` — they cover the most required skills from the job description
