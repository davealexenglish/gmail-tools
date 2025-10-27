"""
Email export utilities for EML and HTML formats.
"""
import os
from typing import List, Dict
from datetime import datetime
from email.utils import parsedate_to_datetime
import html


class EmailExporter:
    """Export emails to various formats."""

    @staticmethod
    def export_to_eml(
        messages: List[Dict],
        gmail_client,
        output_dir: str = 'downloads'
    ) -> List[str]:
        """
        Export messages to .eml files.

        Args:
            messages: List of message dictionaries
            gmail_client: GmailClient instance for fetching raw messages
            output_dir: Directory to save .eml files

        Returns:
            List of saved file paths
        """
        os.makedirs(output_dir, exist_ok=True)
        saved_files = []

        for msg in messages:
            msg_id = msg['id']
            raw_message = gmail_client.get_raw_message(msg_id)

            if raw_message:
                # Create safe filename from subject and ID
                subject = msg.get('subject', 'no-subject')
                safe_subject = EmailExporter._sanitize_filename(subject)
                filename = f"{safe_subject}_{msg_id[:8]}.eml"
                filepath = os.path.join(output_dir, filename)

                with open(filepath, 'wb') as f:
                    f.write(raw_message)

                saved_files.append(filepath)
                print(f"Saved: {filepath}")

        return saved_files

    @staticmethod
    def export_to_html(
        messages: List[Dict],
        output_file: str = 'emails.html',
        sort_chronological: bool = True,
        reverse: bool = False
    ) -> str:
        """
        Export messages to a single HTML file.

        Args:
            messages: List of message dictionaries
            output_file: Output HTML file path
            sort_chronological: Sort emails chronologically
            reverse: Sort in reverse order (newest first)

        Returns:
            Path to saved HTML file
        """
        if sort_chronological:
            def parse_date(msg):
                try:
                    date_str = msg.get('date', '')
                    if date_str:
                        return parsedate_to_datetime(date_str)
                    return datetime.min
                except Exception:
                    return datetime.min

            messages = sorted(messages, key=parse_date, reverse=reverse)

        html_content = EmailExporter._generate_html(messages)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        print(f"Saved HTML: {output_file}")
        return output_file

    @staticmethod
    def _generate_html(messages: List[Dict]) -> str:
        """
        Generate HTML content from messages.

        Args:
            messages: List of message dictionaries

        Returns:
            HTML string
        """
        html_parts = ["""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gmail Export</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .email-container {
            background-color: white;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .email-header {
            background-color: #f8f9fa;
            padding: 15px 20px;
            border-bottom: 1px solid #dee2e6;
        }
        .email-subject {
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 8px;
            color: #212529;
        }
        .email-meta {
            font-size: 13px;
            color: #6c757d;
            margin: 3px 0;
        }
        .email-body {
            padding: 20px;
            line-height: 1.6;
        }
        .email-body iframe {
            width: 100%;
            border: none;
            min-height: 400px;
        }
        .label {
            font-weight: 600;
            margin-right: 5px;
        }
        h1 {
            color: #212529;
            border-bottom: 3px solid #007bff;
            padding-bottom: 10px;
        }
        .summary {
            background-color: white;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
</head>
<body>
    <h1>Gmail Export</h1>
    <div class="summary">
        <p><strong>Total Emails:</strong> """ + str(len(messages)) + """</p>
        <p><strong>Generated:</strong> """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """</p>
    </div>
"""]

        for idx, msg in enumerate(messages, 1):
            subject = html.escape(msg.get('subject', '(No Subject)'))
            from_email = html.escape(msg.get('from', ''))
            to_email = html.escape(msg.get('to', ''))
            date = html.escape(msg.get('date', ''))

            # Use HTML body if available, otherwise plain text
            body = msg.get('body_html', '')
            if not body:
                body_text = msg.get('body_text', msg.get('snippet', ''))
                body = '<pre>' + html.escape(body_text) + '</pre>'

            email_html = f"""
    <div class="email-container" id="email-{idx}">
        <div class="email-header">
            <div class="email-subject">{subject}</div>
            <div class="email-meta"><span class="label">From:</span>{from_email}</div>
            <div class="email-meta"><span class="label">To:</span>{to_email}</div>
            <div class="email-meta"><span class="label">Date:</span>{date}</div>
        </div>
        <div class="email-body">
            {body}
        </div>
    </div>
"""
            html_parts.append(email_html)

        html_parts.append("""
</body>
</html>
""")

        return ''.join(html_parts)

    @staticmethod
    def _sanitize_filename(filename: str, max_length: int = 50) -> str:
        """
        Create a safe filename from a string.

        Args:
            filename: Original filename/subject
            max_length: Maximum length for filename

        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        safe = ''.join(c for c in filename if c.isalnum() or c in (' ', '-', '_'))
        # Replace spaces with underscores
        safe = safe.replace(' ', '_')
        # Truncate if too long
        if len(safe) > max_length:
            safe = safe[:max_length]
        # Remove trailing underscores
        safe = safe.rstrip('_')
        return safe or 'email'
