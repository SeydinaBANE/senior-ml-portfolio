import base64
import json
from email.mime.text import MIMEText
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain_core.tools import tool

from app.config import settings

_SCOPES = ["https://www.googleapis.com/auth/gmail.send", "https://www.googleapis.com/auth/gmail.readonly"]


def _get_gmail_service():  # type: ignore[no-untyped-def]
    token_path = Path(settings.google_token_path)
    creds: Credentials | None = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), _SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise RuntimeError("Google credentials not configured. Run auth flow first.")

        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


@tool
def send_email_tool(to: str, subject: str, body: str) -> str:
    """Send an email via Gmail."""
    service = _get_gmail_service()
    message = MIMEText(body)
    message["to"] = to
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return f"Email sent to {to}"


@tool
def read_recent_emails_tool(max_results: int = 5) -> str:
    """Read the most recent emails from Gmail inbox."""
    service = _get_gmail_service()
    result = service.users().messages().list(userId="me", maxResults=max_results).execute()
    messages = result.get("messages", [])
    summaries = []
    for msg in messages:
        detail = service.users().messages().get(userId="me", id=msg["id"], format="metadata").execute()
        headers = {h["name"]: h["value"] for h in detail.get("payload", {}).get("headers", [])}
        summaries.append(f"From: {headers.get('From')} | Subject: {headers.get('Subject')}")
    return "\n".join(summaries) if summaries else "No messages found"
