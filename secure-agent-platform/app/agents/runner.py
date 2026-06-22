import time
from uuid import UUID

from fastapi import HTTPException, status
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.core.audit.logger import log_event
from app.core.audit.models import AuditEventType
from app.core.guardrails.engine import GuardrailVerdict, check_input, check_output
from app.core.policy.evaluator import check_agent_access
from app.core.tenancy.isolation import assert_agent_belongs_to_tenant
from app.observability.metrics import (
    agent_latency_seconds,
    llm_cost_tokens_total,
    policy_denials_total,
)
from app.schemas.agent import AgentRunRequest, AgentRunResponse

_llm = ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key)


async def run_agent(
    request: AgentRunRequest, tenant_id: UUID, user_id: str
) -> AgentRunResponse:
    try:
        await assert_agent_belongs_to_tenant(request.agent_id, tenant_id)
    except PermissionError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")

    policy = await check_agent_access(tenant_id, user_id, request.agent_id, "invoke")
    if not policy.allowed:
        policy_denials_total.labels(tenant_id=str(tenant_id), agent_id=request.agent_id).inc()
        await log_event(
            tenant_id, user_id, request.agent_id,
            AuditEventType.POLICY_DENIED, {"reason": policy.reason},
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=policy.reason)

    guard_in = await check_input(request.message, str(tenant_id))
    if guard_in.verdict == GuardrailVerdict.UNSAFE:
        event_type = (
            AuditEventType.ATTACK_DETECTED
            if guard_in.category == "prompt_injection"
            else AuditEventType.GUARDRAIL_BLOCKED_INPUT
        )
        await log_event(tenant_id, user_id, request.agent_id, event_type, {"category": guard_in.category})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsafe input detected: {guard_in.category}",
        )

    await log_event(tenant_id, user_id, request.agent_id, AuditEventType.AGENT_INVOKED, {"message": request.message})

    start = time.monotonic()
    ai_message = await _llm.ainvoke([HumanMessage(content=request.message)])
    latency = time.monotonic() - start

    agent_latency_seconds.labels(agent_id=request.agent_id, tenant_id=str(tenant_id)).observe(latency)
    llm_cost_tokens_total.labels(agent_id=request.agent_id, tenant_id=str(tenant_id)).inc(
        ai_message.usage_metadata.get("total_tokens", 0) if ai_message.usage_metadata else 0
    )

    output = str(ai_message.content)
    guard_out = await check_output(output, str(tenant_id))
    if guard_out.verdict == GuardrailVerdict.UNSAFE:
        await log_event(
            tenant_id, user_id, request.agent_id,
            AuditEventType.GUARDRAIL_BLOCKED_OUTPUT, {"category": guard_out.category},
        )
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Agent produced unsafe output")

    await log_event(
        tenant_id, user_id, request.agent_id,
        AuditEventType.AGENT_COMPLETED, {"output": output}, verdict="safe",
    )

    return AgentRunResponse(
        agent_id=request.agent_id,
        output=output,
        latency_ms=round(latency * 1000),
        tenant_id=tenant_id,
    )
