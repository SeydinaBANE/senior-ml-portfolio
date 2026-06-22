from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.schemas.intelligence import IntelResponse


@pytest.mark.asyncio
async def test_intelligence_endpoint(client: AsyncClient) -> None:
    mock_response = IntelResponse(
        query="OpenAI strategy",
        report="Recent developments:\n- GPT-5 launched\nConfidence: high.",
        tokens_used=300,
        sources_searched=True,
    )

    with patch(
        "app.api.routes.intelligence.gather_intelligence",
        new_callable=AsyncMock,
        return_value=mock_response,
    ):
        response = await client.post(
            "/api/v1/intelligence",
            json={"query": "OpenAI strategy"},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "OpenAI strategy"
    assert data["sources_searched"] is True
    assert data["tokens_used"] == 300


@pytest.mark.asyncio
async def test_intelligence_rejects_short_query(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/intelligence",
        json={"query": "ab"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_intelligence_rejects_empty_query(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/intelligence",
        json={"query": ""},
    )
    assert response.status_code == 422
