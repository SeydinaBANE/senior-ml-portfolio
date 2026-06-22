from uuid import UUID

from fastapi import APIRouter, Depends

from app.api.deps import get_tenant_id, get_user_id
from app.core.router.dispatcher import dispatch
from app.schemas.agent import RunRequest, RunResponse

router = APIRouter()


@router.post("/run", response_model=RunResponse)
async def run(
    body: RunRequest,
    tenant_id: UUID = Depends(get_tenant_id),
    user_id: UUID = Depends(get_user_id),
) -> RunResponse:
    return await dispatch(body, tenant_id, user_id)
