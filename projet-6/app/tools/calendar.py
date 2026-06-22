from datetime import datetime, timezone
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from langchain_core.tools import tool

from app.config import settings

_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly", "https://www.googleapis.com/auth/calendar.events"]


def _get_calendar_service():  # type: ignore[no-untyped-def]
    token_path = Path(settings.google_token_path)
    if not token_path.exists():
        raise RuntimeError("Google credentials not configured. Run auth flow first.")
    creds = Credentials.from_authorized_user_file(str(token_path), _SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return build("calendar", "v3", credentials=creds)


@tool
def list_upcoming_events_tool(max_results: int = 10) -> str:
    """List upcoming Google Calendar events."""
    service = _get_calendar_service()
    now = datetime.now(timezone.utc).isoformat()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    events = events_result.get("items", [])
    if not events:
        return "No upcoming events found."
    return "\n".join(
        f"{e['start'].get('dateTime', e['start'].get('date'))} — {e.get('summary', 'No title')}"
        for e in events
    )


@tool
def create_event_tool(title: str, start_datetime: str, end_datetime: str, description: str = "") -> str:
    """Create a Google Calendar event. Datetimes must be ISO 8601 format."""
    service = _get_calendar_service()
    event = {
        "summary": title,
        "description": description,
        "start": {"dateTime": start_datetime, "timeZone": "UTC"},
        "end": {"dateTime": end_datetime, "timeZone": "UTC"},
    }
    created = service.events().insert(calendarId="primary", body=event).execute()
    return f"Event created: {created.get('htmlLink')}"
