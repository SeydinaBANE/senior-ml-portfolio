from unittest.mock import AsyncMock, patch

import pytest

from app.agent.graph import plan_node, verify_node
from app.agent.state import ResearchState
from app.tools.search import SearchResult


@pytest.mark.asyncio
async def test_plan_node_generates_queries() -> None:
    from app.agent.graph import _QueryPlan

    mock_plan = _QueryPlan(queries=["query A", "query B", "query C"])
    state = ResearchState(topic="AI in healthcare")

    with patch("app.agent.graph._llm") as mock_llm:
        mock_llm.with_structured_output.return_value.ainvoke = AsyncMock(return_value=mock_plan)
        result = await plan_node(state)

    assert len(result.search_queries) == 3
    assert result.next == "search"


@pytest.mark.asyncio
async def test_verify_node_filters_low_confidence_sources() -> None:
    from app.tools.verifier import VerificationResult

    state = ResearchState(
        topic="AI in healthcare",
        raw_results=[
            {"url": "https://good.com", "title": "Good Source", "content": "...", "score": 0.9, "query": "q1"},
            {"url": "https://bad.com", "title": "Bad Source", "content": "...", "score": 0.4, "query": "q1"},
        ],
    )

    async def mock_verify(url: str, claim: str) -> VerificationResult:
        if "good" in url:
            return VerificationResult(url=url, supports=True, confidence=0.85, excerpt="Good excerpt")
        return VerificationResult(url=url, supports=False, confidence=0.2, excerpt="")

    with patch("app.agent.graph.verify_source", side_effect=mock_verify):
        result = await verify_node(state)

    assert len(result.verified_sources) == 1
    assert result.verified_sources[0].url == "https://good.com"
    assert result.next == "write"
