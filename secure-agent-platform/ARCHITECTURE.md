# Secure Agent Platform — Architecture

## Overview

Policy-as-code AI platform with 3-layer safety: prompt injection detection (regex + LLM fallback), LlamaGuard content safety, and OPA/Rego policy evaluation via sidecar. Multi-tenant isolation enforced at DB and policy levels.

## Request lifecycle (10 steps)

```
POST /api/v1/agents/run
  → 1. JWT auth → tenant_id + user_id
  → 2. assert_agent_belongs_to_tenant()    (DB check)
  → 3. check_agent_access()                (OPA policy)
  → 4. check_input()                       (regex + LLM injection)
  → 5. llamaguard.classify(role="user")    (content safety)
  → 6. audit: AGENT_INVOKED
  → 7. ChatOpenAI.ainvoke()                (LLM)
  → 8. check_output()                      (llamaguard)
  → 9. audit: AGENT_COMPLETED
  → 10. return AgentRunResponse
```

## Code map

| Path | Responsibility |
|---|---|
| `app/main.py` | FastAPI app + lifespan (tracing, Prometheus metrics server) |
| `app/config.py` | `Settings` — all env-driven config, including `OPA_URL` |
| `app/api/deps.py` | `get_current_user`, `get_tenant_id`, `require_admin` — JWT -> role |
| `app/api/routes/health.py` | `GET /health` |
| `app/api/routes/agents.py` | `POST /api/v1/agents/run` — thin wrapper around `run_agent()` |
| `app/api/routes/admin.py` | CRUD: tenants, agents, audit log listing (admin-only) |
| `app/db/models.py` | `Tenant` (allowed_agents JSON), `Agent`, `AuditLog` |
| `app/db/session.py` | Async engine + session factory |
| `app/schemas/agent.py` | `AgentRunRequest` (agent_id, message), `AgentRunResponse` |
| `app/schemas/admin.py` | `TenantCreate/Response`, `AgentCreate/Response`, `AuditLogEntry` |
| `app/schemas/policy.py` | `AgentAccessInput`, `DataClassificationInput` (for OPA) |
| `app/agents/runner.py` | `run_agent()` — orchestrates the full 10-step pipeline |
| `app/core/policy/opa_client.py` | `OPAClient` singleton — HTTP POST to OPA sidecar with tenacity retry (3 attempts) |
| `app/core/policy/evaluator.py` | `check_agent_access()`, `check_data_classification()` |
| `app/core/guardrails/injection.py` | `PromptInjectionDetector` — 8 regex patterns + LLM fallback |
| `app/core/guardrails/llamaguard.py` | `LlamaGuardClient` — LLM-based SAFE/UNSAFE classifier |
| `app/core/guardrails/engine.py` | `check_input()`, `check_output()` — orchestrates injection + llamaguard |
| `app/core/audit/logger.py` | `log_event()` — immutable JSONL audit trail to PostgreSQL |
| `app/core/audit/models.py` | `AuditEventType` enum (6 event types) |
| `app/core/tenancy/isolation.py` | `resolve_tenant()`, `assert_agent_belongs_to_tenant()` |
| `app/observability/metrics.py` | 4 Prometheus metrics: latency, tokens, guardrail violations, policy denials |
| `app/observability/tracing.py` | OTel TracerProvider with console exporter |

## OPA integration

- **Sidecar container**: `openpolicyagent/opa:latest` on port 8181
- **Policies**: `policies/agent_access.rego` (tenant allowlist) + `policies/data_classification.rego` (clearance levels)
- **Data**: Tenant-specific allowlists loaded via `PUT /v1/data/tenants` at runtime
- **Client**: HTTP POST to `{OPA_URL}/v1/data/platform.agent_access` — tenacity retry with 0.5s exponential backoff
- **Policy result**: `{"result": {"allow": bool, "reason": str}}`

## Multi-tenancy

3 layers: JWT claim (`tenant_id`) → DB row filtering (`WHERE tenant_id = ?`) → OPA policy (tenant allowlist).

## DB models

```
tenants: id, name, allowed_agents (JSON), created_at
agents:  id (PK, e.g. "agent-gpt4o"), tenant_id (FK), name, description, config (JSON)
audit_logs: id, tenant_id (FK), user_id, agent_id, event_type, payload (JSON), verdict, occurred_at
```

## Tests

| File | Tests | What |
|---|---|---|
| `conftest.py` | — | `tenant_id`, `auth_headers` (JWT minted via jose), `client` (ASGITransport) |
| `test_api/test_agents.py` | 2 | Run success (mocked), requires auth |
| `test_api/test_admin.py` | 4 | Create tenant/list (admin vs non-admin) |
| `test_policy/test_opa_client.py` | 2 | OPA allow/deny via respx |
| `test_tenancy/test_isolation.py` | 4 | Resolve tenant found/not-found, agent belongs ok/wrong |
| `test_guardrails/test_injection.py` | 5 | Regex hits (3), safe via LLM, LLM catches subtle |
| `test_guardrails/test_engine.py` | 2 | check_input safe/unsafe increments metric |

Note: NeMo Guardrails is in pyproject.toml deps but NOT used in code. The project implements its own guardrails system.

## Cross-cutting foundations

Shared production foundations wired into every layer of this project:

- **Structured logging** — `app/observability/logging.py`: `setup_logging()` (structlog → JSON) and `get_logger()`, with `request_id` propagated via contextvars. Initialised in the FastAPI lifespan.
- **Observability** — `app/observability/__init__.py`: in-memory `METRICS` counters and `record_span()` timing, offline-friendly and swappable for Prometheus/Langfuse without changing call sites.
- **Governance** — `app/governance.py`: `RBACPolicy.authorize` (role→permission, raises `AccessDeniedError`), `mask_pii`, `IdempotencyGuard`, and an append-only `AuditLog`.
- **LLM gateway** — `app/gateway.py` + `app/schemas/llm.py`: provider-agnostic `LLMGateway` with a deterministic offline `LocalProvider`, an OpenAI/LiteLLM-compatible `HttpLLMProvider`, automatic primary→fallback and streaming.

Known technical debt is tracked in [`DETTE-TECHNIQUE.md`](./DETTE-TECHNIQUE.md).
