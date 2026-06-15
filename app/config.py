import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def _bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y"}


@dataclass(frozen=True)
class Settings:
    database_path: str = os.getenv("DATABASE_PATH", "data/yirra_referrals.sqlite")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    sender_name: str = os.getenv("SENDER_NAME", "Greg Gomez")
    sender_title: str = os.getenv("SENDER_TITLE", "CEO | Founder")
    sender_email: str = os.getenv("SENDER_EMAIL", "greg@yirracare.com.au")
    sender_phone: str = os.getenv("SENDER_PHONE", "0474 525 811")
    company_name: str = os.getenv("COMPANY_NAME", "Yirra Care")
    company_website: str = os.getenv("COMPANY_WEBSITE", "https://yirracare.com.au")
    default_locations: str = os.getenv(
        "DEFAULT_LOCATIONS",
        "Brisbane North, Moreton Bay, Redcliffe, Clontarf, Rothwell, Morayfield, Caboolture",
    )

    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")
    google_cse_id: str | None = os.getenv("GOOGLE_CSE_ID")
    google_client_secret_file: str = os.getenv("GOOGLE_CLIENT_SECRET_FILE", "client_secret.json")
    google_token_file: str = os.getenv("GOOGLE_TOKEN_FILE", "token.json")

    create_drafts_only: bool = _bool(os.getenv("CREATE_DRAFTS_ONLY"), True)
    max_drafts_per_run: int = int(os.getenv("MAX_DRAFTS_PER_RUN", "20"))
    max_contacts_per_query: int = int(os.getenv("MAX_CONTACTS_PER_QUERY", "25"))
    request_delay_seconds: float = float(os.getenv("REQUEST_DELAY_SECONDS", "2"))


settings = Settings()
