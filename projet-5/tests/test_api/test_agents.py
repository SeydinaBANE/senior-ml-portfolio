import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import AsyncClient

from app.db.models import AgentDefinition

AGENT_ID = uuid.uuid4()
TENANT_ID = uuid.uuid4()
OWNER_ID = uuid.uuid4()

_AGENT = AgentDefinition(
    id=AGENT_ID,
    name="hr-bot",
    description="Answers HR questions",
    category="hr",
    system_prompt="You are an HR assistant.",
    tools=[],
    model="gpt-4o",
    tags=["hr"],
    is_public=False,
    owner_id=OWNER_ID,
    tenant_id=TENANT_ID,
)


def _mock_session(agent: AgentDefinition | None = _AGENT) -> MagicMock:
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [agent] if agent else []
    mock_result.scalar_one_or_none.return_value = agent
    mock_session = AsyncMock()
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.refresh = AsyncMock()
    ctx = MagicMock()
    ctx.__aenter__ = AsyncMock(return_value=mock_session)
    ctx.__aexit__ = AsyncMock(return_value=False)
    return ctx


@pytest.mark.asyncio
async def test_list_agents_returns_tenant_agents(
    client: AsyncClient, dev_headers: dict[str, str]
) -> None:
    with patch("app.api.routes.agents.async_session", return_value=_mock_session()):
        r = await client.get("/api/v1/agents", headers=dev_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["name"] == "hr-bot"


@pytest.mark.asyncio
async def test_list_agents_forbidden_for_anonymous(client: AsyncClient) -> None:
    r = await client.get("/api/v1/agents")
    assert r.status_code == 403


@pytest.mark.asyncio
async def test_update_agent_returns_updated(
    client: AsyncClient, dev_headers: dict[str, str]
) -> None:
    updated = AgentDefinition(
        id=AGENT_ID,
        name="hr-bot-v2",
        description="Answers HR questions",
        category="hr",
        system_prompt="You are an HR assistant.",
        tools=[],
        model="gpt-4o",
        tags=["hr"],
        is_public=False,
        owner_id=OWNER_ID,
        tenant_id=TENANT_ID,
    )
    with patch("app.api.routes.agents.async_session", return_value=_mock_session(updated)):
        r = await client.put(
            f"/api/v1/agents/{AGENT_ID}",
            json={"name": "hr-bot-v2"},
            headers=dev_headers,
        )
    assert r.status_code == 200
    assert r.json()["name"] == "hr-bot-v2"


@pytest.mark.asyncio
async def test_update_agent_not_found(
    client: AsyncClient, dev_headers: dict[str, str]
) -> None:
    with patch("app.api.routes.agents.async_session", return_value=_mock_session(None)):
        r = await client.put(
            f"/api/v1/agents/{uuid.uuid4()}",
            json={"name": "ghost"},
            headers=dev_headers,
        )
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_update_agent_forbidden_for_user_role(
    client: AsyncClient, user_headers: dict[str, str]
) -> None:
    r = await client.put(
        f"/api/v1/agents/{AGENT_ID}",
        json={"name": "x"},
        headers=user_headers,
    )
    assert r.status_code == 403
