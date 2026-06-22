import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rag.retriever import retrieve


@pytest.mark.asyncio
async def test_retrieve_returns_chunks() -> None:
    tenant_id = uuid.uuid4()
    mock_rows = [("chunk A",), ("chunk B",)]

    with (
        patch("app.rag.retriever._embeddings.aembed_query", new_callable=AsyncMock, return_value=[0.1] * 1536),
        patch("app.rag.retriever.async_session") as mock_session_ctx,
    ):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = mock_rows
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        chunks = await retrieve("test query", tenant_id)

    assert chunks == ["chunk A", "chunk B"]


@pytest.mark.asyncio
async def test_retrieve_returns_empty_on_no_results() -> None:
    tenant_id = uuid.uuid4()

    with (
        patch("app.rag.retriever._embeddings.aembed_query", new_callable=AsyncMock, return_value=[0.0] * 1536),
        patch("app.rag.retriever.async_session") as mock_session_ctx,
    ):
        mock_session = AsyncMock()
        mock_result = MagicMock()
        mock_result.fetchall.return_value = []
        mock_session.execute = AsyncMock(return_value=mock_result)
        mock_session_ctx.return_value.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session_ctx.return_value.__aexit__ = AsyncMock(return_value=False)

        chunks = await retrieve("empty query", tenant_id)

    assert chunks == []
