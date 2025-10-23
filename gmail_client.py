"""
Gmail API client wrapper for fetching and processing emails.
"""
import base64
from email.mime.text import MIMEText
from typing import List, Dict, Optional


class GmailClient:
    """Wrapper for Gmail API operations."""

    def __init__(self, service):
        """
        Initialize Gmail client.

        Args:
            service: Authenticated Gmail API service
        """
        self.service = service

    def list_messages(self, max_results: int = 10, query: str = '') -> List[Dict]:
        """
        List messages from inbox.

        Args:
            max_results: Maximum number of messages to retrieve
            query: Gmail search query (optional)

        Returns:
            List of message dictionaries with full details
        """
        try:
            # Get message IDs
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q=query
            ).execute()

            messages = results.get('messages', [])

            # Fetch full message details for each
            full_messages = []
            for msg in messages:
                full_msg = self.get_message(msg['id'])
                if full_msg:
                    full_messages.append(full_msg)

            return full_messages

        except Exception as e:
            print(f"Error listing messages: {e}")
            return []

    def get_message(self, msg_id: str) -> Optional[Dict]:
        """
        Get full message details.

        Args:
            msg_id: Message ID

        Returns:
            Message dictionary with parsed details
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='full'
            ).execute()

            return self._parse_message(message)

        except Exception as e:
            print(f"Error getting message {msg_id}: {e}")
            return None

    def _parse_message(self, message: Dict) -> Dict:
        """
        Parse message into a more usable format.

        Args:
            message: Raw message from API

        Returns:
            Parsed message dictionary
        """
        headers = message['payload']['headers']

        # Extract common headers
        subject = self._get_header(headers, 'Subject')
        from_email = self._get_header(headers, 'From')
        to_email = self._get_header(headers, 'To')
        date = self._get_header(headers, 'Date')
        message_id = self._get_header(headers, 'Message-ID')

        # Extract body
        body_html = self._get_body(message['payload'], 'text/html')
        body_text = self._get_body(message['payload'], 'text/plain')

        return {
            'id': message['id'],
            'threadId': message['threadId'],
            'subject': subject,
            'from': from_email,
            'to': to_email,
            'date': date,
            'message_id': message_id,
            'snippet': message.get('snippet', ''),
            'body_html': body_html,
            'body_text': body_text,
            'raw': message
        }

    def _get_header(self, headers: List[Dict], name: str) -> str:
        """
        Extract header value by name.

        Args:
            headers: List of header dictionaries
            name: Header name to find

        Returns:
            Header value or empty string
        """
        for header in headers:
            if header['name'].lower() == name.lower():
                return header['value']
        return ''

    def _get_body(self, payload: Dict, mime_type: str) -> str:
        """
        Extract email body by MIME type.

        Args:
            payload: Message payload
            mime_type: MIME type to extract (text/plain or text/html)

        Returns:
            Decoded body content
        """
        if 'parts' in payload:
            # Multipart message
            for part in payload['parts']:
                if part['mimeType'] == mime_type:
                    if 'data' in part['body']:
                        return base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8', errors='ignore')
                # Check nested parts
                if 'parts' in part:
                    body = self._get_body(part, mime_type)
                    if body:
                        return body
        else:
            # Single part message
            if payload.get('mimeType') == mime_type:
                if 'data' in payload.get('body', {}):
                    return base64.urlsafe_b64decode(
                        payload['body']['data']
                    ).decode('utf-8', errors='ignore')

        return ''

    def get_raw_message(self, msg_id: str) -> Optional[bytes]:
        """
        Get raw RFC822 format message.

        Args:
            msg_id: Message ID

        Returns:
            Raw message bytes suitable for .eml file
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=msg_id,
                format='raw'
            ).execute()

            return base64.urlsafe_b64decode(message['raw'])

        except Exception as e:
            print(f"Error getting raw message {msg_id}: {e}")
            return None
