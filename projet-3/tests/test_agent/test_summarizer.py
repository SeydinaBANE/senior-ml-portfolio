from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.agent.summarizer import summarize_document
from app.schemas.summarize import SummaryRequest, SummaryResponse


def _mock_llm(content: str, tokens: int) -> MagicMock:
    msg = MagicMock()
    msg.content = content
    msg.usage_metadata = {"total_tokens": tokens}
    llm = MagicMock()
    llm.ainvoke = AsyncMock(return_value=msg)
    return llm


@pytest.mark.asyncio
async def test_summarize_returns_response() -> None:
    with patch("app.agent.summarizer._llm", new=_mock_llm("Key points:\n- A\n- B\nConclusion: Good.", 250)):
        result = await summarize_document(SummaryRequest(content="x" * 100, language="en"))

    assert isinstance(result, SummaryResponse)
    assert result.tokens_used == 250
    assert result.latency_ms >= 0


@pytest.mark.asyncio
async def test_summarize_tracks_metrics() -> None:
    with (
        patch("app.agent.summarizer._llm", new=_mock_llm("Summary here.", 100)),
        patch("app.agent.summarizer.summarization_latency") as mock_hist,
        patch("app.agent.summarizer.tokens_consumed_total") as mock_counter,
    ):
        await summarize_document(SummaryRequest(content="x" * 100, language="fr"))

    mock_hist.labels.assert_called_once()
    mock_counter.labels.assert_called_once()
