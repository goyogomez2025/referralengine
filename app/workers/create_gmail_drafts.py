from app.config import settings
from app.db import fetch_draft_ready_emails, mark_gmail_draft
from app.services.gmail_service import create_draft


def run(limit: int | None = None) -> int:
    limit = limit or settings.max_drafts_per_run
    emails = fetch_draft_ready_emails(limit)
    count = 0
    for e in emails:
        draft_id = create_draft(e["recipient_email"], e["subject"], e["body"])
        mark_gmail_draft(e["id"], draft_id)
        count += 1
    return count
