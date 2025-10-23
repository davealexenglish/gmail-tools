#!/usr/bin/env python3
"""
Gmail Tools - Command-line interface for Gmail operations.
"""
import click
from auth import get_gmail_service
from gmail_client import GmailClient
from filters import EmailFilter
from exporters import EmailExporter


@click.group()
def cli():
    """Gmail Tools - Manage your Gmail from the command line."""
    pass


@cli.command()
@click.option('--max-results', '-n', default=10, help='Number of emails to fetch')
@click.option('--query', '-q', default='', help='Gmail search query')
def list_emails(max_results, query):
    """List recent emails from inbox."""
    try:
        service = get_gmail_service()
        client = GmailClient(service)

        click.echo(f"Fetching {max_results} emails...")
        messages = client.list_messages(max_results=max_results, query=query)

        if not messages:
            click.echo("No messages found.")
            return

        click.echo(f"\nFound {len(messages)} emails:\n")

        for idx, msg in enumerate(messages, 1):
            click.echo(f"{idx}. Subject: {msg.get('subject', '(No Subject)')}")
            click.echo(f"   From: {msg.get('from', '')}")
            click.echo(f"   Date: {msg.get('date', '')}")
            click.echo(f"   Snippet: {msg.get('snippet', '')[:80]}...")
            click.echo()

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nPlease set up OAuth2 credentials first. See README.md", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option('--max-results', '-n', default=50, help='Number of emails to fetch')
@click.option('--keywords', '-k', multiple=True, required=True,
              help='Keywords to filter (can specify multiple times)')
@click.option('--subject-only', is_flag=True, help='Search subject only')
@click.option('--body-only', is_flag=True, help='Search body only')
@click.option('--case-sensitive', is_flag=True, help='Case-sensitive search')
@click.option('--output-dir', '-o', default='downloads', help='Output directory for EML files')
@click.option('--html', '-h', default='', help='Export to HTML file')
@click.option('--eml', is_flag=True, help='Export to EML files')
@click.option('--query', '-q', default='', help='Gmail search query (pre-filter)')
def filter_emails(max_results, keywords, subject_only, body_only,
                 case_sensitive, output_dir, html, eml, query):
    """Filter emails by keywords and export them."""
    try:
        service = get_gmail_service()
        client = GmailClient(service)

        click.echo(f"Fetching {max_results} emails...")
        messages = client.list_messages(max_results=max_results, query=query)

        if not messages:
            click.echo("No messages found.")
            return

        # Determine search locations
        search_subject = not body_only
        search_body = not subject_only

        # Apply keyword filter
        keywords_list = list(keywords)
        click.echo(f"Filtering by keywords: {', '.join(keywords_list)}")

        filtered = EmailFilter.filter_by_keywords(
            messages,
            keywords_list,
            search_subject=search_subject,
            search_body=search_body,
            case_sensitive=case_sensitive
        )

        if not filtered:
            click.echo("No messages matched the filter criteria.")
            return

        click.echo(f"\nFound {len(filtered)} matching emails:\n")

        # Display filtered emails
        for idx, msg in enumerate(filtered, 1):
            click.echo(f"{idx}. Subject: {msg.get('subject', '(No Subject)')}")
            click.echo(f"   From: {msg.get('from', '')}")
            click.echo(f"   Date: {msg.get('date', '')}")
            click.echo()

        # Export if requested
        if eml:
            click.echo(f"\nExporting to EML files in '{output_dir}'...")
            saved = EmailExporter.export_to_eml(filtered, client, output_dir)
            click.echo(f"Exported {len(saved)} emails to EML files.")

        if html:
            click.echo(f"\nExporting to HTML file '{html}'...")
            EmailExporter.export_to_html(filtered, html, sort_chronological=True)
            click.echo("HTML export complete.")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nPlease set up OAuth2 credentials first. See README.md", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option('--max-results', '-n', default=50, help='Number of emails to fetch')
@click.option('--output-dir', '-o', default='downloads', help='Output directory')
@click.option('--query', '-q', default='', help='Gmail search query')
def export_eml(max_results, output_dir, query):
    """Export emails to EML files."""
    try:
        service = get_gmail_service()
        client = GmailClient(service)

        click.echo(f"Fetching {max_results} emails...")
        messages = client.list_messages(max_results=max_results, query=query)

        if not messages:
            click.echo("No messages found.")
            return

        click.echo(f"Exporting {len(messages)} emails to '{output_dir}'...")
        saved = EmailExporter.export_to_eml(messages, client, output_dir)
        click.echo(f"\nExported {len(saved)} emails successfully.")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nPlease set up OAuth2 credentials first. See README.md", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.option('--max-results', '-n', default=50, help='Number of emails to fetch')
@click.option('--output', '-o', default='emails.html', help='Output HTML file')
@click.option('--query', '-q', default='', help='Gmail search query')
def export_html(max_results, output, query):
    """Export emails to HTML file."""
    try:
        service = get_gmail_service()
        client = GmailClient(service)

        click.echo(f"Fetching {max_results} emails...")
        messages = client.list_messages(max_results=max_results, query=query)

        if not messages:
            click.echo("No messages found.")
            return

        click.echo(f"Exporting {len(messages)} emails to '{output}'...")
        EmailExporter.export_to_html(messages, output, sort_chronological=True)
        click.echo("Export complete.")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        click.echo("\nPlease set up OAuth2 credentials first. See README.md", err=True)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)


if __name__ == '__main__':
    cli()
