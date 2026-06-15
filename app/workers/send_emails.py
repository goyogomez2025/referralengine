import time
from app.db import fetch_sendable_emails, fetch_emails_by_ids, mark_sent
from app.services.gmail_service import send_email as gmail_send, delete_draft


def run(email_ids: list[int] | None = None, limit: int = 20) -> tuple[int, list[str]]:
    """
    Send emails directly via Gmail.
    - Queries by specific ID when email_ids is provided (no ordering/limit issues).
    - Deletes the Gmail draft after sending so the Drafts folder stays clean.
    Returns (count_sent, list_of_errors).
    """
    if email_ids:
        emails = fetch_emails_by_ids(email_ids)
    else:
        emails = fetch_sendable_emails(limit)

    sent   = 0
    errors: list[str] = []

    for e in emails:
        # Capture draft ID NOW — mark_sent will overwrite gmail_draft_id with
        # the sent message ID, so we must read it before that call.
        draft_id = e.get("gmail_draft_id")

        try:
            msg_id = gmail_send(e["recipient_email"], e["subject"], e["body"])
            mark_sent(e["id"], msg_id)

            # Remove the corresponding Gmail draft so it doesn't sit in the
            # Drafts folder alongside the sent message.
            if draft_id:
                delete_draft(draft_id)

            sent += 1
            time.sleep(1)  # polite rate limiting
        except Exception as exc:
            errors.append(f"{e['recipient_email']}: {exc}")

    return sent, errors
