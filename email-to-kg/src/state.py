"""
State management for email sync deduplication.
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Set, Optional


class SyncState:
    """Tracks processed emails for deduplication."""

    def __init__(self, state_dir: Path):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.seen_file = self.state_dir / "seen_emails.json"
        self.last_sync_file = self.state_dir / "last_sync.json"

        self.seen_ids: Set[str] = set()
        self._load_state()

    def _load_state(self) -> None:
        """Load state from disk."""
        if self.seen_file.exists():
            try:
                with open(self.seen_file, 'r') as f:
                    data = json.load(f)
                    self.seen_ids = set(data.get("message_ids", []))
            except (json.JSONDecodeError, KeyError):
                self.seen_ids = set()

    def _save_state(self) -> None:
        """Save state to disk."""
        with open(self.seen_file, 'w') as f:
            json.dump({
                "message_ids": list(self.seen_ids),
                "updated_at": datetime.now().isoformat()
            }, f, indent=2)

    def get_email_fingerprint(self, email) -> str:
        """
        Generate fingerprint for an email.
        Uses Message-ID if available, otherwise SHA256 of key fields.
        """
        if email.message_id:
            return email.message_id

        # Fallback fingerprint
        content = f"{email.from_addr}|{email.subject}|{email.date.isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()

    def is_seen(self, email) -> bool:
        """Check if email has already been processed."""
        fingerprint = self.get_email_fingerprint(email)
        return fingerprint in self.seen_ids

    def mark_seen(self, email) -> None:
        """Mark email as processed."""
        fingerprint = self.get_email_fingerprint(email)
        self.seen_ids.add(fingerprint)
        self._save_state()

    def get_last_sync(self) -> Optional[datetime]:
        """Get timestamp of last sync."""
        if self.last_sync_file.exists():
            try:
                with open(self.last_sync_file, 'r') as f:
                    data = json.load(f)
                    return datetime.fromisoformat(data["last_sync"])
            except (json.JSONDecodeError, KeyError, ValueError):
                return None
        return None

    def update_last_sync(self) -> None:
        """Update last sync timestamp."""
        with open(self.last_sync_file, 'w') as f:
            json.dump({
                "last_sync": datetime.now().isoformat()
            }, f, indent=2)

    def get_stats(self) -> dict:
        """Get sync statistics."""
        last_sync = self.get_last_sync()
        return {
            "total_processed": len(self.seen_ids),
            "last_sync": last_sync.isoformat() if last_sync else None
        }

    def clear(self) -> None:
        """Clear all state (for testing/reset)."""
        self.seen_ids = set()
        self._save_state()
        if self.last_sync_file.exists():
            self.last_sync_file.unlink()
