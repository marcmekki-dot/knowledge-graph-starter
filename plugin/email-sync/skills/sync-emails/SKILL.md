---
name: sync-emails
description: Sync emails from your inbox to your personal knowledge graph. Classifies emails and routes them to work.md, personal.md, home.md, people files, and daily logs. Use when user says "sync emails", "sync my inbox", or "get new emails".
tools: Bash
---

# Email Sync

Sync your inbox to the personal knowledge graph.

## Command

```bash
python3 ~/email-to-kg/main.py sync
```

## What It Does

1. Connects to your email server via IMAP
2. Fetches new emails since last sync
3. Classifies each email using Claude API (Haiku)
4. Routes content to appropriate files:
   - Work tasks -> `personal/work.md`
   - Personal tasks -> `personal/personal.md`
   - Home/errands -> `personal/home.md`
   - People info -> `personal/people/{name}.md`
   - Knowledge -> `personal/knowledge/references/`
   - Activity -> `personal/logs/YYYY-MM-DD.md`

## Options

- `--full` - Full sync (ignore last sync time, re-fetch all emails from lookback period)

## After Running

Report what was synced:
- Number of new items added
- Which files were modified
- Any errors encountered
