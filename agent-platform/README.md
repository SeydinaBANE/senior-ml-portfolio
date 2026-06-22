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
