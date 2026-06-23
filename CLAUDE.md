# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This workspace is a portfolio preparation kit for a **Senior Agentic AI Engineer** job application. It contains:

- `offre.md` — the full job description (in French) with technical requirements
- `CONSEIL.md` — key advice: emphasize production readiness, quantify results, add demos, write detailed READMEs
- `projet-1.md` through `projet-6.md` — six portfolio project briefs to build and showcase
- `enterprise-agent/`, `secure-agent-platform/`, `intel-agent/`, `enterprise-rag/`, `agent-platform/`, `research-agent/` — the actual project implementations

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
| `enterprise-agent/` | Multi-agent enterprise assistant (LangGraph supervisor + RAG + FastAPI + PostgreSQL + Redis) |
| `secure-agent-platform/` | Secure AI agent platform with OPA/Rego policy-as-code, NeMo Guardrails, multi-tenancy |
| `intel-agent/` | Production agent on Kubernetes with Helm, GitHub Actions CI/CD, full observability stack |
| `enterprise-rag/` | Enterprise-grade RAG with hybrid search, self-correction, Ragas evaluation |
| `agent-platform/` | Full agentic platform (agent marketplace, low-code builder, RBAC, usage tracking) |
| `research-agent/` | Autonomous research agent (Gmail, Calendar, Notion, Slack, Tavily, source verification) |

## Dev commands (apply inside each project directory)

All projects use Python 3.12, `hatchling`, `ruff`, `mypy` (strict), and `pytest-asyncio`.

```bash
pip install -e ".[dev]"                        # install with dev extras
ruff format app/ tests/                        # format (run before lint)
ruff check app/ tests/                         # lint (line-length=100, ruleset: E,F,I,UP,N,S,B,A; S101 ignored)
mypy app/                                      # type check (strict=true, ignore_missing_imports=true)
APP_ENV=test pytest                            # all tests with coverage
APP_ENV=test pytest tests/path/test_file.py    # single test file
APP_ENV=test pytest -k "test_name" -v          # single test by name
docker compose up --build                      # local full stack
```

`enterprise-agent`, `secure-agent-platform`, and `agent-platform` use Alembic for DB migrations (run inside the project dir):
```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
```
Layout differs per project: `enterprise-agent` keeps migrations at `app/db/migrations/` with `alembic.ini` at the root; `secure-agent-platform` and `agent-platform` use an `alembic/` directory. `enterprise-rag` has the Alembic dependency but **no** migration setup.

`enterprise-rag`, `agent-platform`, and `research-agent` each ship a Streamlit UI: `streamlit run ui/streamlit_app.py` (or `docker compose up ui`).

Per-project lint nuances on top of the shared ruleset: `agent-platform` also ignores S105, S106, B008; `intel-agent` ignores E402 in `tests/conftest.py`. The root briefs `offre.md`, `CONSEIL.md`, and `projet-*.md` are gitignored — present on disk but excluded from commits.

`APP_ENV=test` is required — the app conditionally skips DB/Redis init in test mode. Tests use `httpx.AsyncClient(transport=ASGITransport(app=app))` — no live server needed. Auth fixtures vary by project, so read each `conftest.py`: `enterprise-agent` and `secure-agent-platform` export `auth_headers` (mints a JWT); `agent-platform` exports role-scoped `admin_headers` / `dev_headers` / `user_headers`; `intel-agent`, `enterprise-rag`, and `research-agent` define no auth fixture.

Docker Compose services: `pgvector/pgvector:pg16` (postgres with vector extension), `redis:7-alpine`, and `langfuse/langfuse:latest` on port 3000. Copy `.env.example` → `.env` before `docker compose up`.

CI (`intel-agent` has the reference workflow at `.github/workflows/ci.yml`) runs lint → typecheck → test → build/push to GHCR on `main`. CD (`.github/workflows/cd.yml`) applies `helm upgrade` after the image push. Workflow coverage varies: `intel-agent` and `agent-platform` have both `ci.yml` + `cd.yml`; `enterprise-agent` and `secure-agent-platform` have `ci.yml` only; `enterprise-rag` and `research-agent` have no `.github/` workflows yet.

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

### enterprise-agent — LangGraph supervisor pattern
`app/agents/graph.py` builds a `StateGraph` with a central `supervisor` node that dispatches to specialist nodes (`rag`, `tool`, `memory`) via conditional edges; all specialist nodes loop back to the supervisor. `AgentState` (TypedDict) is the shared state passed through the graph. RAG retriever lives in `app/rag/`, Redis-backed short-term memory in `app/memory/cache.py`, JWT auth + guardrails in `app/security/`.

### secure-agent-platform — OPA policy-as-code + multi-tenancy
`app/core/guardrails/engine.py` chains NeMo Guardrails and `llamaguard.py`. `app/core/policy/opa_client.py` queries the OPA sidecar HTTP API; `app/core/policy/evaluator.py` is the pre-call gate invoked by `app/agents/runner.py` before every tool call. OPA/Rego policies live in `policies/`. `app/core/tenancy/isolation.py` enforces per-tenant DB row-level separation. Audit events written via `app/core/audit/`.

### intel-agent — Kubernetes-first observability
`monitoring/otel-collector.yaml` + `monitoring/prometheus.yml` define the telemetry pipeline. Helm chart in `helm/intel-agent/` with separate `values.prod.yaml`. CD workflow (`.github/workflows/cd.yml`) pushes to GHCR then applies Helm upgrade.

### enterprise-rag — Self-correcting RAG pipeline
`app/rag/pipeline.py` orchestrates a grader → rewriter → generator loop: `grader.py` scores retrieval relevance, `rewriter.py` reformulates the query on low scores, `generator.py` synthesises the final answer. Multiple ingestion sources in `app/ingestion/` (PDF, web, SQL, Notion). Ragas evaluation harness in `app/evaluation/ragas_eval.py`.

## When building any project here

- Every project README must include: architecture diagram, technical choices rationale, challenges met, and quantified metrics (latency, cost, accuracy, scale)
- Always wire up Docker Compose for local dev and provide a Kubernetes/Helm path for production
- Include a working demo (Streamlit/Gradio UI or recorded Loom) — recruiters won't run your code
- Prioritize `enterprise-agent/` and `secure-agent-platform/` — they cover the most required skills from the job description
