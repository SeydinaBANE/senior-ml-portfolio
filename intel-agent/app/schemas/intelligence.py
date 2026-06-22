from pydantic import BaseModel, Field


class IntelRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)


class IntelResponse(BaseModel):
    query: str
    report: str
    tokens_used: int
    sources_searched: bool
