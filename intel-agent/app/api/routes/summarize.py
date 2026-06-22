from fastapi import APIRouter

from app.agent.summarizer import summarize_document
from app.schemas.summarize import SummaryRequest, SummaryResponse

router = APIRouter()


@router.post("/summarize", response_model=SummaryResponse)
async def summarize(body: SummaryRequest) -> SummaryResponse:
    return await summarize_document(body)
