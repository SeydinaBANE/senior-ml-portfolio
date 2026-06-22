from uuid import UUID

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(..., min_length=1, max_length=255)


class ChatResponse(BaseModel):
    answer: str
    session_id: str
    sources: list[str] = Field(default_factory=list)
    tenant_id: UUID
