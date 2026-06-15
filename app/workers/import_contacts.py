import pandas as pd
from app.db import upsert_contact


def run(csv_path: str) -> int:
    df = pd.read_csv(csv_path).fillna("")
    count = 0
    for _, row in df.iterrows():
        email = str(row.get("email", "")).strip()
        if not email:
            continue
        upsert_contact({
            "first_name": row.get("first_name") or row.get("name") or None,
            "last_name": row.get("last_name") or None,
            "role": row.get("role") or None,
            "organisation": row.get("organisation") or row.get("company") or None,
            "email": email,
            "phone": row.get("phone") or None,
            "website": row.get("website") or None,
            "location": row.get("location") or None,
            "source_url": row.get("source_url") or None,
            "notes": row.get("notes") or "Imported from CSV",
            "status": "enriched",
        })
        count += 1
    return count
