"""
Gmail OAuth2 Setup Helper
─────────────────────────
Run this ONCE after placing client_secret.json in the project root.
It opens your browser, asks you to authorise access, then saves token.json.

Usage:
    python setup_gmail_auth.py
"""

from pathlib import Path


def main():
    secret_file = Path("client_secret.json")
    if not secret_file.exists():
        print(
            "\n❌  client_secret.json not found.\n\n"
            "Steps to get it:\n"
            "  1. Go to https://console.cloud.google.com/\n"
            "  2. Select (or create) your project.\n"
            "  3. APIs & Services → Enable APIs → search 'Gmail API' → Enable.\n"
            "  4. APIs & Services → Credentials → + CREATE CREDENTIALS → OAuth client ID.\n"
            "  5. Application type: Desktop app.  Give it a name.\n"
            "  6. Download the JSON file, rename it client_secret.json.\n"
            "  7. Place it in the project root (same folder as this script).\n"
            "  8. Re-run:  python setup_gmail_auth.py\n"
        )
        return

    from google.oauth2.credentials import Credentials  # noqa: F401
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request  # noqa: F401
    from googleapiclient.discovery import build  # noqa: F401

    SCOPES = ["https://mail.google.com/"]
    token_path = Path("token.json")

    flow = InstalledAppFlow.from_client_secrets_file(str(secret_file), SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json())

    print("\n✅  token.json saved.  Gmail is ready.\n")
    print("Next steps:")
    print("  python -m app.main find --limit 20")
    print("  python -m app.main scrape --limit 20")
    print("  python -m app.main qualify --limit 50")
    print("  python -m app.main write-emails --campaign cleaning_sc_brisbane --limit 20")
    print("  python -m app.main create-drafts --limit 10")


if __name__ == "__main__":
    main()
