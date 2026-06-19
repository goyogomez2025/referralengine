import sqlite3
from pathlib import Path
from app.config import settings


def get_conn() -> sqlite3.Connection:
    db_path = Path(settings.database_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("PRAGMA foreign_keys = ON")

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            role TEXT,
            organisation TEXT,
            email TEXT UNIQUE,
            phone TEXT,
            website TEXT,
            location TEXT,
            source_url TEXT,
            contact_type TEXT,
            service_angle TEXT,
            qualification_score INTEGER DEFAULT 0,
            qualification_reason TEXT,
            status TEXT DEFAULT 'new',
            last_contacted TEXT,
            reply_status TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS prospects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            title TEXT,
            url TEXT UNIQUE,
            snippet TEXT,
            status TEXT DEFAULT 'found',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS website_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            website TEXT,
            title TEXT,
            text TEXT,
            emails TEXT,
            phones TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            campaign TEXT,
            subject TEXT,
            body TEXT,
            status TEXT DEFAULT 'draft_ready',
            gmail_draft_id TEXT,
            sent_at TEXT,
            followup_due TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(contact_id) REFERENCES contacts(id)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contact_id INTEGER,
            interaction_type TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(contact_id) REFERENCES contacts(id)
        )
        """
    )

    conn.commit()
    conn.close()


def upsert_prospect(query: str, title: str, url: str, snippet: str = "") -> None:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT OR IGNORE INTO prospects(query, title, url, snippet)
        VALUES (?, ?, ?, ?)
        """,
        (query, title, url, snippet),
    )
    conn.commit()
    conn.close()


def upsert_contact(contact: dict) -> int | None:
    email = (contact.get("email") or "").strip().lower()
    if not email:
        return None

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO contacts(
            first_name, last_name, role, organisation, email, phone, website,
            location, source_url, contact_type, service_angle, notes, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(email) DO UPDATE SET
            phone=COALESCE(excluded.phone, contacts.phone),
            website=COALESCE(excluded.website, contacts.website),
            source_url=COALESCE(excluded.source_url, contacts.source_url),
            notes=COALESCE(excluded.notes, contacts.notes),
            updated_at=CURRENT_TIMESTAMP
        """,
        (
            contact.get("first_name"),
            contact.get("last_name"),
            contact.get("role"),
            contact.get("organisation"),
            email,
            contact.get("phone"),
            contact.get("website"),
            contact.get("location"),
            contact.get("source_url"),
            contact.get("contact_type"),
            contact.get("service_angle"),
            contact.get("notes"),
            contact.get("status", "new"),
        ),
    )
    conn.commit()
    row = cur.execute("SELECT id FROM contacts WHERE email = ?", (email,)).fetchone()
    conn.close()
    return int(row["id"]) if row else None


def fetch_contacts_for_qualification(limit: int = 50) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT * FROM contacts
        WHERE status IN ('new', 'enriched')
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_contact_qualification(contact_id: int, score: int, reason: str, contact_type: str, service_angle: str, status: str) -> None:
    conn = get_conn()
    conn.execute(
        """
        UPDATE contacts
        SET qualification_score=?, qualification_reason=?, contact_type=?, service_angle=?, status=?, updated_at=CURRENT_TIMESTAMP
        WHERE id=?
        """,
        (score, reason, contact_type, service_angle, status, contact_id),
    )
    conn.commit()
    conn.close()


def fetch_contacts_for_email(limit: int = 20) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT c.* FROM contacts c
        LEFT JOIN emails e ON e.contact_id = c.id
        WHERE c.status='qualified' AND e.id IS NULL
        ORDER BY c.qualification_score DESC, c.created_at ASC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def save_email(contact_id: int, campaign: str, subject: str, body: str) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO emails(contact_id, campaign, subject, body, status)
        VALUES (?, ?, ?, ?, 'draft_ready')
        """,
        (contact_id, campaign, subject, body),
    )
    email_id = cur.lastrowid
    conn.execute("UPDATE contacts SET status='email_ready', updated_at=CURRENT_TIMESTAMP WHERE id=?", (contact_id,))
    conn.commit()
    conn.close()
    return int(email_id)


def fetch_draft_ready_emails(limit: int = 10) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT e.*, c.email AS recipient_email, c.first_name, c.organisation
        FROM emails e
        JOIN contacts c ON c.id = e.contact_id
        WHERE e.status='draft_ready'
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def mark_gmail_draft(email_id: int, draft_id: str) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE emails SET status='gmail_draft_created', gmail_draft_id=? WHERE id=?",
        (draft_id, email_id),
    )
    conn.commit()
    conn.close()


def mark_sent(email_id: int, gmail_message_id: str) -> None:
    conn = get_conn()
    conn.execute(
        "UPDATE emails SET status='sent', gmail_draft_id=?, sent_at=CURRENT_TIMESTAMP WHERE id=?",
        (gmail_message_id, email_id),
    )
    conn.execute(
        """UPDATE contacts SET status='contacted', last_contacted=CURRENT_TIMESTAMP
           WHERE id=(SELECT contact_id FROM emails WHERE id=?)""",
        (email_id,),
    )
    conn.commit()
    conn.close()


def fetch_sendable_emails(limit: int = 100) -> list[dict]:
    """Emails ready to send (draft_ready or gmail_draft_created)."""
    conn = get_conn()
    rows = conn.execute(
        """
        SELECT e.id, e.campaign, e.subject, e.body, e.status, e.created_at,
               e.gmail_draft_id,
               c.email AS recipient_email, c.first_name, c.organisation,
               c.contact_type, c.qualification_score
        FROM emails e
        JOIN contacts c ON c.id = e.contact_id
        WHERE e.status IN ('draft_ready', 'gmail_draft_created')
        ORDER BY c.qualification_score DESC, e.created_at DESC
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_emails_by_ids(ids: list[int]) -> list[dict]:
    """Fetch specific emails by their IDs (must be in a sendable status)."""
    if not ids:
        return []
    conn  = get_conn()
    ph    = ",".join("?" * len(ids))
    rows  = conn.execute(
        f"""
        SELECT e.id, e.campaign, e.subject, e.body, e.status, e.created_at,
               e.gmail_draft_id,
               c.email AS recipient_email, c.first_name, c.organisation,
               c.contact_type, c.qualification_score
        FROM emails e
        JOIN contacts c ON c.id = e.contact_id
        WHERE e.id IN ({ph})
          AND e.status IN ('draft_ready', 'gmail_draft_created')
        ORDER BY c.qualification_score DESC, e.created_at DESC
        """,
        ids,
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def delete_contacts(ids: list[int]) -> int:
    """Delete contacts (and their emails) by ID list. Returns count deleted."""
    if not ids:
        return 0
    conn = get_conn()
    ph = ",".join("?" * len(ids))
    conn.execute(f"DELETE FROM emails   WHERE contact_id IN ({ph})", ids)
    conn.execute(f"DELETE FROM contacts WHERE id         IN ({ph})", ids)
    conn.commit()
    deleted = conn.execute("SELECT changes()").fetchone()[0]
    conn.close()
    return len(ids)


def delete_emails(ids: list[int]) -> int:
    """Delete email records by ID list. Returns count deleted."""
    if not ids:
        return 0
    conn = get_conn()
    ph = ",".join("?" * len(ids))
    conn.execute(f"DELETE FROM emails WHERE id IN ({ph})", ids)
    conn.commit()
    conn.close()
    return len(ids)


def get_all_stats() -> dict:
    conn = get_conn()
    def n(sql):
        return conn.execute(sql).fetchone()[0]
    stats = {
        "prospects": n("SELECT COUNT(*) FROM prospects"),
        "contacts":  n("SELECT COUNT(*) FROM contacts"),
        "qualified": n("SELECT COUNT(*) FROM contacts WHERE status='qualified'"),
        "emails":    n("SELECT COUNT(*) FROM emails"),
        "drafts":    n("SELECT COUNT(*) FROM emails WHERE status='gmail_draft_created'"),
        "sent":      n("SELECT COUNT(*) FROM emails WHERE status='sent'"),
        "contacted": n("SELECT COUNT(*) FROM contacts WHERE status='contacted'"),
    }
    conn.close()
    return stats
