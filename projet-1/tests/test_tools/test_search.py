from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.tools.search import web_search_tool


@pytest.mark.asyncio
async def test_web_search_returns_answer_field() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Answer": "Python est un langage de programmation interprété.",
        "AbstractText": "",
        "RelatedTopics": [],
    }

    with patch("app.tools.search.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await web_search_tool.ainvoke({"query": "Python programming"})

    assert "Python est un langage" in result


@pytest.mark.asyncio
async def test_web_search_falls_back_to_abstract_text() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Answer": "",
        "AbstractText": "FastAPI is a modern web framework.",
        "RelatedTopics": [],
    }

    with patch("app.tools.search.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await web_search_tool.ainvoke({"query": "FastAPI"})

    assert "FastAPI is a modern web framework." in result


@pytest.mark.asyncio
async def test_web_search_returns_no_results_message() -> None:
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "Answer": "",
        "AbstractText": "",
        "RelatedTopics": [],
    }

    with patch("app.tools.search.httpx.AsyncClient") as mock_cls:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
        mock_cls.return_value.__aexit__ = AsyncMock(return_value=False)

        result = await web_search_tool.ainvoke({"query": "xyzzy_nonexistent"})

    assert "No results found" in result
