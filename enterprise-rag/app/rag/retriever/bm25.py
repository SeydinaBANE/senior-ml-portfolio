from dataclasses import dataclass

from rank_bm25 import BM25Okapi
from sqlalchemy import select

from app.db.models import Document
from app.db.session import async_session
from app.rag.retriever.vector import ScoredChunk


def _tokenize(text: str) -> list[str]:
    return text.lower().split()


async def bm25_search(query: str, top_k: int) -> list[ScoredChunk]:
    async with async_session() as db:
        result = await db.execute(select(Document.content, Document.source, Document.metadata))
        rows = result.fetchall()

    if not rows:
        return []

    corpus = [_tokenize(r[0]) for r in rows]
    bm25 = BM25Okapi(corpus)
    scores = bm25.get_scores(_tokenize(query))

    indexed = sorted(
        zip(scores, rows), key=lambda x: x[0], reverse=True
    )[:top_k]

    return [
        ScoredChunk(content=row[0], score=float(score), source=row[1], metadata=row[2])
        for score, row in indexed
        if score > 0
    ]
