from pydantic import BaseModel, Field


class SummaryRequest(BaseModel):
    content: str = Field(..., min_length=100, max_length=50_000)
    language: str = Field(default="en", pattern="^[a-z]{2}$")


class SummaryResponse(BaseModel):
    summary: str
    tokens_used: int
    latency_ms: int
    model: str
