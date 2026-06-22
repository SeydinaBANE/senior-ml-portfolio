from unittest.mock import AsyncMock, patch

import pytest

from app.rag.generator import GeneratedAnswer
from app.rag.pipeline import run_rag
from app.rag.retriever.vector import ScoredChunk


def _chunk(content: str) -> ScoredChunk:
    return ScoredChunk(content=content, score=0.9, source="test", metadata={})


@pytest.mark.asyncio
async def test_pipeline_returns_answer_on_first_iteration() -> None:
    chunks = [_chunk("Relevant content about X.")]

    with (
        patch("app.rag.pipeline.hybrid_search", new_callable=AsyncMock, return_value=chunks),
        patch("app.rag.pipeline.filter_relevant_chunks", new_callable=AsyncMock, return_value=chunks),
        patch(
            "app.rag.pipeline.generate_answer",
            new_callable=AsyncMock,
            return_value=GeneratedAnswer(answer="X is Y.", has_sufficient_context=True),
        ),
    ):
        answer, returned_chunks, iterations = await run_rag("What is X?")

    assert answer == "X is Y."
    assert iterations == 1


@pytest.mark.asyncio
async def test_pipeline_rewrites_on_no_relevant_chunks() -> None:
    chunks = [_chunk("Unrelated content.")]
    rewritten_chunks = [_chunk("Very relevant content.")]
    call_count = 0

    async def search_side_effect(query: str) -> list[ScoredChunk]:
        nonlocal call_count
        call_count += 1
        return rewritten_chunks if call_count > 1 else chunks

    with (
        patch("app.rag.pipeline.hybrid_search", side_effect=search_side_effect),
        patch(
            "app.rag.pipeline.filter_relevant_chunks",
            new_callable=AsyncMock,
            side_effect=[[], rewritten_chunks],
        ),
        patch("app.rag.pipeline.rewrite_query", new_callable=AsyncMock, return_value="better query"),
        patch(
            "app.rag.pipeline.generate_answer",
            new_callable=AsyncMock,
            return_value=GeneratedAnswer(answer="Found it.", has_sufficient_context=True),
        ),
    ):
        answer, _, iterations = await run_rag("What is X?")

    assert answer == "Found it."
    assert iterations == 2
