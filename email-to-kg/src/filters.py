"""
Email filtering for pre-classification filtering.
"""

import re
from typing import List, Optional


class EmailFilter:
    """Filter emails by sender domain, address, or pattern."""

    def __init__(self, config: dict):
        """
        Initialize filter from config.

        Config format:
            mode: "blocklist" or "allowlist"
            domains: ["uber.com", "linkedin.com"]
            addresses: ["noreply@example.com"]
            patterns: ["^newsletter", "unsubscribe"]
        """
        self.mode = config.get('mode', 'blocklist')
        self.domains = set(d.lower() for d in (config.get('domains') or []))
        self.addresses = set(a.lower() for a in (config.get('addresses') or []))
        self.patterns = [re.compile(p, re.IGNORECASE) for p in (config.get('patterns') or [])]

    def should_process(self, email) -> bool:
        """
        Check if email should be processed.

        Returns True if email should be classified and routed.
        Returns False if email should be skipped.
        """
        matches = self._matches_filter(email)

        if self.mode == 'blocklist':
            # Process if NOT in blocklist
            return not matches
        else:
            # Process if IN allowlist
            return matches

    def _matches_filter(self, email) -> bool:
        """Check if email matches any filter criteria."""
        from_addr = email.from_addr.lower()
        email_addr = self._extract_email(from_addr)
        domain = self._extract_domain(email_addr)

        # Check domain
        if domain and domain in self.domains:
            return True

        # Check exact address
        if email_addr and email_addr in self.addresses:
            return True

        # Check patterns against full from_addr
        for pattern in self.patterns:
            if pattern.search(from_addr):
                return True

        return False

    def _extract_email(self, from_addr: str) -> Optional[str]:
        """
        Extract email address from From header.

        "John Doe <john@example.com>" -> "john@example.com"
        "john@example.com" -> "john@example.com"
        """
        # Try to extract from angle brackets
        match = re.search(r'<([^>]+)>', from_addr)
        if match:
            return match.group(1).lower()

        # Check if it's already just an email
        if '@' in from_addr:
            return from_addr.strip().lower()

        return None

    def _extract_domain(self, email_addr: Optional[str]) -> Optional[str]:
        """Extract domain from email address."""
        if not email_addr or '@' not in email_addr:
            return None

        return email_addr.split('@')[1].lower()

    def get_reason(self, email) -> str:
        """Get human-readable reason why email was filtered."""
        from_addr = email.from_addr.lower()
        email_addr = self._extract_email(from_addr)
        domain = self._extract_domain(email_addr)

        if domain and domain in self.domains:
            return f"domain:{domain}"

        if email_addr and email_addr in self.addresses:
            return f"address:{email_addr}"

        for pattern in self.patterns:
            if pattern.search(from_addr):
                return f"pattern:{pattern.pattern}"

        return "no match"
