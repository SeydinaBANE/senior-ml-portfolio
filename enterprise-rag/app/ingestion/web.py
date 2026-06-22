import httpx
from bs4 import BeautifulSoup

from app.ingestion.store import ingest_chunks


async def ingest_url(url: str, chunk_size: int = 1000) -> int:
    async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
        response = await client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    await ingest_chunks(
        chunks=chunks,
        source="web",
        source_id=url,
        metadata={"url": url, "title": soup.title.string if soup.title else ""},
    )
    return len(chunks)
