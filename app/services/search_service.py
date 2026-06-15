def _search_google_cse(query: str, limit: int = 20) -> list[dict]:
    """Google Custom Search JSON API – requires GOOGLE_API_KEY + GOOGLE_CSE_ID in .env"""
    from app.config import settings
    import requests

    results: list[dict] = []
    per_page = min(limit, 10)  # CSE max per request is 10
    pages_needed = (limit + 9) // 10

    for page in range(pages_needed):
        start = page * 10 + 1
        params = {
            "key": settings.google_api_key,
            "cx": settings.google_cse_id,
            "q": query,
            "num": per_page,
            "start": start,
        }
        resp = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params=params,
            timeout=15,
        )
        resp.raise_for_status()
        data = resp.json()
        for item in data.get("items", []):
            results.append({
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "snippet": item.get("snippet", ""),
            })
        if len(results) >= limit:
            break

    return results[:limit]


def _search_ddgs(query: str, limit: int = 20) -> list[dict]:
    """DuckDuckGo search – free, no key required."""
    try:
        from ddgs import DDGS
    except ImportError as exc:
        raise RuntimeError(
            "Missing dependency 'ddgs'. Run: pip install -r requirements.txt"
        ) from exc

    results: list[dict] = []
    with DDGS() as ddgs:
        for item in ddgs.text(query, max_results=limit):
            url = item.get("href") or item.get("url")
            if not url:
                continue
            results.append({
                "title": item.get("title", ""),
                "url": url,
                "snippet": item.get("body", ""),
            })
    return results


def search_web(query: str, limit: int = 20) -> list[dict]:
    """
    Web search adapter.
    Uses Google Custom Search API when GOOGLE_API_KEY + GOOGLE_CSE_ID are set,
    otherwise falls back to DuckDuckGo (DDGS).
    """
    from app.config import settings

    if settings.google_api_key and settings.google_cse_id:
        try:
            return _search_google_cse(query, limit)
        except Exception:
            pass  # fall through to DDGS

    return _search_ddgs(query, limit)
