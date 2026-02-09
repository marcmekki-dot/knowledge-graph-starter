#!/usr/bin/env python3
"""
Email to Knowledge Graph - CLI Entry Point

Syncs emails from your inbox to a personal knowledge graph.
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml

from src.email_client import EmailClient
from src.classifier import EmailClassifier
from src.router import ContentRouter
from src.state import SyncState
from src.filters import EmailFilter
from src.search import parse_natural_query, search_emails, format_results_json


def load_config(config_path: Path) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    # Expand paths
    config['paths']['personal_dir'] = Path(config['paths']['personal_dir']).expanduser()
    config['paths']['state_dir'] = Path(config['paths']['state_dir']).expanduser()

    return config


def cmd_sync(args, config: dict) -> int:
    """Sync emails and route to knowledge graph."""
    print("Starting email sync...")

    # Initialize components
    state = SyncState(config['paths']['state_dir'])
    classifier = EmailClassifier(model=config['anthropic']['model'])
    router = ContentRouter(config['paths']['personal_dir'])

    # Determine sync date
    last_sync = state.get_last_sync()
    if last_sync and not args.full:
        since_date = last_sync - timedelta(hours=1)  # Small overlap for safety
    else:
        since_date = datetime.now() - timedelta(days=config['sync']['days_lookback'])

    print(f"Fetching emails since {since_date.strftime('%Y-%m-%d %H:%M')}")

    # Connect and fetch emails
    email_config = config['email']
    client = EmailClient(
        email_address=email_config['address'],
        imap_server=email_config['imap_server'],
        imap_port=email_config['imap_port'],
        keychain_service=email_config['keychain_service']
    )

    try:
        with client:
            emails = client.fetch_emails(
                since_date=since_date,
                max_emails=config['sync']['max_emails']
            )
    except Exception as e:
        print(f"Error connecting to email: {e}")
        return 1

    print(f"Found {len(emails)} emails")

    # Initialize filter
    filter_config = config.get('filters', {})
    email_filter = EmailFilter(filter_config)

    # Process each email
    new_count = 0
    ignored_count = 0
    filtered_count = 0
    error_count = 0

    for email in emails:
        if state.is_seen(email):
            continue

        # Pre-classification filter (saves API calls)
        if not email_filter.should_process(email):
            reason = email_filter.get_reason(email)
            print(f"  [filtered] {email.subject[:40]}... ({reason})")
            filtered_count += 1
            state.mark_seen(email)
            continue

        try:
            # Classify
            classification = classifier.classify(email)

            if classification.category == "ignore":
                ignored_count += 1
                state.mark_seen(email)
                continue

            # Route to files
            modified = router.route(email, classification)

            if modified:
                print(f"  [{classification.category}] {email.subject[:50]}...")
                for f in modified:
                    print(f"    -> {Path(f).name}")
                new_count += 1

            state.mark_seen(email)

        except Exception as e:
            print(f"  Error processing: {email.subject[:50]}... - {e}")
            error_count += 1

    state.update_last_sync()

    print(f"\nSync complete:")
    print(f"  New items: {new_count}")
    print(f"  Filtered: {filtered_count}")
    print(f"  Ignored: {ignored_count}")
    print(f"  Errors: {error_count}")

    return 0


def cmd_status(args, config: dict) -> int:
    """Show sync status."""
    state = SyncState(config['paths']['state_dir'])
    stats = state.get_stats()

    print("Email Sync Status:")
    print(f"  Total processed: {stats['total_processed']}")
    print(f"  Last sync: {stats['last_sync'] or 'Never'}")

    return 0


def cmd_check(args, config: dict) -> int:
    """Check for pending emails without syncing."""
    print("Checking for new emails...")

    state = SyncState(config['paths']['state_dir'])
    last_sync = state.get_last_sync()
    since_date = last_sync if last_sync else datetime.now() - timedelta(days=config['sync']['days_lookback'])

    email_config = config['email']
    client = EmailClient(
        email_address=email_config['address'],
        imap_server=email_config['imap_server'],
        imap_port=email_config['imap_port'],
        keychain_service=email_config['keychain_service']
    )

    try:
        with client:
            emails = client.fetch_emails(since_date=since_date, max_emails=100)
    except Exception as e:
        print(f"Error: {e}")
        return 1

    # Count unseen
    unseen = [e for e in emails if not state.is_seen(e)]
    print(f"Pending emails: {len(unseen)}")

    if unseen and args.verbose:
        for email in unseen[:10]:
            print(f"  - {email.subject[:60]}")

    return 0


def cmd_reset(args, config: dict) -> int:
    """Reset sync state."""
    if not args.force:
        confirm = input("This will reset all sync state. Continue? [y/N] ")
        if confirm.lower() != 'y':
            print("Cancelled.")
            return 0

    state = SyncState(config['paths']['state_dir'])
    state.clear()
    print("Sync state reset.")
    return 0


def cmd_search(args, config: dict) -> int:
    """Search emails with natural language query."""
    import json

    query_text = args.query

    # Parse natural language query
    query = parse_natural_query(query_text)

    # Apply limit from args if provided
    if args.limit:
        query.limit = args.limit

    # Determine search date range
    # If no date specified in query, default to configured lookback
    if not query.date_from:
        query.date_from = datetime.now() - timedelta(days=config['sync']['days_lookback'])

    # Connect and fetch emails
    email_config = config['email']
    client = EmailClient(
        email_address=email_config['address'],
        imap_server=email_config['imap_server'],
        imap_port=email_config['imap_port'],
        keychain_service=email_config['keychain_service']
    )

    try:
        with client:
            max_fetch = args.max if args.max else 200
            emails = client.fetch_emails(
                since_date=query.date_from,
                max_emails=max_fetch
            )
    except Exception as e:
        error_output = {"error": str(e), "result_count": 0, "emails": []}
        print(json.dumps(error_output))
        return 1

    # Search and return results
    results = search_emails(emails, query)

    # Output as JSON for Claude to interpret
    print(format_results_json(results, query))

    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Sync emails to personal knowledge graph"
    )
    parser.add_argument(
        '--config', '-c',
        type=Path,
        default=Path(__file__).parent / 'config' / 'config.yaml',
        help='Path to config file'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # sync command
    sync_parser = subparsers.add_parser('sync', help='Sync emails to knowledge graph')
    sync_parser.add_argument('--full', action='store_true', help='Full sync (ignore last sync time)')

    # status command
    subparsers.add_parser('status', help='Show sync status')

    # check command
    check_parser = subparsers.add_parser('check', help='Check for pending emails')
    check_parser.add_argument('-v', '--verbose', action='store_true', help='Show email subjects')

    # reset command
    reset_parser = subparsers.add_parser('reset', help='Reset sync state')
    reset_parser.add_argument('-f', '--force', action='store_true', help='Skip confirmation')

    # search command
    search_parser = subparsers.add_parser('search', help='Search emails with natural language')
    search_parser.add_argument('query', type=str, help='Natural language search query')
    search_parser.add_argument('--limit', '-l', type=int, default=20, help='Max results to return')
    search_parser.add_argument('--max', '-m', type=int, default=200, help='Max emails to fetch from server')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Load config
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading config: {e}")
        return 1

    # Validate email address is set
    if not config['email']['address']:
        print("Error: Email address not configured in config/config.yaml")
        return 1

    # Route to command
    commands = {
        'sync': cmd_sync,
        'status': cmd_status,
        'check': cmd_check,
        'reset': cmd_reset,
        'search': cmd_search
    }

    return commands[args.command](args, config)


if __name__ == '__main__':
    sys.exit(main())
