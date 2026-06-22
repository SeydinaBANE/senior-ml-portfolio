from pydantic import BaseModel, Field


class ResearchRequest(BaseModel):
    topic: str = Field(..., min_length=5, max_length=500)
    post_to_slack: bool = False
    save_to_notion: bool = False
    notion_parent_page_id: str = ""


class SourceSummary(BaseModel):
    url: str
    title: str
    confidence: float
    excerpt: str


class ResearchReport(BaseModel):
    topic: str
    report: str
    verified_sources: list[SourceSummary]
    total_sources_found: int
    total_sources_verified: int
    search_queries_used: int
