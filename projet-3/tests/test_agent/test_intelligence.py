from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agent.intelligence import gather_intelligence
from app.schemas.intelligence import IntelRequest, IntelResponse


def _mock_llm(content: str, tokens: int) -> MagicMock:
    msg = MagicMock()
    msg.content = content
    msg.usage_metadata = {"total_tokens": tokens}
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=msg)
    return llm


def _mock_search(return_value: str = "search result") -> MagicMock:
    search = MagicMock()
    search.arun = AsyncMock(return_value=return_value)
    return search


@pytest.mark.asyncio
async def test_intelligence_returns_response() -> None:
    with (
        patch("app.agent.intelligence._search", new=_mock_search()),
        patch("app.agent.intelligence._llm", new=_mock_llm("- Fact A\nRisk: X", 320)),
    ):
        result = await gather_intelligence(IntelRequest(query="OpenAI competitors"))

    assert isinstance(result, IntelResponse)
    assert result.tokens_used == 320
    assert result.sources_searched is True
    assert result.query == "OpenAI competitors"


@pytest.mark.asyncio
async def test_intelligence_handles_search_failure() -> None:
    broken_search = MagicMock()
    broken_search.arun = AsyncMock(side_effect=Exception("network error"))

    with (
        patch("app.agent.intelligence._search", new=broken_search),
        patch("app.agent.intelligence._llm", new=_mock_llm("Fallback report", 100)),
        patch("app.agent.intelligence.intelligence_requests_total") as mock_counter,
    ):
        result = await gather_intelligence(IntelRequest(query="some query"))

    assert isinstance(result, IntelResponse)
    mock_counter.labels.assert_any_call(status="search_error")


@pytest.mark.asyncio
async def test_intelligence_tracks_tokens() -> None:
    with (
        patch("app.agent.intelligence._search", new=_mock_search()),
        patch("app.agent.intelligence._llm", new=_mock_llm("Report", 200)),
        patch("app.agent.intelligence.tokens_consumed_total") as mock_tokens,
        patch("app.agent.intelligence.intelligence_requests_total"),
    ):
        await gather_intelligence(IntelRequest(query="test query"))

    mock_tokens.labels.assert_called_once()
