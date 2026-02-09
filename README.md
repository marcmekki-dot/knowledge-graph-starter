# Knowledge Graph Starter for Claude Code

A self-improving personal knowledge management system built on Claude Code. It automatically captures tasks, notes, and knowledge from your conversations and emails, routing everything to organized markdown files.

## What You Get

- **Auto-logging** - Claude automatically captures tasks, notes, and context from every conversation
- **Content routing** - Tasks go to the right file (work, personal, home) with priority markers and tags
- **Knowledge graph** - Build a personal wiki of your methods, references, people, and organizations
- **Email sync** - Connect your email inbox and have Claude classify, extract, and route email content
- **Email search** - Natural language search across your entire email archive
- **Profile enrichment** - Build rich profiles of contacts and organizations from email history
- **Daily logs** - Automatic session activity tracking
- **Weekly reviews** - Friday prompts to review and reprioritize

## Architecture

```
You (Claude Code CLI)
        |
   CLAUDE.md (behavior rules + content routing)
        |
   ~/personal/ (your knowledge graph - markdown files)
   |   ├── work.md, personal.md, home.md (task trackers)
   |   ├── people/ (contact profiles)
   |   ├── organizations/ (company profiles)
   |   ├── projects/ (project files)
   |   ├── knowledge/ (methods + references)
   |   └── logs/ (daily session logs)
   |
   email-to-kg (Python - email sync engine)
   |   └── IMAP → Claude API classification → markdown routing
   |
   mail-context (Python - email search + enrichment)
       └── Maildir → SQLite FTS5 → search/enrich tools
```

## Prerequisites

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) installed and configured
- Python 3.10+
- macOS (uses Keychain for credential storage)
- An email account with IMAP access (Amazon Workmail, Gmail, Outlook, etc.)
- An Anthropic API key

## Quick Start

```bash
git clone https://github.com/YOUR_USERNAME/knowledge-graph-starter.git
cd knowledge-graph-starter
./install.sh
```

The install script will:
1. Scaffold your `~/personal/` knowledge graph directory
2. Install `CLAUDE.md` to your home directory
3. Set up the email-to-kg sync engine
4. Install the email-sync Claude Code plugin
5. Store your credentials securely in macOS Keychain
6. Optionally install mail-context for advanced email search

## Manual Installation

If you prefer to install components individually, see [MANUAL_INSTALL.md](MANUAL_INSTALL.md).

## Components

### 1. CLAUDE.md (Core Instructions)

The brain of the system. Place at `~/CLAUDE.md`. It tells Claude how to:
- Automatically log tasks and notes from conversations
- Route content to the right files
- Use priority markers ([P1], [P2], [P3]) and tags (@person, @deadline, etc.)
- Run startup checks and weekly reviews
- Maintain and enrich your knowledge graph

### 2. Personal Knowledge Graph (`~/personal/`)

A directory of markdown files organized as:

| File/Directory | Purpose |
|---|---|
| `work.md` | Work tasks with priorities and deadlines |
| `personal.md` | Personal goals and self-improvement |
| `home.md` | Household, family, errands |
| `people/{name}.md` | Contact profiles with interaction history |
| `organizations/{name}.md` | Company profiles with relationships |
| `projects/{name}.md` | Project tracking and notes |
| `knowledge/my-methods/` | Your own frameworks and processes |
| `knowledge/references/` | Third-party tools, concepts, research |
| `logs/YYYY-MM-DD.md` | Daily session activity logs |

All files are plain markdown. You can open them in any editor, or use [Obsidian](https://obsidian.md) for wiki-style navigation with `[[wikilinks]]`.

### 3. Email-to-KG (Email Sync Engine)

A Python CLI that connects to your email via IMAP, classifies each email using Claude API (Haiku - fast and cheap), and routes the extracted content to your knowledge graph files.

**Classification categories:**
- `work_task` → work.md
- `personal_task` → personal.md
- `home_task` → home.md
- `person_info` → people/{name}.md
- `knowledge` → knowledge/references/
- `log_entry` → logs/{date}.md
- `ignore` → skipped

### 4. Email-Sync Plugin (Claude Code Plugin)

A local Claude Code plugin that adds skills and a session hook:

**Skills (slash commands):**
- `/sync-emails` - Sync your inbox to the knowledge graph
- `/check-emails` - Check how many new emails are pending
- `/email-status` - Show sync statistics
- `/search-emails` - Search emails with natural language
- `/enrich-person` - Build a contact profile from email history
- `/enrich-org` - Build an organization profile from email history

**Session hook:** Automatically checks for new emails when you start Claude Code.

### 5. Mail-Context (Optional - Advanced Email Search)

A more powerful email tool that:
- Indexes your entire Maildir into SQLite with FTS5 full-text search
- Provides instant search across thousands of emails
- Reconstructs email threads
- Generates AI-powered summaries
- Powers the enrichment commands

This is optional but recommended for power users with large email volumes.

## Configuration

### Email Filters

In `email-to-kg/config/config.yaml`, configure which emails to process:

```yaml
filters:
  mode: "allowlist"  # or "blocklist"
  domains:
    - "yourcompany.com"
    - "client.com"
  addresses: []
  patterns: []
```

### Priority System

| Marker | Meaning |
|--------|---------|
| `[P1]` | Urgent - needs attention today |
| `[P2]` | Important - this week |
| `[P3]` | Normal - when time permits |

### Tags

| Tag | Meaning |
|-----|---------|
| `@person:Name` | Involves a specific person |
| `@deadline:Date` | Has a deadline |
| `@waiting` | Waiting on someone else |
| `@followup` | Needs follow-up |

## Daily Workflow

1. **Start Claude Code** - The system automatically checks for new emails and surfaces urgent items
2. **Work normally** - As you discuss tasks, Claude logs them to the right files
3. **Say "sync emails"** - Pull new emails into your knowledge graph
4. **Ask about anyone** - "Tell me about John Smith" enriches their profile from emails
5. **Search emails** - "What did Sarah say about the budget?" searches your archive
6. **Friday review** - Claude prompts you to review and reprioritize

## Customization

### Adding Your Own Methods

When you share how you do something ("Here's my approach to X"), Claude saves it to `knowledge/my-methods/`. Use the template in `knowledge/my-methods/_template.md`.

### Adding More Email Providers

The email-to-kg system works with any IMAP server. Update `config/config.yaml`:

```yaml
email:
  address: "you@gmail.com"
  imap_server: "imap.gmail.com"  # Gmail
  # imap_server: "outlook.office365.com"  # Outlook/O365
  # imap_server: "imap.mail.us-east-1.awsapps.com"  # AWS Workmail
  imap_port: 993
  keychain_service: "email-to-kg"
```

### Obsidian Integration

The `~/personal/` directory works as an Obsidian vault out of the box. Just open it as a vault in Obsidian. The `[[wikilinks]]` in knowledge/index.md and cross-references between files will work automatically.

## Troubleshooting

**"Failed to get password from Keychain"**
Run `./email-to-kg/setup.sh` to re-store credentials.

**"Error connecting to email"**
Check your IMAP server address and port in `config/config.yaml`. For Gmail, you may need to enable "Less secure apps" or use an App Password.

**Emails not being classified correctly**
Adjust the classification model in `config/config.yaml`. The default `claude-3-haiku-20240307` is fast and cheap. Use `claude-sonnet-4-5-20250929` for better accuracy at higher cost.

**Plugin not loading**
Ensure `email-sync@local` is enabled in `~/.claude/settings.json`:
```json
{
  "enabledPlugins": {
    "email-sync@local": true
  }
}
```

## Security

- All credentials are stored in macOS Keychain (never in config files)
- Email content is processed locally
- Only email text is sent to Claude API for classification (no attachments)
- Your knowledge graph lives entirely on your local filesystem

## License

MIT
