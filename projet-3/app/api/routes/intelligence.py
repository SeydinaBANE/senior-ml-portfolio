from fastapi import APIRouter

from app.agent.intelligence import gather_intelligence
from app.schemas.intelligence import IntelRequest, IntelResponse

router = APIRouter()


@router.post("/intelligence", response_model=IntelResponse)
async def intelligence(body: IntelRequest) -> IntelResponse:
    return await gather_intelligence(body)
