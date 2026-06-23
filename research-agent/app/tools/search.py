from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING

from langchain_core.tools import tool

from app.config import settings

if TYPE_CHECKING:
    from tavily import TavilyClient


@lru_cache(maxsize=1)
def _get_client() -> TavilyClient:
    if not settings.tavily_api_key:
        raise RuntimeError("TAVILY_API_KEY not configured")
    from tavily import TavilyClient

    return TavilyClient(api_key=settings.tavily_api_key)


@dataclass
class SearchResult:
    url: str
    title: str
    content: str
    score: float


async def web_search(query: str, max_results: int | None = None) -> list[SearchResult]:
    client = _get_client()
    k = max_results or settings.max_sources_per_query
    response = client.search(query=query, max_results=k, include_raw_content=False)

    threshold = settings.min_source_confidence
    return [
        SearchResult(
            url=r.get("url", ""),
            title=r.get("title", ""),
            content=r.get("content", ""),
            score=float(r.get("score", 0.0)),
        )
        for r in response.get("results", [])
        if float(r.get("score", 0.0)) >= threshold
    ]


@tool
async def search_tool(query: str) -> str:
    """Search the web for information about a topic."""
    results = await web_search(query)
    return "\n\n".join(f"[{r.title}]({r.url})\n{r.content}" for r in results)
