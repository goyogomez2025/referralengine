from app.config import settings
from app.db import fetch_contacts_for_email, save_email
from app.services.openai_service import generate_email_json, has_openai


def fallback_email(contact: dict, campaign: str) -> dict:
    first_name = contact.get("first_name") or "there"
    contact_type = contact.get("contact_type") or "NDIS professional"
    service_angle = contact.get("service_angle") or "NDIS cleaning and domestic task support"
    locations = settings.default_locations

    if "moving" in campaign.lower() or "relocation" in campaign.lower():
        subject = "NDIS moving and home transition support"
        body = f"""Hi {first_name},

I’m Greg from Yirra Care.

We’re currently able to assist NDIS participants who need practical moving, decluttering, packing, cleaning before or after a move, and home transition support around {locations}.

This can be useful where a participant needs more than a standard removalist and requires reliable, respectful support around the move.

If you have any participants needing this type of practical support, feel free to send the details through and we can check capacity.

Kind regards,
Greg Gomez
CEO | Founder · Yirra Care
M: {settings.sender_phone}
W: {settings.company_website}

If this is not relevant, just reply “no” and I won’t follow up."""
    else:
        subject = "NDIS cleaning capacity around Brisbane North"
        body = f"""Hi {first_name},

I’m Greg from Yirra Care.

We currently have capacity for {service_angle} around {locations}.

We can assist participants with regular home cleaning, bathroom and kitchen cleaning, vacuuming, mopping, laundry assistance and general domestic tasks. We work with plan-managed, self-managed and agency-managed participants and can send a quote and service agreement quickly.

If you have any participants needing reliable cleaning support, feel free to send the details through and we can check capacity.

Kind regards,
Greg Gomez
CEO | Founder · Yirra Care
M: {settings.sender_phone}
W: {settings.company_website}

If this is not relevant, just reply “no” and I won’t follow up."""

    return {"subject": subject, "body": body}


def build_prompt(contact: dict, campaign: str) -> str:
    return f"""
Write a short professional outreach email from Greg Gomez, CEO of Yirra Care.

Company context:
- Yirra Care provides NDIS supports in Queensland.
- Main service for this campaign: NDIS cleaning and domestic task support.
- Key locations: {settings.default_locations}.
- Can work with plan-managed, self-managed and agency-managed participants.
- Tone: warm, human, professional, not spammy, not pushy.

Contact:
- First name: {contact.get('first_name') or ''}
- Last name: {contact.get('last_name') or ''}
- Role/contact type: {contact.get('contact_type') or contact.get('role') or ''}
- Organisation: {contact.get('organisation') or ''}
- Email: {contact.get('email') or ''}
- Location: {contact.get('location') or ''}
- Service angle: {contact.get('service_angle') or ''}
- Qualification reason: {contact.get('qualification_reason') or ''}

Campaign: {campaign}

Rules:
- Maximum 130 words in the body.
- Do not sound like an SEO agency or generic sales email.
- Do not overpromise.
- Do not mention that the contact was scraped/found online.
- Include a simple opt-out line at the end.
- Return valid JSON only with keys: subject, body.
"""


def run(campaign: str = "cleaning_sc_brisbane", limit: int = 20) -> int:
    contacts = fetch_contacts_for_email(limit)
    count = 0
    for c in contacts:
        try:
            if has_openai():
                email = generate_email_json(build_prompt(c, campaign))
            else:
                email = fallback_email(c, campaign)
            subject = (email.get("subject") or "NDIS cleaning capacity around Brisbane North").strip()
            body = (email.get("body") or fallback_email(c, campaign)["body"]).strip()
            save_email(c["id"], campaign, subject, body)
            count += 1
        except Exception:
            email = fallback_email(c, campaign)
            save_email(c["id"], campaign, email["subject"], email["body"])
            count += 1
    return count
