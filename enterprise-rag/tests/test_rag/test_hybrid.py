import pytest

from app.rag.retriever.hybrid import _reciprocal_rank_fusion
from app.rag.retriever.vector import ScoredChunk


def _chunk(content: str, score: float = 0.9) -> ScoredChunk:
    return ScoredChunk(content=content, score=score, source="test", metadata={})


def test_rrf_merges_and_deduplicates() -> None:
    vector_hits = [_chunk("A"), _chunk("B"), _chunk("C")]
    bm25_hits = [_chunk("B"), _chunk("D"), _chunk("A")]

    result = _reciprocal_rank_fusion(vector_hits, bm25_hits)

    contents = [r.content for r in result]
    assert len(set(contents)) == len(contents), "duplicates found"
    assert contents[0] in ("A", "B"), "top-ranked should be a shared hit"


def test_rrf_respects_weights() -> None:
    vector_only = [_chunk("X")]
    bm25_only = [_chunk("Y")]

    result = _reciprocal_rank_fusion(vector_only, bm25_only)
    assert result[0].content == "X", "vector-only hit should rank higher (higher weight)"
