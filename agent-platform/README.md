# Agent Platform — Multi-Tenant Agent SaaS Platform

Full-stack agentic platform with agent marketplace, LLM-based intent routing, RBAC (admin/developer/user), and usage-based billing. Includes a Streamlit UI for marketplace browsing, agent building, and billing dashboards.

## Architecture

```
Request → JWT auth → RBAC enforcer (admin/developer/user)
               ↓
         Intent Router (LLM classifier)
               ↓
         Agent Dispatcher → matched AgentDefinition
               ↓
         Billing Tracker (token count → USD cost)
               ↓
         Audit log + Response
```

## Quick start

```bash
cp .env.example .env
# Fill OPENAI_API_KEY and SECRET_KEY
docker compose up --build

# API:  http://localhost:8000
# UI:   http://localhost:8501
# Docs: http://localhost:8000/docs
```

## API endpoints

| Method | Path | Auth | Permission |
|---|---|---|---|
| `POST` | `/api/v1/auth/register` | — | — |
| `POST` | `/api/v1/auth/login` | — | — |
| `GET` | `/api/v1/agents` | Bearer | `agent:read` |
| `POST` | `/api/v1/agents` | Bearer | `agent:create` |
| `PUT` | `/api/v1/agents/{id}` | Bearer | `agent:update` |
| `DELETE` | `/api/v1/agents/{id}` | Bearer | `agent:delete` |
| `POST` | `/api/v1/run` | Bearer | — |
| `POST` | `/api/v1/billing/report` | Bearer | `billing:read` |

## Development

```bash
pip install -e ".[dev]"
APP_ENV=test pytest
```

## RBAC permissions

| Permission | Admin | Developer | User |
|---|---|---|---|
| `agent:create` | ✅ | ✅ | ❌ |
| `agent:read` | ✅ | ✅ | ✅ |
| `agent:update` | ✅ | ✅ | ❌ |
| `agent:delete` | ✅ | ✅ | ❌ |
| `agent:publish` | ✅ | ❌ | ❌ |
| `billing:read` | ✅ | ✅ | ❌ |
| `user:manage` | ✅ | ❌ | ❌ |

## Cross-cutting foundations

Shared production foundations wired into every layer of this project:

- **Structured logging** — `app/observability/logging.py`: `setup_logging()` (structlog → JSON) and `get_logger()`, with `request_id` propagated via contextvars. Initialised in the FastAPI lifespan.
- **Observability** — `app/observability/__init__.py`: in-memory `METRICS` counters and `record_span()` timing, offline-friendly and swappable for Prometheus/Langfuse without changing call sites.
- **Governance** — `app/governance.py`: `RBACPolicy.authorize` (role→permission, raises `AccessDeniedError`), `mask_pii`, `IdempotencyGuard`, and an append-only `AuditLog`.
- **LLM gateway** — `app/gateway.py` + `app/schemas/llm.py`: provider-agnostic `LLMGateway` with a deterministic offline `LocalProvider`, an OpenAI/LiteLLM-compatible `HttpLLMProvider`, automatic primary→fallback and streaming.

Known technical debt is tracked in [`DETTE-TECHNIQUE.md`](./DETTE-TECHNIQUE.md).
