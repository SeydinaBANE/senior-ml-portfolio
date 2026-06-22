from dataclasses import dataclass

from langchain_core.tools import tool
from tavily import TavilyClient

from app.config import settings

_client = TavilyClient(api_key=settings.tavily_api_key) if settings.tavily_api_key else None


@dataclass
class SearchResult:
    url: str
    title: str
    content: str
    score: float


async def web_search(query: str, max_results: int | None = None) -> list[SearchResult]:
    if _client is None:
        raise RuntimeError("TAVILY_API_KEY not configured")

    k = max_results or settings.max_sources_per_query
    response = _client.search(query=query, max_results=k, include_raw_content=False)

    return [
        SearchResult(
            url=r.get("url", ""),
            title=r.get("title", ""),
            content=r.get("content", ""),
            score=float(r.get("score", 0.0)),
        )
        for r in response.get("results", [])
    ]


@tool
async def search_tool(query: str) -> str:
    """Search the web for information about a topic."""
    results = await web_search(query)
    return "\n\n".join(f"[{r.title}]({r.url})\n{r.content}" for r in results)
