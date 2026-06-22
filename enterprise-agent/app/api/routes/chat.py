from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from langchain_core.messages import HumanMessage

from app.agents.graph import compiled_graph
from app.agents.state import AgentState
from app.api.deps import get_current_tenant
from app.memory.persistent import save_message
from app.schemas.chat import ChatRequest, ChatResponse
from app.security.guardrails import PromptInjectionError, validate_input

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    tenant_id: UUID = Depends(get_current_tenant),
) -> ChatResponse:
    try:
        safe_message = validate_input(body.message)
    except PromptInjectionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    await save_message(tenant_id, body.session_id, "user", safe_message)

    initial_state = AgentState(
        messages=[HumanMessage(content=safe_message)],
        tenant_id=tenant_id,
        session_id=body.session_id,
    )

    final_state: AgentState = await compiled_graph.ainvoke(initial_state)

    last_ai = final_state.messages[-1].content if final_state.messages else ""
    await save_message(tenant_id, body.session_id, "assistant", str(last_ai))

    return ChatResponse(
        answer=str(last_ai),
        session_id=body.session_id,
        sources=final_state.context_chunks,
        tenant_id=tenant_id,
    )
