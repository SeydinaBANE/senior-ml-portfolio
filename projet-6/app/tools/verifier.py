from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.config import settings

_SYSTEM = """You are a fact-checker. Given a URL's extracted content and a claim,
assess whether the content actually supports the claim.
Respond with: {"supports": true|false, "confidence": 0.0-1.0, "excerpt": "relevant quote or empty"}"""


class _VerifySchema(BaseModel):
    supports: bool
    confidence: float
    excerpt: str


_llm = ChatOpenAI(
    model=settings.openai_model, api_key=settings.openai_api_key, temperature=0
).with_structured_output(_VerifySchema)


@dataclass
class VerificationResult:
    url: str
    supports: bool
    confidence: float
    excerpt: str


async def fetch_page_text(url: str) -> str:
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "aside"]):
        tag.decompose()
    return soup.get_text(separator=" ", strip=True)[:3000]


async def verify_source(url: str, claim: str) -> VerificationResult:
    try:
        page_text = await fetch_page_text(url)
    except Exception:
        return VerificationResult(url=url, supports=False, confidence=0.0, excerpt="")

    result: _VerifySchema = await _llm.ainvoke(
        [
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=f"Claim: {claim}\n\nPage content:\n{page_text}"),
        ]
    )
    return VerificationResult(
        url=url,
        supports=result.supports,
        confidence=result.confidence,
        excerpt=result.excerpt,
    )
