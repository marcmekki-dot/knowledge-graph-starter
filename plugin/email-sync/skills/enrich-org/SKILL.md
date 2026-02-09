---
name: enrich-org
description: Enrich an organization's profile from email history. Use when user asks about a company, organization, or client like "tell me about KPMG", "what's my history with PwC", "enrich org profile for", "who do I know at [company]", or wants context about an organization.
tools: Bash, AskUserQuestion, Edit, Read
---

# Organization Profile Enrichment

Extract rich context about an organization from your email history.

## Command

```bash
mail-context enrich-org "DOMAIN" --save
```

Replace DOMAIN with the organization's email domain (e.g., company.com).

**Note:** This command requires mail-context to be installed. If not available, inform the user they need to install it (see README).

## What It Extracts

- **Organization Name** - Full company name
- **Industry** - Sector/industry type
- **Key Contacts** - People you've emailed at this org with their roles
- **Projects Together** - Engagements and deliverables
- **Key Interactions** - Important meetings, decisions, milestones
- **Commercial Notes** - Pricing, invoicing, contract details
- **Relationship Notes** - How the relationship started, nature of partnership

## Examples

```bash
# Enrich a client organization
mail-context enrich-org "client.com" --save

# Enrich a partner organization
mail-context enrich-org "partner.com" --save

# Preview without saving
mail-context enrich-org "company.com"
```

## Batch Enrichment

To enrich multiple organizations at once:

```bash
# Preview organizations from email history
mail-context enrich-orgs --dry-run --min-emails 20

# Enrich specific organizations
mail-context enrich-orgs -i client.com -i partner.com --yes

# Enrich top 10 organizations by email volume
mail-context enrich-orgs --limit 10 --yes
```

## Your Role

After running enrichment:
1. Summarize the organization and your relationship with them
2. Highlight key contacts and their roles
3. Mention notable projects or engagements
4. Note any commercial/business context
5. Note the file was saved to ~/personal/organizations/

## Output Location

Profiles are saved to: `~/personal/organizations/{org-name}.md`
