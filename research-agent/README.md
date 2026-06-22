# Research Agent — Autonomous Research & Report Generator

Autonomous research agent that plans search queries, searches the web (Tavily), verifies sources by fetching and fact-checking page content, writes structured reports, and optionally distributes via Slack and Notion. Includes a Streamlit UI.

## Architecture

```
Topic → Plan (N queries) → Search (parallel Tavily) → Verify (parallel LLM fact-check)
                                                            ↓
                                                       Write (report + citations)
                                                            ↓
                                                       Review (approve / rewrite, max 1×)
                                                            ↓
                                               [optional] Slack post + Notion page
```

## Quick start

```bash
cp .env.example .env
# Fill OPENAI_API_KEY, TAVILY_API_KEY, and optionally Notion/Slack/Google keys

# Google OAuth: place token.json in .secrets/ after first browser auth
docker compose up --build

# API:  http://localhost:8000
# UI:   http://localhost:8501
```

## Integrations

| Service | Auth | Env var |
|---|---|---|
| Tavily | API key | `TAVILY_API_KEY` |
| OpenAI | API key | `OPENAI_API_KEY` |
| Gmail | OAuth2 | `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` |
| Calendar | OAuth2 | (same as Gmail) |
| Notion | Bearer token | `NOTION_API_KEY` |
| Slack | Bot token | `SLACK_BOT_TOKEN` |

## API endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/research` | Run research on a topic |
| `GET` | `/api/v1/tools/status` | Check which integrations are configured |

## Development

```bash
pip install -e ".[dev]"
APP_ENV=test pytest
```
