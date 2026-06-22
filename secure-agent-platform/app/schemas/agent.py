from uuid import UUID

from pydantic import BaseModel, Field


class AgentRunRequest(BaseModel):
    agent_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1, max_length=4000)


class AgentRunResponse(BaseModel):
    agent_id: str
    output: str
    latency_ms: int
    tenant_id: UUID
