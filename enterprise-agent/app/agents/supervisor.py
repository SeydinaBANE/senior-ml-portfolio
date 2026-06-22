from typing import Literal

from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from app.agents.state import AgentState
from app.config import settings

_SYSTEM_PROMPT = """You are a supervisor orchestrating specialized agents.
Decide which agent should handle the current request:
- rag: user needs information from the knowledge base
- tool: user needs an external action (API call, database query, search)
- memory: user references past interactions or context
- __end__: the request is fully answered

Respond ONLY with the agent name."""


class RoutingDecision(BaseModel):
    next: Literal["rag", "tool", "memory", "__end__"]


_llm = ChatOpenAI(
    model=settings.openai_model,
    api_key=settings.openai_api_key,
    temperature=0,
).with_structured_output(RoutingDecision)

MAX_ITERATIONS = 5


async def supervisor_node(state: AgentState) -> AgentState:
    if state.iteration_count >= MAX_ITERATIONS:
        return state.model_copy(update={"next_agent": "__end__"})

    decision: RoutingDecision = await _llm.ainvoke(
        [SystemMessage(content=_SYSTEM_PROMPT)] + state.messages
    )
    return state.model_copy(
        update={
            "next_agent": decision.next,
            "iteration_count": state.iteration_count + 1,
        }
    )
