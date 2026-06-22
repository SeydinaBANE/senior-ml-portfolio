from langchain_core.tools import tool
from slack_sdk.web.async_client import AsyncWebClient

from app.config import settings

_client = AsyncWebClient(token=settings.slack_bot_token) if settings.slack_bot_token else None


@tool
async def post_slack_message_tool(message: str, channel: str = "") -> str:
    """Post a message to a Slack channel."""
    if _client is None:
        raise RuntimeError("SLACK_BOT_TOKEN not configured")
    target = channel or settings.slack_default_channel
    await _client.chat_postMessage(channel=target, text=message, mrkdwn=True)
    return f"Message posted to {target}"


@tool
async def post_report_to_slack_tool(title: str, report: str) -> str:
    """Post a structured research report to Slack with formatting."""
    if _client is None:
        raise RuntimeError("SLACK_BOT_TOKEN not configured")
    blocks = [
        {"type": "header", "text": {"type": "plain_text", "text": title}},
        {"type": "divider"},
        {"type": "section", "text": {"type": "mrkdwn", "text": report[:2900]}},
    ]
    await _client.chat_postMessage(
        channel=settings.slack_default_channel,
        blocks=blocks,
        text=title,
    )
    return f"Report '{title}' posted to {settings.slack_default_channel}"
