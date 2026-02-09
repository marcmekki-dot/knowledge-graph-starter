"""
Email classifier using Claude API.
"""

import json
import subprocess
from dataclasses import dataclass
from typing import List, Optional
from anthropic import Anthropic


@dataclass
class ClassificationResult:
    """Result of email classification."""
    category: str  # work_task, personal_task, home_task, person_info, knowledge, log_entry, ignore
    priority: str  # P1, P2, P3
    people: List[str]  # Names of people mentioned
    deadline: Optional[str]  # ISO date if deadline found
    summary: str  # One-line summary
    action_items: List[str]  # Extracted action items
    tags: List[str]  # Additional tags


def get_anthropic_api_key() -> str:
    """Retrieve Anthropic API key from macOS Keychain."""
    try:
        result = subprocess.run(
            ["security", "find-generic-password", "-s", "anthropic", "-a", "api_key", "-w"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Failed to get Anthropic API key from Keychain: {e.stderr}")


CLASSIFICATION_PROMPT = """Analyze this email and extract structured information.

Email:
From: {from_addr}
To: {to_addr}
Subject: {subject}
Date: {date}

Body:
{body}

---

Classify and extract information as JSON with these fields:

- category: One of:
  - "work_task" - Work-related action items, project tasks, deadlines
  - "personal_task" - Personal goals, fitness, self-improvement tasks
  - "home_task" - Household, family, errands
  - "person_info" - Contact details, relationship context, meeting someone new
  - "knowledge" - Tools, concepts, learning materials worth saving
  - "log_entry" - FYI, general context, updates (no action needed)
  - "ignore" - Spam, newsletters, automated notifications, marketing

- priority: "P1" (urgent/today), "P2" (important/this week), "P3" (normal)

- people: Array of names mentioned (extract first name + last name if available)

- deadline: ISO date string if deadline mentioned, null otherwise

- summary: One concise sentence summarizing the email (under 100 chars)

- action_items: Array of specific actions needed (empty if none)

- tags: Array of relevant tags like "meeting", "followup", "waiting", "review"

Respond with ONLY valid JSON, no other text."""


class EmailClassifier:
    """Classifies emails using Claude API."""

    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.api_key = get_anthropic_api_key()
        self.client = Anthropic(api_key=self.api_key)
        self.model = model

    def classify(self, email) -> ClassificationResult:
        """Classify a single email."""
        prompt = CLASSIFICATION_PROMPT.format(
            from_addr=email.from_addr,
            to_addr=email.to_addr,
            subject=email.subject,
            date=email.date.isoformat(),
            body=email.body[:4000]  # Limit body size
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Parse JSON response
        response_text = response.content[0].text.strip()

        # Clean up response if wrapped in markdown
        if response_text.startswith("```"):
            lines = response_text.split("\n")
            response_text = "\n".join(lines[1:-1])

        try:
            data = json.loads(response_text)
        except json.JSONDecodeError as e:
            # Fallback for malformed JSON
            return ClassificationResult(
                category="log_entry",
                priority="P3",
                people=[],
                deadline=None,
                summary=email.subject[:100],
                action_items=[],
                tags=[]
            )

        return ClassificationResult(
            category=data.get("category", "log_entry"),
            priority=data.get("priority", "P3"),
            people=data.get("people", []),
            deadline=data.get("deadline"),
            summary=data.get("summary", email.subject[:100]),
            action_items=data.get("action_items", []),
            tags=data.get("tags", [])
        )
