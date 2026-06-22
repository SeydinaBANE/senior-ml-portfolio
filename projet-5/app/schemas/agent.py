from uuid import UUID

from pydantic import BaseModel, Field


class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=10, max_length=500)
    category: str = Field(..., min_length=2, max_length=50)
    system_prompt: str = Field(..., min_length=10)
    tools: list[str] = Field(default_factory=list)
    model: str = "gpt-4o"
    tags: list[str] = Field(default_factory=list)
    is_public: bool = False


class AgentResponse(BaseModel):
    id: UUID
    name: str
    description: str
    category: str
    tags: list[str]
    model: str
    is_public: bool
    owner_id: UUID


class AgentUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    tools: list[str] | None = None
    model: str | None = None
    tags: list[str] | None = None
    is_public: bool | None = None


class RunRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=4000)


class RunResponse(BaseModel):
    agent_name: str
    agent_id: UUID
    output: str
    routed_by: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
