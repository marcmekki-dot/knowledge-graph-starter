# Manual Installation Guide

If you prefer to install components individually rather than using `install.sh`, follow these steps.

## 1. Knowledge Graph Directory

Create the directory structure:

```bash
mkdir -p ~/personal/{people,organizations,projects,logs}
mkdir -p ~/personal/knowledge/{my-methods,references}
```

Copy the template files:

```bash
cp templates/personal/work.md ~/personal/
cp templates/personal/personal.md ~/personal/
cp templates/personal/home.md ~/personal/
cp templates/personal/dashboard.md ~/personal/
cp templates/personal/knowledge/index.md ~/personal/knowledge/
cp templates/personal/knowledge/my-methods/_template.md ~/personal/knowledge/my-methods/
cp templates/personal/knowledge/references/_template.md ~/personal/knowledge/references/
```

## 2. CLAUDE.md

Copy the instructions file to your home directory:

```bash
cp CLAUDE.md ~/CLAUDE.md
```

This is the core of the system. Claude Code reads `~/CLAUDE.md` on every session start and follows these instructions for auto-logging, content routing, and knowledge management.

## 3. Email-to-KG (Email Sync Engine)

Copy the email sync engine:

```bash
cp -r email-to-kg ~/email-to-kg
```

Install Python dependencies:

```bash
pip3 install -r ~/email-to-kg/requirements.txt
```

Configure your email:

```bash
# Edit the config file
nano ~/email-to-kg/config/config.yaml

# Set your email address and IMAP server, then store credentials:
~/email-to-kg/setup.sh
```

### IMAP Server Reference

| Provider | IMAP Server |
|----------|-------------|
| Gmail | `imap.gmail.com` |
| Outlook/O365 | `outlook.office365.com` |
| AWS Workmail (US) | `imap.mail.us-east-1.awsapps.com` |
| AWS Workmail (EU) | `imap.mail.eu-west-1.awsapps.com` |
| Yahoo | `imap.mail.yahoo.com` |
| iCloud | `imap.mail.me.com` |
| Fastmail | `imap.fastmail.com` |

### Gmail Notes

Gmail requires an **App Password** instead of your regular password:
1. Go to https://myaccount.google.com/apppasswords
2. Create a new app password for "Mail"
3. Use this password in the setup script

## 4. Email-Sync Plugin

Install the Claude Code plugin:

```bash
mkdir -p ~/.claude/plugins/marketplaces/local/email-sync
cp -r plugin/email-sync/* ~/.claude/plugins/marketplaces/local/email-sync/
```

Enable it in Claude Code settings:

```bash
# If settings.json exists, add to enabledPlugins
# If not, create it:
cat > ~/.claude/settings.json << 'EOF'
{
  "enabledPlugins": {
    "email-sync@local": true
  }
}
EOF
```

**Important:** If you already have a `~/.claude/settings.json`, don't overwrite it. Instead, add `"email-sync@local": true` to the `enabledPlugins` object.

## 5. Mail-Context (Optional)

Mail-context provides advanced email search and enrichment. It requires:

1. `mbsync` (isstrstrstrync) to sync emails locally
2. A SQLite database indexed from your Maildir

### Install mbsync

```bash
# macOS
brew install isync

# Generate config
mail-context mbsync-config
```

### Install mail-context

```bash
git clone https://github.com/YOUR_USERNAME/mail-context.git ~/mail-context
cd ~/mail-context
pip3 install -e .
```

### Index your emails

```bash
# Sync emails locally first
mbsync -a

# Index into SQLite
mail-context index ~/.mail
```

## 6. Verify Installation

Test each component:

```bash
# Check CLAUDE.md is in place
cat ~/CLAUDE.md | head -5

# Check personal directory
ls ~/personal/

# Check email-to-kg
python3 ~/email-to-kg/main.py status

# Check plugin
ls ~/.claude/plugins/marketplaces/local/email-sync/

# Start Claude Code - it should run startup protocol
claude
```

## Uninstall

To remove the system:

```bash
rm ~/CLAUDE.md
rm -rf ~/email-to-kg
rm -rf ~/.claude/plugins/marketplaces/local/email-sync

# Remove credentials from Keychain
security delete-generic-password -s "email-to-kg"
security delete-generic-password -s "anthropic"

# Keep ~/personal/ - that's your data
```
