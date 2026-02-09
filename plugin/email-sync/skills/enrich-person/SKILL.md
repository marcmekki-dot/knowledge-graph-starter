---
name: enrich-person
description: Enrich a person's profile from email history. Use when user asks to "tell me about [person]", "what do I know about [name]", "enrich profile for", "who is [name] in my emails", or wants context about a contact.
tools: Bash, AskUserQuestion, Edit, Read
---

# Person Profile Enrichment

Extract rich context about a contact from your email history.

## Command

```bash
mail-context enrich-person "EMAIL_OR_NAME" --save
```

Replace EMAIL_OR_NAME with the person's email or name.

**Note:** This command requires mail-context to be installed. If not available, inform the user they need to install it (see README).

## What It Extracts

- **Role & Company** - Their position and organization
- **Topics/Expertise** - What they email about
- **Projects Together** - Engagements you've collaborated on
- **Key Interactions** - Important decisions, agreements, dates
- **Relationship Notes** - How you know them, their role in your network

## Examples

```bash
# By email
mail-context enrich-person "john.smith@company.com" --save

# By name (will search and prompt if multiple matches)
mail-context enrich-person "John" --save

# Preview without saving
mail-context enrich-person "john@company.com"
```

## Batch Enrichment

To enrich multiple contacts at once:

```bash
# Preview contacts from specific domains
mail-context enrich-people --dry-run -i company.com -i client.com

# Enrich top 20 contacts from those domains
mail-context enrich-people --limit 20 --yes -i company.com -i client.com
```

## Your Role

After running enrichment:
1. Summarize the key information about the person
2. Highlight their role and how they relate to the user
3. Mention notable projects or interactions
4. Note the file was saved to ~/personal/people/

## Output Location

Profiles are saved to: `~/personal/people/{name}.md`
