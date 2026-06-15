import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
CAMPAIGNS_FILE = ROOT / "data" / "campaigns.json"

DEFAULT: dict = {}


def load() -> dict:
    if CAMPAIGNS_FILE.exists():
        return json.loads(CAMPAIGNS_FILE.read_text())
    return dict(DEFAULT)


def save(campaigns: dict) -> None:
    CAMPAIGNS_FILE.parent.mkdir(exist_ok=True)
    CAMPAIGNS_FILE.write_text(json.dumps(campaigns, indent=2, ensure_ascii=False))


def all_campaigns() -> list[dict]:
    return list(load().values())


def get(campaign_id: str) -> dict | None:
    return load().get(campaign_id)


def upsert(data: dict) -> dict:
    campaigns = load()
    cid = data.get("id") or _slugify(data["name"])
    data["id"] = cid
    campaigns[cid] = data
    save(campaigns)
    return data


def delete(campaign_id: str) -> None:
    campaigns = load()
    campaigns.pop(campaign_id, None)
    save(campaigns)


def _slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")
