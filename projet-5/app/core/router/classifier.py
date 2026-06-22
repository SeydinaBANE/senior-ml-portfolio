from uuid import UUID

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from sqlalchemy import select

from app.config import settings
from app.db.models import AgentDefinition
from app.db.session import async_session

_SYSTEM = """You are an agent router. Given a user message and a list of available agents
(name, description, category), pick the most appropriate agent.
Respond with the agent name exactly as provided. If none fit, respond with '__none__'."""


class RoutingDecision(BaseModel):
    agent_name: str
    confidence: float
    reasoning: str


_llm = ChatOpenAI(
    model=settings.openai_model, api_key=settings.openai_api_key, temperature=0
).with_structured_output(RoutingDecision)


async def classify_intent(message: str, tenant_id: UUID) -> RoutingDecision:
    async with async_session() as db:
        result = await db.execute(
            select(AgentDefinition).where(
                (AgentDefinition.tenant_id == tenant_id) | AgentDefinition.is_public
            )
        )
        agents = result.scalars().all()

    if not agents:
        return RoutingDecision(
            agent_name="__none__", confidence=0.0, reasoning="No agents available"
        )

    agent_list = "\n".join(
        f"- {a.name} ({a.category}): {a.description}" for a in agents
    )
    decision: RoutingDecision = await _llm.ainvoke(
        [
            SystemMessage(content=_SYSTEM),
            HumanMessage(content=f"Agents:\n{agent_list}\n\nMessage: {message}"),
        ]
    )
    return decision
