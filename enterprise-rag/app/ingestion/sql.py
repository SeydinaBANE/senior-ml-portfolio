from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.ingestion.store import ingest_chunks


async def ingest_sql_table(
    connection_url: str, query: str, text_columns: list[str], source_id: str
) -> int:
    engine = create_async_engine(connection_url)
    async with engine.connect() as conn:
        result = await conn.execute(text(query))
        rows = result.fetchall()
        keys = list(result.keys())

    chunks = []
    for row in rows:
        row_dict = dict(zip(keys, row))
        chunk = " | ".join(
            f"{col}: {row_dict[col]}" for col in text_columns if col in row_dict
        )
        if chunk.strip():
            chunks.append(chunk)

    await ingest_chunks(
        chunks=chunks,
        source="sql",
        source_id=source_id,
        metadata={"query": query, "row_count": len(rows)},
    )
    await engine.dispose()
    return len(chunks)
