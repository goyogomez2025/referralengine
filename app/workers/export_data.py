from pathlib import Path
import pandas as pd
from app.db import get_conn

EXPORT_DIR = Path("exports")
EXPORT_DIR.mkdir(exist_ok=True)


def export_contacts(path: str = "exports/contacts.csv") -> str:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM contacts ORDER BY qualification_score DESC, created_at DESC", conn)
    conn.close()
    df.to_csv(path, index=False)
    return path


def export_emails(path: str = "exports/emails.csv") -> str:
    conn = get_conn()
    df = pd.read_sql_query(
        """
        SELECT e.*, c.email AS recipient_email, c.first_name, c.last_name, c.organisation, c.contact_type
        FROM emails e
        JOIN contacts c ON c.id = e.contact_id
        ORDER BY e.created_at DESC
        """,
        conn,
    )
    conn.close()
    df.to_csv(path, index=False)
    return path
