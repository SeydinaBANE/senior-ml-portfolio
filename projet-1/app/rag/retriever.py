from uuid import UUID

from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text

from app.config import settings
from app.db.session import async_session

_embeddings = OpenAIEmbeddings(
    model=settings.embedding_model, api_key=settings.openai_api_key
)

TOP_K = 5


async def retrieve(query: str, tenant_id: UUID) -> list[str]:
    vector = await _embeddings.aembed_query(query)
    async with async_session() as session:
        result = await session.execute(
            text(
                """
                SELECT content FROM documents
                WHERE tenant_id = :tenant_id
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :k
                """
            ),
            {"tenant_id": str(tenant_id), "embedding": vector, "k": TOP_K},
        )
        return [row[0] for row in result.fetchall()]


async def index_document(
    content: str, metadata: dict[str, str], tenant_id: UUID
) -> None:
    vector = await _embeddings.aembed_query(content)
    async with async_session() as session:
        await session.execute(
            text(
                """
                INSERT INTO documents (content, metadata, embedding, tenant_id)
                VALUES (:content, :metadata, CAST(:embedding AS vector), :tenant_id)
                """
            ),
            {
                "content": content,
                "metadata": metadata,
                "embedding": vector,
                "tenant_id": str(tenant_id),
            },
        )
        await session.commit()
