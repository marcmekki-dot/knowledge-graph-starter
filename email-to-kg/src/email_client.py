"""
Email client for IMAP connection.

Supports any IMAP server (Gmail, Outlook, Amazon Workmail, etc.)
"""

from __future__ import annotations

import imaplib
import email as email_lib
from email.header import decode_header
from email.message import Message as EmailMessage
from email.utils import parsedate_to_datetime
from datetime import datetime, timedelta
from typing import List, Optional, Any
import subprocess
import re


class Email:
    """Parsed email object."""

    def __init__(
        self,
        message_id: str,
        from_addr: str,
        to_addr: str,
        subject: str,
        body: str,
        date: datetime,
        raw_email: Any
    ):
        self.message_id = message_id
        self.from_addr = from_addr
        self.to_addr = to_addr
        self.subject = subject
        self.body = body
        self.date = date
        self.raw_email = raw_email

    def __repr__(self):
        return f"Email(from={self.from_addr}, subject={self.subject[:50]}...)"


def get_keychain_password(service: str, account: str) -> str:
    """Retrieve password from macOS Keychain."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", service, "-a", account, "-w"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to get password from Keychain for {service}/{account}: {e.stderr}")


def decode_mime_header(header: Optional[str]) -> str:
    """Decode MIME encoded header to string."""
    if not header:
        return ""

    decoded_parts = []
    for part, charset in decode_header(header):
        if isinstance(part, bytes):
            decoded_parts.append(part.decode(charset or 'utf-8', errors='replace'))
        else:
            decoded_parts.append(part)

    return ' '.join(decoded_parts)


def extract_email_body(msg: EmailMessage) -> str:
    """Extract plain text body from email message."""
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    charset = part.get_content_charset() or 'utf-8'
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode(charset, errors='replace')
                        break
                except Exception:
                    continue
    else:
        content_type = msg.get_content_type()
        if content_type == "text/plain":
            try:
                charset = msg.get_content_charset() or 'utf-8'
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode(charset, errors='replace')
            except Exception:
                pass

    # Clean up body
    body = re.sub(r'\r\n', '\n', body)
    body = re.sub(r'\n{3,}', '\n\n', body)

    return body.strip()


class EmailClient:
    """IMAP client for email servers."""

    def __init__(
        self,
        email_address: str,
        imap_server: str = "imap.gmail.com",
        imap_port: int = 993,
        keychain_service: str = "email-to-kg"
    ):
        self.email_address = email_address
        self.imap_server = imap_server
        self.imap_port = imap_port
        self.keychain_service = keychain_service
        self.connection: Optional[imaplib.IMAP4_SSL] = None

    def connect(self) -> None:
        """Connect to IMAP server."""
        password = get_keychain_password(self.keychain_service, self.email_address)

        self.connection = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
        self.connection.login(self.email_address, password)

    def disconnect(self) -> None:
        """Disconnect from IMAP server."""
        if self.connection:
            try:
                self.connection.logout()
            except Exception:
                pass
            self.connection = None

    def fetch_emails(
        self,
        folder: str = "INBOX",
        since_date: Optional[datetime] = None,
        max_emails: int = 50
    ) -> List[Email]:
        """Fetch emails from specified folder."""
        if not self.connection:
            raise RuntimeError("Not connected to IMAP server")

        self.connection.select(folder)

        # Build search criteria
        if since_date:
            date_str = since_date.strftime("%d-%b-%Y")
            search_criteria = f'(SINCE {date_str})'
        else:
            # Default to last 7 days
            week_ago = datetime.now() - timedelta(days=7)
            date_str = week_ago.strftime("%d-%b-%Y")
            search_criteria = f'(SINCE {date_str})'

        _, message_numbers = self.connection.search(None, search_criteria)

        if not message_numbers[0]:
            return []

        email_ids = message_numbers[0].split()

        # Limit to most recent emails
        email_ids = email_ids[-max_emails:]

        emails = []
        for email_id in email_ids:
            try:
                _, msg_data = self.connection.fetch(email_id, "(RFC822)")

                if msg_data[0] is None:
                    continue

                raw_email = email_lib.message_from_bytes(msg_data[0][1])

                # Extract fields
                message_id = raw_email.get("Message-ID", "")
                from_addr = decode_mime_header(raw_email.get("From", ""))
                to_addr = decode_mime_header(raw_email.get("To", ""))
                subject = decode_mime_header(raw_email.get("Subject", ""))

                # Parse date
                date_str = raw_email.get("Date", "")
                try:
                    date = parsedate_to_datetime(date_str)
                except Exception:
                    date = datetime.now()

                # Extract body
                body = extract_email_body(raw_email)

                emails.append(Email(
                    message_id=message_id,
                    from_addr=from_addr,
                    to_addr=to_addr,
                    subject=subject,
                    body=body,
                    date=date,
                    raw_email=raw_email
                ))

            except Exception as e:
                print(f"Error parsing email {email_id}: {e}")
                continue

        return emails

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
