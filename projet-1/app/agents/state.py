from typing import Annotated, Literal
from uuid import UUID

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class AgentState(BaseModel):
    messages: Annotated[list[BaseMessage], add_messages] = Field(default_factory=list)
    tenant_id: UUID
    session_id: str
    next_agent: Literal["rag", "tool", "memory", "supervisor", "__end__"] = "supervisor"
    context_chunks: list[str] = Field(default_factory=list)
    iteration_count: int = 0
