"""
Email filtering utilities.
"""
import re
from typing import List, Dict


class EmailFilter:
    """Filter emails based on various criteria."""

    @staticmethod
    def filter_by_keywords(
        messages: List[Dict],
        keywords: List[str],
        search_subject: bool = True,
        search_body: bool = True,
        case_sensitive: bool = False
    ) -> List[Dict]:
        """
        Filter messages by keywords in subject and/or body.

        Args:
            messages: List of message dictionaries
            keywords: List of keywords to search for
            search_subject: Search in subject line
            search_body: Search in body text
            case_sensitive: Whether search is case-sensitive

        Returns:
            Filtered list of messages
        """
        if not keywords:
            return messages

        filtered = []

        for msg in messages:
            if EmailFilter._message_matches_keywords(
                msg, keywords, search_subject, search_body, case_sensitive
            ):
                filtered.append(msg)

        return filtered

    @staticmethod
    def _message_matches_keywords(
        message: Dict,
        keywords: List[str],
        search_subject: bool,
        search_body: bool,
        case_sensitive: bool
    ) -> bool:
        """
        Check if message matches any keyword.

        Args:
            message: Message dictionary
            keywords: Keywords to search for
            search_subject: Search in subject
            search_body: Search in body
            case_sensitive: Case-sensitive search

        Returns:
            True if any keyword matches
        """
        search_text = ''

        if search_subject:
            search_text += message.get('subject', '') + ' '

        if search_body:
            search_text += message.get('body_text', '') + ' '
            search_text += message.get('body_html', '') + ' '
            search_text += message.get('snippet', '')

        if not case_sensitive:
            search_text = search_text.lower()
            keywords = [k.lower() for k in keywords]

        # Check if any keyword matches
        for keyword in keywords:
            if keyword in search_text:
                return True

        return False

    @staticmethod
    def filter_by_sender(
        messages: List[Dict],
        sender_pattern: str
    ) -> List[Dict]:
        """
        Filter messages by sender email pattern.

        Args:
            messages: List of message dictionaries
            sender_pattern: Regex pattern to match sender

        Returns:
            Filtered list of messages
        """
        pattern = re.compile(sender_pattern, re.IGNORECASE)
        filtered = []

        for msg in messages:
            from_email = msg.get('from', '')
            if pattern.search(from_email):
                filtered.append(msg)

        return filtered

    @staticmethod
    def filter_by_date_range(
        messages: List[Dict],
        start_date: str = None,
        end_date: str = None
    ) -> List[Dict]:
        """
        Filter messages by date range.
        Note: For simplicity, this uses the date string comparison.
        For production use, consider proper date parsing.

        Args:
            messages: List of message dictionaries
            start_date: Start date string
            end_date: End date string

        Returns:
            Filtered list of messages
        """
        filtered = []

        for msg in messages:
            date = msg.get('date', '')

            if start_date and date < start_date:
                continue
            if end_date and date > end_date:
                continue

            filtered.append(msg)

        return filtered

    @staticmethod
    def sort_by_date(
        messages: List[Dict],
        reverse: bool = False
    ) -> List[Dict]:
        """
        Sort messages chronologically by date.

        Args:
            messages: List of message dictionaries
            reverse: Sort in reverse order (newest first)

        Returns:
            Sorted list of messages
        """
        return sorted(
            messages,
            key=lambda m: m.get('date', ''),
            reverse=reverse
        )
