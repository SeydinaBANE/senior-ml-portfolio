from unittest.mock import AsyncMock, patch

import pytest

from app.tools.verifier import VerificationResult, verify_source


@pytest.mark.asyncio
async def test_verify_source_supports_claim() -> None:
    mock_schema = AsyncMock()
    mock_schema.supports = True
    mock_schema.confidence = 0.88
    mock_schema.excerpt = "The study confirms X."

    with (
        patch("app.tools.verifier.fetch_page_text", new_callable=AsyncMock, return_value="The study confirms X in detail."),
        patch("app.tools.verifier._llm.ainvoke", new_callable=AsyncMock, return_value=mock_schema),
    ):
        result = await verify_source("https://example.com/study", "X is true")

    assert result.supports is True
    assert result.confidence == 0.88
    assert result.excerpt == "The study confirms X."


@pytest.mark.asyncio
async def test_verify_source_fetch_failure_returns_unverified() -> None:
    with patch(
        "app.tools.verifier.fetch_page_text",
        new_callable=AsyncMock,
        side_effect=Exception("Connection timeout"),
    ):
        result = await verify_source("https://unreachable.example.com", "some claim")

    assert result.supports is False
    assert result.confidence == 0.0
