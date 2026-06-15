import json
from app.db import get_conn, upsert_contact
from app.services.scrape_service import scrape_site
from app.utils.text import guess_org_from_domain, split_name_from_email

EMAIL_PRIORITY = ["referrals", "intake", "hello", "contact", "admin", "info", "support", "enquiries"]


def _email_rank(email: str) -> int:
    local = email.split("@")[0]
    for i, prefix in enumerate(EMAIL_PRIORITY):
        if local.startswith(prefix):
            return i
    return 50


def run(limit: int = 20, location: str | None = None) -> int:
    conn = get_conn()
    prospects = conn.execute(
        "SELECT * FROM prospects WHERE status='found' LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()

    contacts_created = 0
    for p in prospects:
        url = p["url"]
        scraped = scrape_site(url)
        emails = sorted(scraped["emails"], key=_email_rank)
        phones = scraped["phones"]
        org = guess_org_from_domain(url)
        text = scraped.get("text", "")[:1000]

        for email in emails[:3]:  # max 3 contactos por web para no llenar basura
            first, last = split_name_from_email(email)
            upsert_contact({
                "first_name": first,
                "last_name": last,
                "role": None,
                "organisation": org,
                "email": email,
                "phone": phones[0] if phones else None,
                "website": scraped["start_url"],
                "location": location,
                "source_url": url,
                "notes": f"Search result: {p['title']} | Snippet: {p['snippet']} | Page text sample: {text}",
                "status": "enriched",
            })
            contacts_created += 1

        conn = get_conn()
        conn.execute(
            "UPDATE prospects SET status='scraped' WHERE id=?",
            (p["id"],),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO website_pages(url, website, title, text, emails, phones)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                scraped["start_url"],
                scraped["start_url"],
                p["title"],
                scraped.get("text", "")[:50000],
                json.dumps(emails),
                json.dumps(phones),
            ),
        )
        conn.commit()
        conn.close()

    return contacts_created
