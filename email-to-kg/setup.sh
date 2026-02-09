#!/bin/bash
# Email to Knowledge Graph - Credential Setup Script
# Stores email and API credentials in macOS Keychain

set -e

echo "=== Email to Knowledge Graph - Credential Setup ==="
echo ""

# Check if config has email address
CONFIG_FILE="$(dirname "$0")/config/config.yaml"
if grep -q 'address: ""' "$CONFIG_FILE"; then
    echo "Step 1: Configure your email address"
    echo "Edit config/config.yaml and set your email address"
    echo ""
fi

# Store email password
echo "Step 2: Store email password in Keychain"
echo "Enter your email address:"
read -r EMAIL_ADDRESS
echo "Enter your email password (will be stored securely):"
read -rs PASSWORD
echo ""

security add-generic-password -s "email-to-kg" -a "$EMAIL_ADDRESS" -w "$PASSWORD" -U 2>/dev/null || \
security add-generic-password -s "email-to-kg" -a "$EMAIL_ADDRESS" -w "$PASSWORD"
echo "Email password stored"

# Store Anthropic API key
echo ""
echo "Step 3: Store Anthropic API key in Keychain"
echo "Enter your Anthropic API key:"
read -rs API_KEY
echo ""

security add-generic-password -s "anthropic" -a "api_key" -w "$API_KEY" -U 2>/dev/null || \
security add-generic-password -s "anthropic" -a "api_key" -w "$API_KEY"
echo "Anthropic API key stored"

# Update config with email address
if grep -q 'address: ""' "$CONFIG_FILE"; then
    sed -i '' "s/address: \"\"/address: \"$EMAIL_ADDRESS\"/" "$CONFIG_FILE"
    echo "Updated config with email address"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Test your setup with:"
echo "  python3 ~/email-to-kg/main.py status"
echo ""
echo "Run your first sync with:"
echo "  python3 ~/email-to-kg/main.py sync"
