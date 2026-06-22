import httpx

from app.config import settings
from app.ingestion.store import ingest_chunks

_BASE = "https://api.notion.com/v1"
_HEADERS = {
    "Authorization": f"Bearer {settings.notion_api_key}",
    "Notion-Version": "2022-06-28",
}


async def _fetch_blocks(page_id: str) -> list[str]:
    async with httpx.AsyncClient(headers=_HEADERS, timeout=10.0) as client:
        resp = await client.get(f"{_BASE}/blocks/{page_id}/children")
        resp.raise_for_status()
        blocks = resp.json().get("results", [])

    texts = []
    for block in blocks:
        block_type = block.get("type", "")
        rich_text = block.get(block_type, {}).get("rich_text", [])
        texts.extend(rt.get("plain_text", "") for rt in rich_text)
    return texts


async def ingest_notion_database() -> int:
    async with httpx.AsyncClient(headers=_HEADERS, timeout=10.0) as client:
        resp = await client.post(
            f"{_BASE}/databases/{settings.notion_database_id}/query",
            json={},
        )
        resp.raise_for_status()
        pages = resp.json().get("results", [])

    total = 0
    for page in pages:
        page_id = page["id"]
        title_prop = next(iter(page.get("properties", {}).values()), {})
        title = title_prop.get("title", [{}])[0].get("plain_text", page_id)

        blocks = await _fetch_blocks(page_id)
        text = "\n".join(blocks)
        if text.strip():
            await ingest_chunks(
                chunks=[text],
                source="notion",
                source_id=page_id,
                metadata={"title": title, "page_id": page_id},
            )
            total += 1
    return total
