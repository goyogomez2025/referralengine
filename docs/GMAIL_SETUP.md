# Gmail Setup

The project creates Gmail drafts, not automatic sends.

## Steps

1. Go to Google Cloud Console.
2. Create a project.
3. Enable Gmail API.
4. Configure OAuth consent screen.
5. Create OAuth Client ID for Desktop App.
6. Download JSON credentials.
7. Rename it to `client_secret.json`.
8. Place it in project root.
9. Run:

```bash
python -m app.main create-drafts --limit 1
```

A browser window opens. Log in with the Gmail account you want to create drafts from.

The app stores `token.json` locally. Do not upload it to GitHub.

## Scope used

`https://www.googleapis.com/auth/gmail.compose`

This is enough to create drafts. It does not need full mailbox access.
