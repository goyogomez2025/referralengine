from app.config import settings
from app.db import upsert_prospect
from app.services.search_service import search_web
import time, random

DEFAULT_QUERIES = [
    "NDIS support coordinator Brisbane email",
    "NDIS support coordination Moreton Bay contact",
    "support coordinator Redcliffe NDIS email",
    "psychosocial recovery coach Brisbane NDIS contact",
    "occupational therapist Brisbane NDIS contact email",
    "NDIS plan manager Queensland contact email",
]


def run(query: str | None = None, limit: int | None = None, campaign_id: str | None = None) -> int:
    # Priority: single query > campaign queries > defaults
    if query:
        queries = [query]
    elif campaign_id:
        try:
            from app.services.campaign_service import get as get_campaign
            camp = get_campaign(campaign_id)
            queries = camp.get("queries", DEFAULT_QUERIES) if camp else DEFAULT_QUERIES
        except Exception:
            queries = DEFAULT_QUERIES
    else:
        queries = DEFAULT_QUERIES

    total = 0
    limit = limit or settings.max_contacts_per_query
    for i, q in enumerate(queries):
        # Space out requests to avoid DuckDuckGo rate limiting:
        # 1.5–3s between each query (skip delay on the first one)
        if i > 0:
            time.sleep(random.uniform(1.5, 3.0))

        results = search_web(q, limit=limit)
        for r in results:
            upsert_prospect(q, r["title"], r["url"], r.get("snippet", ""))
            total += 1
    return total
