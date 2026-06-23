from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class TenantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    allowed_agents: list[str] = Field(default_factory=list)


class TenantResponse(BaseModel):
    id: UUID
    name: str
    allowed_agents: list[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class AgentCreate(BaseModel):
    id: str = Field(..., min_length=1, max_length=255, pattern=r"^[a-z0-9_-]+$")
    name: str = Field(..., min_length=1, max_length=255)
    description: str = ""
    config: dict[str, object] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    id: str
    tenant_id: UUID
    name: str
    description: str
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogEntry(BaseModel):
    id: UUID
    user_id: str
    agent_id: str
    event_type: str
    verdict: str | None
    occurred_at: datetime

    model_config = {"from_attributes": True}
