from app.db import fetch_contacts_for_qualification, update_contact_qualification

KEYWORDS = {
    "Support Coordinator": ["support coordinator", "support coordination", "specialist support coordination"],
    "Recovery Coach": ["recovery coach", "psychosocial", "mental health"],
    "Occupational Therapist": ["occupational therapist", "occupational therapy", " ot ", "functional capacity"],
    "Plan Manager": ["plan manager", "plan management", "invoice", "claims"],
    "Community Organisation": ["community services", "disability services", "ndis provider", "ndis registered"],
}

SERVICE_ANGLES = {
    "Support Coordinator": "NDIS cleaning, domestic tasks, laundry assistance, community access and practical participant support",
    "Recovery Coach": "NDIS cleaning, domestic tasks, laundry support and practical home support for psychosocial participants",
    "Occupational Therapist": "NDIS cleaning, decluttering, domestic tasks and home support where participants need practical assistance",
    "Plan Manager": "provider introduction, compliant invoicing, fast service agreements and reliable communication",
    "Community Organisation": "NDIS cleaning, domestic tasks, community access and practical home support",
    "Other": "professional services and support",
}

BAD_PATTERNS = ["web design", "seo agency", "marketing agency", "jobs", "career", "recruitment"]

# Email domains/patterns that are clearly not real contacts
BAD_EMAIL_PATTERNS = [
    "sentry.wixpress.com",
    "sentry-next.wixpress.com",
    "wixpress.com",
    "sentry.io",
    "example.com",
    "user@domain",
    "test@",
    "noreply@",
    "no-reply@",
    "donotreply@",
]


def qualify(contact: dict) -> tuple[int, str, str, str, str]:
    text = " ".join(str(contact.get(k) or "") for k in ["role", "organisation", "email", "website", "notes"]).lower()
    email = (contact.get("email") or "").lower()

    # Filter out tracker/placeholder emails
    if any(bad in email for bad in BAD_EMAIL_PATTERNS):
        return 0, "Bad fit: internal tracker or placeholder email.", "Other", SERVICE_ANGLES["Other"], "rejected"

    if any(bad in text for bad in BAD_PATTERNS):
        return 0, "Bad fit: likely agency/job/recruitment unrelated to NDIS referrals.", "Other", SERVICE_ANGLES["Other"], "rejected"

    contact_type = "Other"
    score = 10
    reasons = []

    for ctype, words in KEYWORDS.items():
        matched = [w for w in words if w in text]
        if matched:
            contact_type = ctype
            reasons.append(f"Matched {ctype}: {', '.join(matched[:3])}")
            break

    if contact_type == "Support Coordinator":
        score += 70
    elif contact_type == "Recovery Coach":
        score += 60
    elif contact_type == "Occupational Therapist":
        score += 45
    elif contact_type == "Community Organisation":
        score += 35
    elif contact_type == "Plan Manager":
        score += 25
    else:
        # Generic contact — give a reasonable baseline score so non-NDIS
        # industries (Real Estate, Legal, Healthcare, etc.) still qualify.
        score += 40
        reasons.append("No specific niche keyword matched; general outreach contact.")

    email = (contact.get("email") or "").lower()
    local = email.split("@")[0]
    if local in {"referrals", "intake"}:
        score += 15
        reasons.append("Referral/intake email detected.")
    elif local in {"info", "admin", "hello", "contact", "enquiries"}:
        score += 5
        reasons.append("Generic contact email, still usable.")
    elif "." in local or "_" in local or "-" in local:
        score += 10
        reasons.append("Likely personal email format.")

    status = "qualified" if score >= 45 else "low_priority"
    return min(score, 100), " ".join(reasons), contact_type, SERVICE_ANGLES[contact_type], status


def run(limit: int = 50) -> int:
    contacts = fetch_contacts_for_qualification(limit)
    count = 0
    for c in contacts:
        score, reason, ctype, angle, status = qualify(c)
        update_contact_qualification(c["id"], score, reason, ctype, angle, status)
        count += 1
    return count
