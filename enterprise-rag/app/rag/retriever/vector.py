from dataclasses import dataclass

from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text

from app.config import settings
from app.db.session import async_session

_embeddings = OpenAIEmbeddings(model=settings.embedding_model, api_key=settings.openai_api_key)


@dataclass
class ScoredChunk:
    content: str
    score: float
    source: str
    metadata: dict[str, object]


async def vector_search(query: str, top_k: int) -> list[ScoredChunk]:
    vector = await _embeddings.aembed_query(query)
    async with async_session() as db:
        rows = await db.execute(
            text(
                """
                SELECT content, source, metadata,
                       1 - (embedding <=> CAST(:emb AS vector)) AS score
                FROM documents
                ORDER BY embedding <=> CAST(:emb AS vector)
                LIMIT :k
                """
            ),
            {"emb": vector, "k": top_k},
        )
        return [
            ScoredChunk(content=r[0], score=float(r[3]), source=r[1], metadata=r[2])
            for r in rows.fetchall()
        ]
