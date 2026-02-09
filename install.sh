#!/bin/bash
# Knowledge Graph Starter - Install Script
# Sets up the complete knowledge graph system for Claude Code

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PERSONAL_DIR="$HOME/personal"
EMAIL_TO_KG_DIR="$HOME/email-to-kg"
PLUGIN_DIR="$HOME/.claude/plugins/marketplaces/local/email-sync"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo ""
echo "============================================"
echo "  Knowledge Graph Starter for Claude Code"
echo "============================================"
echo ""

# ------------------------------------------------
# Step 1: Scaffold personal directory
# ------------------------------------------------
echo -e "${BLUE}Step 1: Setting up ~/personal/ knowledge graph${NC}"

if [ -d "$PERSONAL_DIR" ]; then
    echo -e "${YELLOW}  ~/personal/ already exists. Skipping scaffold (won't overwrite).${NC}"
else
    cp -r "$SCRIPT_DIR/templates/personal" "$PERSONAL_DIR"
    echo -e "${GREEN}  Created ~/personal/ with directory structure${NC}"
fi

# Ensure subdirectories exist even if personal/ already existed
mkdir -p "$PERSONAL_DIR"/{people,organizations,projects,logs}
mkdir -p "$PERSONAL_DIR"/knowledge/{my-methods,references}
echo "  Verified all subdirectories exist"

# Copy template files if they don't exist
for file in work.md personal.md home.md dashboard.md; do
    if [ ! -f "$PERSONAL_DIR/$file" ]; then
        cp "$SCRIPT_DIR/templates/personal/$file" "$PERSONAL_DIR/$file"
        echo "  Created $file"
    fi
done

if [ ! -f "$PERSONAL_DIR/knowledge/index.md" ]; then
    cp "$SCRIPT_DIR/templates/personal/knowledge/index.md" "$PERSONAL_DIR/knowledge/index.md"
    echo "  Created knowledge/index.md"
fi

for template in _template.md; do
    if [ ! -f "$PERSONAL_DIR/knowledge/my-methods/$template" ]; then
        cp "$SCRIPT_DIR/templates/personal/knowledge/my-methods/$template" "$PERSONAL_DIR/knowledge/my-methods/$template"
    fi
    if [ ! -f "$PERSONAL_DIR/knowledge/references/$template" ]; then
        cp "$SCRIPT_DIR/templates/personal/knowledge/references/$template" "$PERSONAL_DIR/knowledge/references/$template"
    fi
done
echo -e "${GREEN}  Knowledge graph scaffold complete${NC}"
echo ""

# ------------------------------------------------
# Step 2: Install CLAUDE.md
# ------------------------------------------------
echo -e "${BLUE}Step 2: Installing CLAUDE.md${NC}"

if [ -f "$HOME/CLAUDE.md" ]; then
    echo -e "${YELLOW}  ~/CLAUDE.md already exists.${NC}"
    read -p "  Overwrite with knowledge graph version? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$SCRIPT_DIR/CLAUDE.md" "$HOME/CLAUDE.md"
        echo -e "${GREEN}  Updated ~/CLAUDE.md${NC}"
    else
        echo "  Kept existing CLAUDE.md"
    fi
else
    cp "$SCRIPT_DIR/CLAUDE.md" "$HOME/CLAUDE.md"
    echo -e "${GREEN}  Installed ~/CLAUDE.md${NC}"
fi
echo ""

# ------------------------------------------------
# Step 3: Install email-to-kg
# ------------------------------------------------
echo -e "${BLUE}Step 3: Setting up email-to-kg (email sync engine)${NC}"

if [ -d "$EMAIL_TO_KG_DIR" ]; then
    echo -e "${YELLOW}  ~/email-to-kg/ already exists. Skipping copy.${NC}"
else
    cp -r "$SCRIPT_DIR/email-to-kg" "$EMAIL_TO_KG_DIR"
    echo -e "${GREEN}  Installed email-to-kg to ~/email-to-kg/${NC}"
fi

# Install Python dependencies
echo "  Installing Python dependencies..."
pip3 install -q -r "$EMAIL_TO_KG_DIR/requirements.txt" 2>/dev/null || {
    echo -e "${YELLOW}  pip3 install failed. Trying with --user flag...${NC}"
    pip3 install --user -q -r "$EMAIL_TO_KG_DIR/requirements.txt"
}
echo -e "${GREEN}  Python dependencies installed${NC}"
echo ""

# ------------------------------------------------
# Step 4: Configure email credentials
# ------------------------------------------------
echo -e "${BLUE}Step 4: Email configuration${NC}"
echo ""

read -p "  Do you want to configure email sync now? [Y/n] " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "  Supported email providers:"
    echo "    1. Amazon Workmail"
    echo "    2. Gmail"
    echo "    3. Outlook / Office 365"
    echo "    4. Other IMAP server"
    echo ""
    read -p "  Select provider [1-4]: " PROVIDER

    case $PROVIDER in
        1)
            IMAP_SERVER="imap.mail.us-east-1.awsapps.com"
            echo "  Note: Workmail IMAP server varies by region."
            echo "  Common servers:"
            echo "    US East: imap.mail.us-east-1.awsapps.com"
            echo "    EU West: imap.mail.eu-west-1.awsapps.com"
            read -p "  Enter your Workmail IMAP server [$IMAP_SERVER]: " CUSTOM_SERVER
            IMAP_SERVER="${CUSTOM_SERVER:-$IMAP_SERVER}"
            ;;
        2)
            IMAP_SERVER="imap.gmail.com"
            echo -e "${YELLOW}  Note: Gmail requires an App Password.${NC}"
            echo "  Create one at: https://myaccount.google.com/apppasswords"
            ;;
        3)
            IMAP_SERVER="outlook.office365.com"
            ;;
        4)
            read -p "  Enter IMAP server hostname: " IMAP_SERVER
            ;;
        *)
            IMAP_SERVER="imap.gmail.com"
            ;;
    esac

    echo ""
    read -p "  Enter your email address: " EMAIL_ADDRESS
    echo "  Enter your email password (stored in macOS Keychain):"
    read -rs EMAIL_PASSWORD
    echo ""

    # Store email password in Keychain
    security add-generic-password -s "email-to-kg" -a "$EMAIL_ADDRESS" -w "$EMAIL_PASSWORD" -U 2>/dev/null || \
    security add-generic-password -s "email-to-kg" -a "$EMAIL_ADDRESS" -w "$EMAIL_PASSWORD"
    echo -e "${GREEN}  Email password stored in Keychain${NC}"

    # Update config
    CONFIG_FILE="$EMAIL_TO_KG_DIR/config/config.yaml"
    sed -i '' "s|address: \".*\"|address: \"$EMAIL_ADDRESS\"|" "$CONFIG_FILE"
    sed -i '' "s|imap_server: \".*\"|imap_server: \"$IMAP_SERVER\"|" "$CONFIG_FILE"
    sed -i '' "s|keychain_service: \".*\"|keychain_service: \"email-to-kg\"|" "$CONFIG_FILE"
    echo -e "${GREEN}  Email config updated${NC}"

    echo ""
    echo "  Enter your Anthropic API key (for email classification):"
    read -rs API_KEY
    echo ""

    security add-generic-password -s "anthropic" -a "api_key" -w "$API_KEY" -U 2>/dev/null || \
    security add-generic-password -s "anthropic" -a "api_key" -w "$API_KEY"
    echo -e "${GREEN}  Anthropic API key stored in Keychain${NC}"

    # Ask about email filter domains
    echo ""
    echo "  Configure email filters (optional)."
    echo "  You can set domains to include (allowlist) or exclude (blocklist)."
    read -p "  Enter domains to process (comma-separated, or press Enter to skip): " DOMAINS

    if [ -n "$DOMAINS" ]; then
        # Clear existing domains and add new ones
        # This is a simple replacement - users can fine-tune config.yaml later
        echo -e "${GREEN}  Domains noted. Edit ~/email-to-kg/config/config.yaml to fine-tune filters.${NC}"
    fi
else
    echo "  Skipped. Run ~/email-to-kg/setup.sh later to configure."
fi
echo ""

# ------------------------------------------------
# Step 5: Install Claude Code plugin
# ------------------------------------------------
echo -e "${BLUE}Step 5: Installing email-sync Claude Code plugin${NC}"

mkdir -p "$PLUGIN_DIR"
cp -r "$SCRIPT_DIR/plugin/email-sync/"* "$PLUGIN_DIR/"
echo -e "${GREEN}  Plugin installed to $PLUGIN_DIR${NC}"

# Enable plugin in settings
SETTINGS_FILE="$HOME/.claude/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
    # Check if email-sync is already in settings
    if grep -q "email-sync@local" "$SETTINGS_FILE"; then
        echo "  Plugin already enabled in settings"
    else
        # Add to enabledPlugins using Python for safe JSON manipulation
        python3 -c "
import json
with open('$SETTINGS_FILE', 'r') as f:
    settings = json.load(f)
if 'enabledPlugins' not in settings:
    settings['enabledPlugins'] = {}
settings['enabledPlugins']['email-sync@local'] = True
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(settings, f, indent=2)
print('  Plugin enabled in settings.json')
"
    fi
else
    mkdir -p "$HOME/.claude"
    echo '{"enabledPlugins":{"email-sync@local":true}}' | python3 -m json.tool > "$SETTINGS_FILE"
    echo -e "${GREEN}  Created settings.json with plugin enabled${NC}"
fi
echo ""

# ------------------------------------------------
# Step 6: mail-context (optional)
# ------------------------------------------------
echo -e "${BLUE}Step 6: Mail-Context (advanced email search - optional)${NC}"
echo ""
echo "  mail-context provides:"
echo "    - Full-text search across your entire email archive"
echo "    - Thread reconstruction"
echo "    - AI-powered contact and organization enrichment"
echo ""
read -p "  Install mail-context? [y/N] " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "$HOME/mail-context" ]; then
        echo -e "${YELLOW}  ~/mail-context/ already exists. Skipping.${NC}"
    else
        echo "  mail-context requires a separate repository."
        echo "  Clone it from: https://github.com/marcmekki-dot/mail-context"
        echo ""
        read -p "  Enter the git URL (or press Enter to skip): " MC_URL
        if [ -n "$MC_URL" ]; then
            git clone "$MC_URL" "$HOME/mail-context"
            cd "$HOME/mail-context"
            pip3 install -e . 2>/dev/null || pip3 install --user -e .
            echo -e "${GREEN}  mail-context installed${NC}"
        else
            echo "  Skipped. Install manually later."
        fi
    fi
else
    echo "  Skipped. You can install mail-context later for advanced features."
fi
echo ""

# ------------------------------------------------
# Done
# ------------------------------------------------
echo "============================================"
echo -e "${GREEN}  Installation Complete!${NC}"
echo "============================================"
echo ""
echo "  What was installed:"
echo "    ~/CLAUDE.md              - Claude behavior instructions"
echo "    ~/personal/              - Knowledge graph directory"
echo "    ~/email-to-kg/           - Email sync engine"
echo "    ~/.claude/plugins/.../   - Email-sync plugin"
echo ""
echo "  Next steps:"
echo "    1. Start Claude Code:  claude"
echo "    2. Claude will run the startup protocol automatically"
echo "    3. Say 'sync emails' to pull in your first batch"
echo "    4. Say 'check emails' to see pending count"
echo "    5. Start chatting - tasks and notes are logged automatically"
echo ""
echo "  Useful commands:"
echo "    python3 ~/email-to-kg/main.py check     # Check for new emails"
echo "    python3 ~/email-to-kg/main.py sync      # Sync emails to KG"
echo "    python3 ~/email-to-kg/main.py status    # Show sync stats"
echo ""
echo "  Edit ~/email-to-kg/config/config.yaml to adjust settings."
echo ""
