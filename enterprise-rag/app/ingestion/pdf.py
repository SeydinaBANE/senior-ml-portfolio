from pathlib import Path

from pypdf import PdfReader

from app.ingestion.store import ingest_chunks


def _chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += chunk_size - overlap
    return chunks


async def ingest_pdf(path: Path) -> int:
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    chunks = _chunk_text(text)
    await ingest_chunks(
        chunks=chunks,
        source="pdf",
        source_id=path.name,
        metadata={"filename": path.name, "pages": len(reader.pages)},
    )
    return len(chunks)
