from unittest.mock import AsyncMock, patch
from uuid import UUID

import pytest
from httpx import AsyncClient

from app.schemas.agent import AgentRunResponse


@pytest.mark.asyncio
async def test_run_agent_success(client: AsyncClient, auth_headers: dict, tenant_id: UUID) -> None:
    mock_response = AgentRunResponse(
        agent_id="agent-1", output="Done!", latency_ms=120, tenant_id=tenant_id
    )
    with patch("app.api.routes.agents.run_agent", new_callable=AsyncMock, return_value=mock_response):
        response = await client.post(
            "/api/v1/agents/run",
            json={"agent_id": "agent-1", "message": "Do something"},
            headers=auth_headers,
        )
    assert response.status_code == 200
    assert response.json()["output"] == "Done!"


@pytest.mark.asyncio
async def test_run_agent_requires_auth(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/agents/run",
        json={"agent_id": "agent-1", "message": "Do something"},
    )
    assert response.status_code == 403
