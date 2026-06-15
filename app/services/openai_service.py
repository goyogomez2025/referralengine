import json
from app.config import settings


def has_openai() -> bool:
    return bool(settings.openai_api_key)


def generate_email_json(prompt: str) -> dict:
    if not settings.openai_api_key:
        raise RuntimeError("OPENAI_API_KEY missing")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Missing dependency 'openai'. Run: pip install -r requirements.txt") from exc

    client = OpenAI(api_key=settings.openai_api_key)

    # Simple JSON mode for broad SDK compatibility.
    response = client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": "You write concise, compliant, professional outreach emails. Return valid JSON only."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
    )
    content = response.choices[0].message.content or "{}"
    return json.loads(content)
