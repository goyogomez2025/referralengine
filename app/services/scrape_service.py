import time
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from app.config import settings
from app.utils.text import clean_text, extract_emails, extract_phones

HEADERS = {
    "User-Agent": "YirraCareReferralResearchBot/0.1 (+https://yirracare.com.au)"
}

CONTACT_PATH_HINTS = [
    "contact", "about", "team", "referral", "referrals", "intake", "support-coordination", "ndis"
]


def fetch_url(url: str, timeout: int = 15) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    content_type = resp.headers.get("content-type", "")
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        return ""
    return resp.text


def parse_page(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()
    title = clean_text(soup.title.get_text(" ")) if soup.title else ""
    text = clean_text(soup.get_text(" "))

    links = []
    base_domain = urlparse(url).netloc
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("mailto:"):
            text += " " + href.replace("mailto:", " ")
        absolute = urljoin(url, href)
        if urlparse(absolute).netloc == base_domain:
            if any(hint in absolute.lower() for hint in CONTACT_PATH_HINTS):
                links.append(absolute.split("#")[0])

    return {
        "url": url,
        "title": title,
        "text": text[:30000],
        "emails": extract_emails(html + " " + text),
        "phones": extract_phones(text),
        "internal_contact_links": sorted(set(links))[:5],
    }


def scrape_site(start_url: str, max_pages: int = 4) -> dict:
    visited = set()
    pages = []
    queue = [start_url]

    while queue and len(visited) < max_pages:
        url = queue.pop(0)
        if url in visited:
            continue
        visited.add(url)
        try:
            html = fetch_url(url)
            if not html:
                continue
            parsed = parse_page(url, html)
            pages.append(parsed)
            for link in parsed["internal_contact_links"]:
                if link not in visited and link not in queue:
                    queue.append(link)
            time.sleep(settings.request_delay_seconds)
        except Exception as exc:
            pages.append({
                "url": url,
                "title": "",
                "text": "",
                "emails": [],
                "phones": [],
                "error": str(exc),
            })

    all_text = " ".join(p.get("text", "") for p in pages)
    all_emails = sorted(set(e for p in pages for e in p.get("emails", [])))
    all_phones = sorted(set(pn for p in pages for pn in p.get("phones", [])))

    return {
        "start_url": start_url,
        "pages": pages,
        "text": all_text[:50000],
        "emails": all_emails,
        "phones": all_phones,
    }
