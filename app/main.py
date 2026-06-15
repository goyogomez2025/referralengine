import argparse
from rich.console import Console
from app.db import init_db
from app.workers import find_contacts, scrape_emails, qualify_contacts, write_emails, create_gmail_drafts, export_data, import_contacts

console = Console()


def cmd_init_db(args):
    init_db()
    console.print("[green]Database initialized.[/green]")


def cmd_find(args):
    init_db()
    count = find_contacts.run(query=args.query, limit=args.limit, campaign_id=getattr(args, "campaign", None))
    console.print(f"[green]Prospects found/saved:[/green] {count}")


def cmd_scrape(args):
    init_db()
    count = scrape_emails.run(limit=args.limit, location=args.location)
    console.print(f"[green]Contacts extracted:[/green] {count}")


def cmd_qualify(args):
    init_db()
    count = qualify_contacts.run(limit=args.limit)
    console.print(f"[green]Contacts qualified:[/green] {count}")


def cmd_write_emails(args):
    init_db()
    count = write_emails.run(campaign=args.campaign, limit=args.limit)
    console.print(f"[green]Emails written:[/green] {count}")


def cmd_create_drafts(args):
    init_db()
    count = create_gmail_drafts.run(limit=args.limit)
    console.print(f"[green]Gmail drafts created:[/green] {count}")


def cmd_export_contacts(args):
    path = export_data.export_contacts(args.path)
    console.print(f"[green]Contacts exported:[/green] {path}")


def cmd_export_emails(args):
    path = export_data.export_emails(args.path)
    console.print(f"[green]Emails exported:[/green] {path}")


def cmd_import_contacts(args):
    init_db()
    count = import_contacts.run(args.path)
    console.print(f"[green]Contacts imported:[/green] {count}")


def cmd_run_campaign(args):
    init_db()
    console.print("[bold]Step 1/4: finding prospects...[/bold]")
    prospects = find_contacts.run(query=args.query, limit=args.limit, campaign_id=args.campaign)
    console.print(f"Prospects saved: {prospects}")

    console.print("[bold]Step 2/4: scraping emails...[/bold]")
    contacts = scrape_emails.run(limit=args.limit, location=args.location)
    console.print(f"Contacts extracted: {contacts}")

    console.print("[bold]Step 3/4: qualifying contacts...[/bold]")
    qualified = qualify_contacts.run(limit=args.limit * 3)
    console.print(f"Contacts processed: {qualified}")

    console.print("[bold]Step 4/4: writing emails...[/bold]")
    emails = write_emails.run(campaign=args.campaign, limit=args.limit)
    console.print(f"Emails ready: {emails}")
    console.print("[yellow]Next: run `python -m app.main create-drafts --limit 10` after Gmail OAuth setup.[/yellow]")


def build_parser():
    parser = argparse.ArgumentParser(description="Yirra Referral Engine")
    sub = parser.add_subparsers(required=True)

    p = sub.add_parser("init-db")
    p.set_defaults(func=cmd_init_db)

    p = sub.add_parser("find")
    p.add_argument("--query", default=None)
    p.add_argument("--campaign", default=None)
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_find)

    p = sub.add_parser("scrape")
    p.add_argument("--limit", type=int, default=20)
    p.add_argument("--location", default="Brisbane North / Moreton Bay")
    p.set_defaults(func=cmd_scrape)

    p = sub.add_parser("qualify")
    p.add_argument("--limit", type=int, default=50)
    p.set_defaults(func=cmd_qualify)

    p = sub.add_parser("write-emails")
    p.add_argument("--campaign", default="cleaning_sc_brisbane")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_write_emails)

    p = sub.add_parser("create-drafts")
    p.add_argument("--limit", type=int, default=10)
    p.set_defaults(func=cmd_create_drafts)

    p = sub.add_parser("export-contacts")
    p.add_argument("--path", default="exports/contacts.csv")
    p.set_defaults(func=cmd_export_contacts)

    p = sub.add_parser("export-emails")
    p.add_argument("--path", default="exports/emails.csv")
    p.set_defaults(func=cmd_export_emails)

    p = sub.add_parser("import-contacts")
    p.add_argument("--path", required=True)
    p.set_defaults(func=cmd_import_contacts)

    p = sub.add_parser("run-campaign")
    p.add_argument("--campaign", default="cleaning_sc_brisbane")
    p.add_argument("--query", required=True)
    p.add_argument("--location", default="Brisbane North / Moreton Bay")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_run_campaign)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
