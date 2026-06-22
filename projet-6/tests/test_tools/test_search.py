from unittest.mock import MagicMock, patch

import pytest

from app.tools.search import SearchResult, web_search


@pytest.mark.asyncio
async def test_web_search_filters_by_confidence() -> None:
    mock_response = {
        "results": [
            {"url": "https://a.com", "title": "A", "content": "Content A", "score": 0.9},
            {"url": "https://b.com", "title": "B", "content": "Content B", "score": 0.3},
        ]
    }
    mock_client = MagicMock()
    mock_client.search.return_value = mock_response

    with patch("app.tools.search._client", mock_client):
        results = await web_search("test query", max_results=5)

    assert all(r.score >= 0.6 for r in results)
    assert len(results) == 1
    assert results[0].url == "https://a.com"


@pytest.mark.asyncio
async def test_web_search_raises_without_api_key() -> None:
    with patch("app.tools.search._client", None):
        with pytest.raises(RuntimeError, match="TAVILY_API_KEY"):
            await web_search("test")
