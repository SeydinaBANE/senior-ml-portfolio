from uuid import UUID

from fastapi import APIRouter, Depends

from app.agents.runner import run_agent
from app.api.deps import get_tenant_id, get_user_id
from app.schemas.agent import AgentRunRequest, AgentRunResponse

router = APIRouter()


@router.post("/agents/run", response_model=AgentRunResponse)
async def run(
    body: AgentRunRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: str = Depends(get_user_id),
) -> AgentRunResponse:
    return await run_agent(body, tenant_id, user_id)
