# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

This workspace is a portfolio preparation kit for a **Senior Agentic AI Engineer** job application. It contains:

- `offre.md` — the full job description (in French) with technical requirements
- `CONSEIL.md` — key advice: emphasize production readiness, quantify results, add demos, write detailed READMEs
- `projet-1.md` through `projet-6.md` — six portfolio project briefs to build and showcase

## Target role requirements (from `offre.md`)

Core stack: **Python, LangGraph/LangChain, FastAPI, Docker, Kubernetes, CI/CD (GitHub Actions)**

Key themes to demonstrate in every project:
- Production-grade observability: OpenTelemetry, Langfuse, Prometheus + Grafana
- Security: prompt injection protection, multi-tenancy with strong isolation, OWASP Top 10 for LLMs
- Governance: OPA/Rego policy-as-code, audit trails, reproducibility
- Quality: Pydantic structured output, typed Python, tests, CI/CD pipelines

## Project briefs summary

| File | Project |
|---|---|
| `projet-1.md` | Multi-agent enterprise assistant (LangGraph supervisor + RAG + FastAPI + PostgreSQL + Redis) |
| `projet-2.md` | Secure AI agent platform with OPA/Rego policy-as-code, NeMo Guardrails, multi-tenancy |
| `projet-3.md` | Production agent on Kubernetes with Helm, GitHub Actions CI/CD, full observability stack |
| `projet-4.md` | Enterprise-grade RAG with hybrid search, self-correction, Ragas evaluation |
| `projet-5.md` | Full agentic platform (agent marketplace, low-code builder, RBAC, usage tracking) |
| `projet-6.md` | Tool-calling agent (Gmail, Calendar, Slack…) or open-source contribution to LangGraph/guardrails |

## When building any project here

- Every project README must include: architecture diagram, technical choices rationale, challenges met, and quantified metrics (latency, cost, accuracy, scale)
- Always wire up Docker Compose for local dev and provide a Kubernetes/Helm path for production
- Include a working demo (Streamlit/Gradio UI or recorded Loom) — recruiters won't run your code
- Prioritize `projet-1.md` and `projet-2.md` — they cover the most required skills from the job description
