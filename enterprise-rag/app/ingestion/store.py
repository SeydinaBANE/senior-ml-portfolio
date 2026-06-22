from langchain_openai import OpenAIEmbeddings
from sqlalchemy import text

from app.config import settings
from app.db.session import async_session

_embeddings = OpenAIEmbeddings(
    model=settings.embedding_model, api_key=settings.openai_api_key
)


async def ingest_chunks(
    chunks: list[str], source: str, source_id: str, metadata: dict
) -> None:
    vectors = await _embeddings.aembed_documents(chunks)
    async with async_session() as db:
        for chunk, vector in zip(chunks, vectors):
            await db.execute(
                text(
                    """
                    INSERT INTO documents (content, source, source_id, metadata, embedding)
                    VALUES (:content, :source, :source_id, :metadata, CAST(:emb AS vector))
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "content": chunk,
                    "source": source,
                    "source_id": source_id,
                    "metadata": metadata,
                    "emb": vector,
                },
            )
        await db.commit()
