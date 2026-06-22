from typing import Annotated, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class VerifiedSource(BaseModel):
    url: str
    title: str
    excerpt: str
    confidence: float
    verified: bool = False


class ResearchState(BaseModel):
    topic: str
    search_queries: list[str] = Field(default_factory=list)
    raw_results: list[dict] = Field(default_factory=list)
    verified_sources: list[VerifiedSource] = Field(default_factory=list)
    messages: Annotated[list[BaseMessage], add_messages] = Field(default_factory=list)
    report_draft: str = ""
    iteration: int = 0
    next: Literal["plan", "search", "verify", "write", "review", "__end__"] = "plan"
