from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient

from app.schemas.summarize import SummaryResponse


@pytest.mark.asyncio
async def test_summarize_endpoint(client: AsyncClient) -> None:
    mock_response = SummaryResponse(summary="A nice summary.", tokens_used=80, latency_ms=200, model="gpt-4o")

    with patch("app.api.routes.summarize.summarize_document", new_callable=AsyncMock, return_value=mock_response):
        response = await client.post(
            "/api/v1/summarize",
            json={"content": "x" * 100, "language": "en"},
        )

    assert response.status_code == 200
    assert response.json()["summary"] == "A nice summary."


@pytest.mark.asyncio
async def test_summarize_rejects_short_content(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/summarize",
        json={"content": "too short", "language": "en"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
