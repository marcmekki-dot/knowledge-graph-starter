"""
Email search with natural language query support.
"""

import re
import json
from datetime import datetime, timedelta, timezone


def _normalize_datetime(dt: datetime) -> datetime:
    """Normalize datetime to UTC for comparison. Handles both naive and aware."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        # Assume naive datetimes are UTC
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)
from typing import List, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class SearchQuery:
    """Parsed search query components."""
    keywords: List[str]
    sender: Optional[str]
    date_from: Optional[datetime]
    date_to: Optional[datetime]
    limit: int = 20


@dataclass
class SearchResult:
    """Single email search result."""
    message_id: str
    from_addr: str
    to_addr: str
    subject: str
    date: str
    body_preview: str
    match_context: str
    relevance_score: float


def parse_natural_query(query: str) -> SearchQuery:
    """
    Parse natural language query into structured search parameters.

    Examples:
    - "emails from John about budget" -> sender=John, keywords=[budget]
    - "last week's emails about the meeting" -> date_from=7 days ago, keywords=[meeting]
    - "find anything mentioning conference" -> keywords=[conference]
    """
    query_lower = query.lower()

    # Extract sender with "from X" pattern
    sender = None
    from_match = re.search(r'\bfrom\s+(\w+(?:\s+\w+)?)', query_lower)
    if from_match:
        sender = from_match.group(1)

    # Extract date ranges
    date_from = None
    date_to = None

    # "last week", "this week", "past week"
    if re.search(r'(last|this|past)\s+week', query_lower):
        date_from = datetime.now(timezone.utc) - timedelta(days=7)

    # "last month", "this month"
    elif re.search(r'(last|this|past)\s+month', query_lower):
        date_from = datetime.now(timezone.utc) - timedelta(days=30)

    # "yesterday"
    elif 'yesterday' in query_lower:
        date_from = datetime.now(timezone.utc) - timedelta(days=2)
        date_to = datetime.now(timezone.utc)

    # "today"
    elif 'today' in query_lower:
        date_from = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)

    # "last N days"
    days_match = re.search(r'last\s+(\d+)\s+days?', query_lower)
    if days_match:
        date_from = datetime.now(timezone.utc) - timedelta(days=int(days_match.group(1)))

    # Extract keywords (remove stopwords and query syntax)
    stopwords = {
        'find', 'search', 'show', 'get', 'any', 'all', 'me', 'my',
        'emails', 'email', 'messages', 'message', 'mail',
        'about', 'regarding', 'concerning', 'mentioning', 'containing',
        'with', 'the', 'a', 'an', 'and', 'or', 'for', 'in', 'on',
        'from', 'to', 'last', 'this', 'past', 'week', 'month', 'day', 'days',
        'yesterday', 'today', 'what', 'did', 'say', 'said', 'says',
        'anything', 'something', 'everything', 'recent', 'new', 'old'
    }

    words = re.findall(r'\b\w+\b', query_lower)
    keywords = [w for w in words if w not in stopwords and len(w) > 2]

    # Remove the sender name from keywords if present
    if sender:
        sender_parts = sender.lower().split()
        keywords = [k for k in keywords if k not in sender_parts]

    return SearchQuery(
        keywords=keywords,
        sender=sender,
        date_from=date_from,
        date_to=date_to,
        limit=20
    )


def search_emails(emails: List[Any], query: SearchQuery) -> List[SearchResult]:
    """
    Search emails based on parsed query.
    Returns results sorted by relevance.
    """
    results = []

    for email in emails:
        # Filter by sender if specified
        if query.sender:
            sender_lower = email.from_addr.lower()
            if query.sender.lower() not in sender_lower:
                continue

        # Filter by date range (normalize to handle mixed naive/aware datetimes)
        email_date = _normalize_datetime(email.date)
        if query.date_from and email_date < _normalize_datetime(query.date_from):
            continue
        if query.date_to and email_date > _normalize_datetime(query.date_to):
            continue

        # Score relevance based on keyword matches
        score = 0.0
        match_contexts = []

        for keyword in query.keywords:
            keyword_lower = keyword.lower()

            # Check subject (higher weight)
            if keyword_lower in email.subject.lower():
                score += 2.0
                match_contexts.append(f"Subject: '{keyword}'")

            # Check body
            if keyword_lower in email.body.lower():
                score += 1.0
                # Extract context snippet around the match
                idx = email.body.lower().find(keyword_lower)
                if idx >= 0:
                    start = max(0, idx - 40)
                    end = min(len(email.body), idx + len(keyword) + 40)
                    snippet = email.body[start:end].strip()
                    snippet = re.sub(r'\s+', ' ', snippet)  # Normalize whitespace
                    if start > 0:
                        snippet = "..." + snippet
                    if end < len(email.body):
                        snippet = snippet + "..."
                    match_contexts.append(snippet)

        # If no keywords specified, include all (filtered by sender/date)
        if not query.keywords:
            score = 1.0

        # Only include if there's a match
        if score > 0:
            # Create body preview
            body_preview = email.body[:500]
            if len(email.body) > 500:
                body_preview += "..."
            body_preview = re.sub(r'\s+', ' ', body_preview).strip()

            results.append(SearchResult(
                message_id=email.message_id,
                from_addr=email.from_addr,
                to_addr=email.to_addr,
                subject=email.subject,
                date=email.date.isoformat(),
                body_preview=body_preview,
                match_context=" | ".join(match_contexts[:3]) if match_contexts else "",
                relevance_score=score
            ))

    # Sort by relevance (highest first), then by date (newest first)
    results.sort(key=lambda r: (-r.relevance_score, r.date))

    return results[:query.limit]


def format_results_json(results: List[SearchResult], query: SearchQuery) -> str:
    """Format search results as JSON for Claude to interpret."""
    output = {
        "query": {
            "keywords": query.keywords,
            "sender": query.sender,
            "date_from": query.date_from.isoformat() if query.date_from else None,
            "date_to": query.date_to.isoformat() if query.date_to else None,
        },
        "result_count": len(results),
        "emails": [asdict(r) for r in results]
    }
    return json.dumps(output, indent=2)
