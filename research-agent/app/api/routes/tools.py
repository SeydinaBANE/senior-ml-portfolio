from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings

router = APIRouter()


class ToolStatus(BaseModel):
    name: str
    configured: bool


@router.get("/tools/status", response_model=list[ToolStatus])
async def tools_status() -> list[ToolStatus]:
    return [
        ToolStatus(name="tavily_search", configured=bool(settings.tavily_api_key)),
        ToolStatus(name="gmail", configured=bool(settings.google_client_id)),
        ToolStatus(name="google_calendar", configured=bool(settings.google_client_id)),
        ToolStatus(name="notion", configured=bool(settings.notion_api_key)),
        ToolStatus(name="slack", configured=bool(settings.slack_bot_token)),
    ]
