import re
from urllib.parse import urlparse

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"(?:\+?61|0)[\s\-]?(?:2|3|4|7|8)[\d\s\-]{7,12}")

BAD_EMAIL_PREFIXES = {
    "noreply", "no-reply", "donotreply", "do-not-reply", "privacy", "abuse",
    "webmaster", "postmaster", "support+", "example"
}


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def extract_emails(text: str) -> list[str]:
    emails = set(e.lower().strip(".,;:()[]{}<>") for e in EMAIL_RE.findall(text or ""))
    cleaned = []
    for email in emails:
        prefix = email.split("@")[0]
        if any(prefix.startswith(bad) for bad in BAD_EMAIL_PREFIXES):
            continue
        if email.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            continue
        cleaned.append(email)
    return sorted(cleaned)


def extract_phones(text: str) -> list[str]:
    phones = set(clean_text(p) for p in PHONE_RE.findall(text or ""))
    return sorted(phones)


def domain_from_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "")


def guess_org_from_domain(url: str) -> str:
    domain = domain_from_url(url).split(":")[0]
    base = domain.split(".")[0]
    return base.replace("-", " ").replace("_", " ").title()


def split_name_from_email(email: str) -> tuple[str | None, str | None]:
    local = email.split("@")[0]
    local = re.sub(r"\d+", "", local)
    for sep in [".", "_", "-"]:
        if sep in local:
            parts = [p.capitalize() for p in local.split(sep) if p]
            if len(parts) >= 2:
                return parts[0], parts[-1]
    if local in {"info", "admin", "hello", "contact", "referrals", "intake", "support", "enquiries"}:
        return None, None
    return local.capitalize(), None
