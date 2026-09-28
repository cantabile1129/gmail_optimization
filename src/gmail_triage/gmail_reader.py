from __future__ import annotations

from pathlib import Path

from .models import Message


SCOPE = "https://www.googleapis.com/auth/gmail.metadata"
HEADERS = ["From", "Subject", "List-Id"]


def connect(credentials_path: Path, token_path: Path):
    """Authorize locally. Credentials and refresh token must stay outside Git."""
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError('Install the Gmail extra: pip install -e ".[gmail]"') from exc

    if not credentials_path.is_file():
        raise FileNotFoundError(f"OAuth client file not found: {credentials_path}")
    token_path.parent.mkdir(parents=True, exist_ok=True)
    creds = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), [SCOPE])
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(credentials_path), [SCOPE])
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json(), encoding="utf-8")
    return build("gmail", "v1", credentials=creds, cache_discovery=False)


def read_recent_metadata(service, limit: int) -> list[Message]:
    """Read recent Inbox IDs and selected headers; never request message bodies."""
    if limit < 1:
        raise ValueError("limit must be positive")
    messages: list[Message] = []
    page_token = None
    while len(messages) < limit:
        page_size = min(500, limit - len(messages))
        request = service.users().messages().list(
            userId="me", maxResults=page_size,
            pageToken=page_token, labelIds=["INBOX"], includeSpamTrash=False,
        )
        page = request.execute()
        ids = page.get("messages", [])
        if not ids:
            break
        for item in ids:
            detail = service.users().messages().get(
                userId="me", id=item["id"], format="metadata", metadataHeaders=HEADERS,
            ).execute()
            messages.append(Message.from_gmail(detail))
        page_token = page.get("nextPageToken")
        if not page_token:
            break
    return messages
