import time
from uuid import UUID

from fastapi import HTTPException, status
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from sqlalchemy import select

from app.config import settings
from app.core.billing.tracker import record_usage
from app.core.router.classifier import classify_intent
from app.db.models import AgentDefinition
from app.db.session import async_session
from app.schemas.agent import RunRequest, RunResponse


async def dispatch(request: RunRequest, tenant_id: UUID, user_id: UUID) -> RunResponse:
    decision = await classify_intent(request.message, tenant_id)

    if decision.agent_name == "__none__" or decision.confidence < 0.5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"No suitable agent found (confidence={decision.confidence:.2f})",
        )

    async with async_session() as db:
        result = await db.execute(
            select(AgentDefinition).where(AgentDefinition.name == decision.agent_name)
        )
        agent = result.scalar_one_or_none()

    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    llm = ChatOpenAI(model=agent.model, api_key=settings.openai_api_key)

    start = time.monotonic()
    response = await llm.ainvoke(
        [SystemMessage(content=agent.system_prompt), HumanMessage(content=request.message)]
    )
    latency_ms = round((time.monotonic() - start) * 1000)

    usage = response.usage_metadata or {}
    input_tokens = usage.get("input_tokens", 0)
    output_tokens = usage.get("output_tokens", 0)

    await record_usage(
        tenant_id=tenant_id,
        user_id=user_id,
        agent_id=agent.id,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
    )

    return RunResponse(
        agent_name=agent.name,
        agent_id=agent.id,
        output=str(response.content),
        routed_by=decision.reasoning,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        latency_ms=latency_ms,
    )
