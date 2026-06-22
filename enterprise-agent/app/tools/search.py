import httpx
from langchain_core.tools import tool


@tool
async def web_search_tool(query: str) -> str:
    """Search the web for up-to-date information on any topic."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            "https://api.duckduckgo.com/",
            params={"q": query, "format": "json", "no_html": "1", "skip_disambig": "1"},
        )
        data = response.json()

    parts = [
        data.get("Answer", ""),
        data.get("AbstractText", ""),
        *[t.get("Text", "") for t in data.get("RelatedTopics", [])[:3]],
    ]
    text = "\n".join(p for p in parts if p)
    return text if text else f"No results found for: {query}"
