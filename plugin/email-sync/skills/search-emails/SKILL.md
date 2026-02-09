---
name: search-emails
description: Search emails using natural language queries. Use when user asks to "find emails", "search for emails", "what did X say about Y", "show me emails about Z", or any email search/query request.
tools: Bash
---

# Email Search

Search your email archive with natural language and get intelligent, contextual answers.

## Command

If mail-context is installed:
```bash
mail-context assemble "USER_QUERY_HERE" --window 30d
```

Otherwise, use the built-in search:
```bash
python3 ~/email-to-kg/main.py search "USER_QUERY_HERE"
```

Replace USER_QUERY_HERE with the user's search request.

## Query Syntax

The tool supports natural language and structured queries:

- **Keywords**: `budget proposal meeting`
- **From sender**: `from:fred` or `from:john@example.com`
- **Subject line**: `subject:booking`
- **Combined**: `from:sarah hotel booking`

## Time Windows

Adjust `--window` based on the query:
- Recent/urgent queries: `--window 7d`
- General searches: `--window 30d`
- Historical searches: `--window 90d` or `--window 365d`

## Output Format

Returns markdown with:
- Thread subject and message count
- Each email with sender, date, and body
- Full thread context for understanding conversations

## Your Role

After running the search, provide an **intelligent response**:

1. **Answer the question directly**: If user asked "what did John say about X", summarize what John said
2. **Synthesize content**: Don't just list emails - extract key information, dates, action items
3. **Group related threads**: Treat email threads as conversations
4. **Highlight important details**: Deadlines, decisions, requests, amounts
5. **Be conversational**: Respond naturally as an assistant would

### Response Examples

**User**: "What did Sarah say about the budget?"

**Bad**: "Found 3 emails from Sarah mentioning budget. Here are the subjects..."

**Good**: "Sarah sent three emails about the budget this week. Key points: Q2 budget is approved at $50k, she needs your sign-off by Friday, and she's concerned about the marketing line item being over by 15%."

## Tips

- For vague queries, start with a broader window and narrow down
- If no results, try alternative keywords or check spelling of names
- Use `from:` filter when looking for specific person's messages
- For older emails, use `--window 90d` or longer
