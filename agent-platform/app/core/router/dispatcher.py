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
from app.observability.metrics import (
    agent_run_latency,
    agent_runs_total,
    token_usage_total,
)
from app.schemas.agent import RunRequest, RunResponse


async def dispatch(request: RunRequest, tenant_id: UUID, user_id: UUID) -> RunResponse:
    decision = await classify_intent(request.message, tenant_id)
    tid = str(tenant_id)

    if decision.agent_name == "__none__" or decision.confidence < 0.5:
        agent_runs_total.labels(tenant_id=tid, agent_name="__none__", status="rejected").inc()
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
        agent_runs_total.labels(tid, decision.agent_name, "not_found").inc()
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    llm = ChatOpenAI(model=agent.model, api_key=settings.openai_api_key)

    start = time.monotonic()
    try:
        response = await llm.ainvoke(
            [SystemMessage(content=agent.system_prompt), HumanMessage(content=request.message)]
        )
    except Exception:
        agent_runs_total.labels(tid, agent.name, "error").inc()
        raise
    latency_s = time.monotonic() - start
    latency_ms = round(latency_s * 1000)

    usage = response.usage_metadata or {}
    input_tokens: int = usage.get("input_tokens", 0)
    output_tokens: int = usage.get("output_tokens", 0)

    agent_runs_total.labels(tid, agent.name, "ok").inc()
    agent_run_latency.labels(agent_name=agent.name).observe(latency_s)
    token_usage_total.labels(tenant_id=tid, direction="input").inc(input_tokens)
    token_usage_total.labels(tenant_id=tid, direction="output").inc(output_tokens)

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
