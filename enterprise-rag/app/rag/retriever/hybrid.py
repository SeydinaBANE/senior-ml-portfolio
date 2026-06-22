from app.config import settings
from app.rag.retriever.bm25 import bm25_search
from app.rag.retriever.vector import ScoredChunk, vector_search


def _reciprocal_rank_fusion(
    vector_hits: list[ScoredChunk],
    bm25_hits: list[ScoredChunk],
    k: int = 60,
) -> list[ScoredChunk]:
    scores: dict[str, float] = {}
    chunks: dict[str, ScoredChunk] = {}

    for rank, chunk in enumerate(vector_hits):
        scores[chunk.content] = scores.get(chunk.content, 0) + settings.vector_weight / (k + rank + 1)
        chunks[chunk.content] = chunk

    for rank, chunk in enumerate(bm25_hits):
        scores[chunk.content] = scores.get(chunk.content, 0) + settings.bm25_weight / (k + rank + 1)
        chunks[chunk.content] = chunk

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [
        ScoredChunk(
            content=chunks[content].content,
            score=score,
            source=chunks[content].source,
            metadata=chunks[content].metadata,
        )
        for content, score in ranked
    ]


async def hybrid_search(query: str, top_k: int | None = None) -> list[ScoredChunk]:
    k = top_k or settings.top_k_chunks
    vector_hits, bm25_hits = await _parallel_search(query, k)
    return _reciprocal_rank_fusion(vector_hits, bm25_hits)[:k]


async def _parallel_search(
    query: str, k: int
) -> tuple[list[ScoredChunk], list[ScoredChunk]]:
    import asyncio
    return await asyncio.gather(vector_search(query, k), bm25_search(query, k))
