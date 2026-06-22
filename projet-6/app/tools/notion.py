import httpx
from langchain_core.tools import tool

from app.config import settings

_BASE = "https://api.notion.com/v1"
_HEADERS = {
    "Authorization": f"Bearer {settings.notion_api_key}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}


@tool
async def create_notion_page_tool(title: str, content: str, parent_page_id: str) -> str:
    """Create a new Notion page with markdown-style content."""
    payload = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": {"title": [{"text": {"content": title}}]}
        },
        "children": [
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": content[:2000]}}]
                },
            }
        ],
    }
    async with httpx.AsyncClient(headers=_HEADERS, timeout=10.0) as client:
        response = await client.post(f"{_BASE}/pages", json=payload)
        response.raise_for_status()
        data = response.json()
    return f"Page created: {data.get('url', 'unknown URL')}"


@tool
async def search_notion_tool(query: str) -> str:
    """Search Notion for pages matching a query."""
    async with httpx.AsyncClient(headers=_HEADERS, timeout=10.0) as client:
        response = await client.post(f"{_BASE}/search", json={"query": query, "page_size": 5})
        response.raise_for_status()
        results = response.json().get("results", [])

    if not results:
        return "No Notion pages found."
    return "\n".join(
        f"- {r.get('properties', {}).get('title', {}).get('title', [{}])[0].get('plain_text', 'Untitled')}"
        for r in results
    )
