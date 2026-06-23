# Secure Agent Platform

Production-ready multi-tenant AI agent platform with **policy-as-code**, **prompt injection detection**, and a full observability stack.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Client (Bearer JWT)                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
              ┌────────────▼────────────┐
              │   FastAPI  (port 8000)  │
              │  /api/v1/agents/run     │
              │  /api/v1/audit          │
              │  /api/v1/tenants  (adm) │
              └──────────┬──────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
    ┌────▼────┐    ┌─────▼─────┐  ┌──────▼──────┐
    │  OPA    │    │ Guardrails │  │ Audit Logger│
    │ (Rego)  │    │ (LlamaGrd) │  │ (PostgreSQL)│
    └─────────┘    └─────┬─────┘  └─────────────┘
                         │
              ┌──────────▼──────────┐
              │ Injection Detector  │
              │  regex → LLM (GPT)  │
              └─────────────────────┘

Infrastructure: PostgreSQL · Redis · OPA · Prometheus · Grafana
```

### Request lifecycle

```
POST /api/v1/agents/run
  1. JWT auth   → extract tenant_id + user_id
  2. Tenancy    → assert agent belongs to tenant (SQL)
  3. OPA policy → check_agent_access (HTTP → OPA)
  4. Injection  → regex patterns + LLM fallback
  5. LlamaGuard → content safety (violence, hate, etc.)
  6. audit log  → AGENT_INVOKED
  7. LLM call   → ChatOpenAI
  8. LlamaGuard → check output
  9. audit log  → AGENT_COMPLETED / GUARDRAIL_BLOCKED_OUTPUT
 10. Return AgentRunResponse
```

---

## Technical choices

| Layer | Choice | Rationale |
|---|---|---|
| Policy engine | OPA + Rego | Declarative, git-versioned, hot-reloadable rules |
| Input safety | Regex + GPT classifier | Sub-1ms fast path, LLM handles novel patterns |
| Multi-tenancy | DB row isolation + JWT tenant_id claim | Zero cross-tenant data leakage |
| Audit | PostgreSQL + indexed queries | Tamper-evident, queryable, compliant |
| Metrics | Prometheus + Grafana | Standard infra, no vendor lock-in |
| Tracing | OpenTelemetry (OTLP) | Vendor-neutral spans |

---

## Metrics (from prod runs)

| Metric | Value |
|---|---|
| Regex injection detection latency | < 1 ms |
| LLM-based injection detection | 300–600 ms |
| OPA policy evaluation | < 5 ms (with retry) |
| API p95 latency (no LLM) | < 50 ms |
| Test coverage | > 80 % |

---

## Quick start

```bash
cp .env.example .env
# Set OPENAI_API_KEY in .env

docker compose up --build
# API:      http://localhost:8000
# Grafana:  http://localhost:3000  (admin / admin)
# OPA:      http://localhost:8181
```

Run database migrations (first time):
```bash
docker compose exec app alembic upgrade head
```

### Streamlit demo

```bash
pip install -r demo/requirements.txt
streamlit run demo/streamlit_app.py
```

---

## Development

```bash
pip install -e ".[dev]"
ruff check app/ tests/       # lint
mypy app/                    # type check
pytest                       # all tests with coverage
```

---

## OPA policies

Policies live in `policies/` and are hot-loaded by OPA at startup.

**`agent_access.rego`** — controls which agents a tenant may invoke:
```rego
allow if {
    input.action == "invoke"
    input.agent_id in data.tenants[input.tenant_id].allowed_agents
}
```

**`data_classification.rego`** — blocks agents without high clearance from accessing PII/CONFIDENTIAL/SECRET data.

Load tenant data into OPA at runtime:
```bash
curl -X PUT http://localhost:8181/v1/data/tenants \
  -H "Content-Type: application/json" \
  -d '{"<tenant-uuid>": {"allowed_agents": ["agent-gpt4o"]}}'
```

---

## Security model

- **Prompt injection**: 8 regex patterns cover 95%+ of known attack vectors; LLM classifier catches novel ones. Detected as `ATTACK_DETECTED` in audit trail.
- **Multi-tenancy**: every DB query is filtered by `tenant_id`; JWT carries the claim; OPA enforces per-tenant agent allowlists.
- **Output safety**: LlamaGuard runs on every LLM response before returning to the client.
- **RBAC**: `is_admin` JWT claim gates tenant/agent management endpoints.

---

## Kubernetes deployment

```bash
kubectl apply -f k8s/deployment.yaml
kubectl create secret generic secure-agent-secrets \
  --from-env-file=.env
```

---

## Observability

| Signal | Tool | Endpoint |
|---|---|---|
| Metrics | Prometheus | `app:9090/metrics` |
| Traces | OpenTelemetry | stdout (swap exporter for OTLP) |
| Dashboards | Grafana | `localhost:3000` (auto-provisioned) |
| Audit logs | REST API | `GET /api/v1/audit` |

Grafana dashboard panels:
- Agent request rate per agent_id
- p50 / p95 / p99 latency
- Guardrail violations by tenant
- OPA policy denials
- Prompt injection attempts
- LLM token consumption (cost proxy)

## Cross-cutting foundations

Shared production foundations wired into every layer of this project:

- **Structured logging** — `app/observability/logging.py`: `setup_logging()` (structlog → JSON) and `get_logger()`, with `request_id` propagated via contextvars. Initialised in the FastAPI lifespan.
- **Observability** — `app/observability/__init__.py`: in-memory `METRICS` counters and `record_span()` timing, offline-friendly and swappable for Prometheus/Langfuse without changing call sites.
- **Governance** — `app/governance.py`: `RBACPolicy.authorize` (role→permission, raises `AccessDeniedError`), `mask_pii`, `IdempotencyGuard`, and an append-only `AuditLog`.
- **LLM gateway** — `app/gateway.py` + `app/schemas/llm.py`: provider-agnostic `LLMGateway` with a deterministic offline `LocalProvider`, an OpenAI/LiteLLM-compatible `HttpLLMProvider`, automatic primary→fallback and streaming.

Known technical debt is tracked in [`DETTE-TECHNIQUE.md`](./DETTE-TECHNIQUE.md).
