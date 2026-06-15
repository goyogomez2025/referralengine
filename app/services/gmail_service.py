import base64
from email.message import EmailMessage
from pathlib import Path
from app.config import settings

SCOPES = ["https://mail.google.com/"]


def get_gmail_service():
    try:
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from google.auth.transport.requests import Request
        from googleapiclient.discovery import build
    except ImportError as exc:
        raise RuntimeError("Missing Google dependencies. Run: pip install -r requirements.txt") from exc

    creds = None
    token_path = Path(settings.google_token_file)
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not Path(settings.google_client_secret_file).exists():
                raise FileNotFoundError(
                    f"Missing {settings.google_client_secret_file}. Download OAuth credentials from Google Cloud Console."
                )
            flow = InstalledAppFlow.from_client_secrets_file(settings.google_client_secret_file, SCOPES)
            creds = flow.run_local_server(port=0)
        token_path.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def create_message(to: str, subject: str, body: str) -> dict:
    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["From"] = settings.sender_email
    message["Subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {"message": {"raw": raw}}


def create_draft(to: str, subject: str, body: str) -> str:
    service = get_gmail_service()
    draft_body = create_message(to, subject, body)
    draft = service.users().drafts().create(userId="me", body=draft_body).execute()
    return draft["id"]


def send_email(to: str, subject: str, body: str) -> str:
    """Send an email immediately (not as draft)."""
    service = get_gmail_service()
    msg = EmailMessage()
    msg.set_content(body)
    msg["To"] = to
    msg["From"] = settings.sender_email
    msg["Subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
    return sent["id"]


def delete_draft(draft_id: str) -> None:
    """Delete a Gmail draft by its draft ID — called after an email is sent."""
    try:
        service = get_gmail_service()
        service.users().drafts().delete(userId="me", id=draft_id).execute()
    except Exception:
        pass  # Non-critical: draft may already be gone
