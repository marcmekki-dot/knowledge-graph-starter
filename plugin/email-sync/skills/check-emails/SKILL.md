---
name: check-emails
description: Check for pending emails without syncing them. Shows how many new emails are waiting. Use when user asks "check emails", "any new emails?", or "how many emails".
tools: Bash
---

# Check Emails

Check for pending emails without processing them.

## Command

```bash
python3 ~/email-to-kg/main.py check -v
```

## What It Shows

- Number of unprocessed emails since last sync
- Subject lines of up to 10 pending emails (with -v flag)

## Use Cases

- Quick status check before deciding to run full sync
- See what's in your inbox without processing
