from app.config import settings
from app.db import fetch_contacts_for_email, save_email
from app.services import campaign_service
from app.services.openai_service import generate_email_json, has_openai


def _get_campaign(campaign_id: str) -> dict:
    """Return full campaign dict; fall back to empty dict if not found."""
    if campaign_id:
        return campaign_service.get(campaign_id) or {}
    camps = campaign_service.all_campaigns()
    return next((c for c in camps if c.get("active", True)), {}) if camps else {}


def _sender(camp: dict) -> tuple:
    name    = camp.get("sender_name")    or settings.sender_name
    title   = camp.get("sender_title")   or settings.sender_title
    company = camp.get("sender_company") or settings.company_name
    return name, title, company


def fallback_email(contact: dict, camp: dict) -> dict:
    first_name  = contact.get("first_name") or "there"
    service     = camp.get("service") or contact.get("service_angle") or "our services"
    value_prop  = camp.get("value_proposition") or ""
    locations   = ", ".join(camp.get("locations", [])) or settings.default_locations
    sender_name, sender_title, sender_company = _sender(camp)
    location_first = locations.split(",")[0].strip() if locations else "your area"

    subject = f"{service} — availability in {location_first}"
    vp_line = f"\n{value_prop}\n" if value_prop else ""
    body = (
        f"Hi {first_name},\n\n"
        f"I'm {sender_name} from {sender_company}.\n\n"
        f"We currently have capacity for {service} in {locations}.{vp_line}\n"
        f"If you have any clients or contacts who may benefit from this service, "
        f"feel free to reach out — we can check availability and get you our details quickly.\n\n"
        f"Kind regards,\n"
        f"{sender_name}\n"
        f"{sender_title} · {sender_company}\n"
        f"M: {settings.sender_phone}\n"
        f"W: {settings.company_website}\n\n"
        f"If this is not relevant to you, just reply \"no thanks\" and I won't follow up."
    )
    return {"subject": subject, "body": body}


def build_prompt(contact: dict, camp: dict) -> str:
    sender_name, sender_title, sender_company = _sender(camp)
    industry   = camp.get("industry")          or "General"
    niche      = camp.get("niche")             or contact.get("contact_type") or contact.get("role") or "professional"
    service    = camp.get("service")           or contact.get("service_angle") or "our services"
    value_prop = camp.get("value_proposition") or ""
    locations  = ", ".join(camp.get("locations", [])) or settings.default_locations
    tone       = camp.get("tone")              or "Warm & Professional"

    return f"""Write a short professional outreach email from {sender_name}, {sender_title} of {sender_company}.

Context:
- Industry: {industry}
- {sender_company} offers: {service}
- Key service areas: {locations}
- Value proposition: {value_prop or "N/A"}
- Target audience: {niche}
- Tone: {tone} — not pushy, not spammy, human and direct

Contact:
- First name: {contact.get("first_name") or ""}
- Last name: {contact.get("last_name") or ""}
- Role: {contact.get("contact_type") or contact.get("role") or ""}
- Organisation: {contact.get("organisation") or ""}
- Email: {contact.get("email") or ""}
- Location: {contact.get("location") or ""}
- Qualification reason: {contact.get("qualification_reason") or ""}

Rules:
- Maximum 130 words in the body.
- Do not sound like a marketing agency or generic sales email.
- Do not mention that this contact was found online.
- Include a simple opt-out line at the end (e.g. "If this isn't relevant, just reply no.").
- Return valid JSON only with exactly these keys: subject, body.
"""


def run(campaign: str = "", limit: int = 20) -> int:
    camp     = _get_campaign(campaign)
    contacts = fetch_contacts_for_email(limit)
    count    = 0
    _, _, company = _sender(camp)
    default_subject = f"Introduction from {company}"

    for c in contacts:
        try:
            if has_openai():
                email = generate_email_json(build_prompt(c, camp))
            else:
                email = fallback_email(c, camp)
            subject = (email.get("subject") or default_subject).strip()
            body    = (email.get("body") or fallback_email(c, camp)["body"]).strip()
            save_email(c["id"], campaign, subject, body)
            count += 1
        except Exception:
            email = fallback_email(c, camp)
            save_email(c["id"], campaign, email["subject"], email["body"])
            count += 1
    return count
