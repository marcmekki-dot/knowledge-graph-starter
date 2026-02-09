# Claude Self-Improving System

## Auto-Logging Rules (DO NOT ASK BEFORE LOGGING)
- When user mentions a task → Add to appropriate file's TODO section
- When user completes something → Mark done, move to daily log
- When user shares notes/context → Add to daily log under today
- Capture EVERYTHING in text — never write "see app" or "see link"

## Content Routing

### Task & Activity Tracking
- Work tasks → personal/work.md
- Household, family, errands → personal/home.md
- Fitness, health, personal goals → personal/personal.md
- Notes about people → personal/people/{name}.md
- Project-specific items → personal/projects/{project-name}.md
- Session activity → personal/logs/YYYY-MM-DD.md

### Knowledge Management
- User's own frameworks, processes, approaches → personal/knowledge/my-methods/{topic}.md
- Third-party tools, concepts, research → personal/knowledge/references/{topic}.md
- Update knowledge/index.md when adding new entries

### Knowledge Capture Triggers
- "Here's how I do X" / "My approach to X" → my-methods/
- "I learned that..." / "This tool does..." → references/
- Workshop methodologies, facilitation techniques → my-methods/
- AI tools, platforms, capabilities → references/
- When capturing knowledge, extract the transferable principle, not just the instance

## Priority Markers
- [P1] Urgent - needs attention today
- [P2] Important - this week
- [P3] Normal - when time permits

## Tags
- @person:Name - involves a specific person
- @deadline:Date - has a deadline
- @waiting - waiting on someone else
- @followup - needs follow-up

## Startup Protocol
1. Read this file
2. Check today's log in personal/logs/
3. Review TODOs in work.md, personal.md, home.md
4. Scan knowledge/index.md for context on current projects
5. Surface urgent [P1] items and upcoming deadlines
6. Ask user focus priorities

## Weekly Review (Friday Afternoon)
On Fridays, prompt user to:
- Review completed items from the week
- Assess remaining TODOs and reprioritize
- Archive done items older than 2 weeks
- Identify blockers and next actions

## Knowledge Graph Maintenance
- After completing a project or workshop → extract methods worth preserving
- When a reference is cited 3+ times → promote to dedicated entry
- Cross-link related methods and references using [[filename]] notation
- Periodically review knowledge/index.md to identify gaps

## Knowledge Graph Enrichment (Daily/Session Start)
On each new session or daily, scan for gaps and surface opportunities to enrich:

### Gap Detection
- People with < 5 lines of content → suggest LinkedIn/email enrichment
- Organizations with < 10 lines → suggest enrichment from emails or web
- Projects without linked people or orgs → suggest adding connections
- Recent email contacts not yet in people/ → suggest creating profiles

### Enrichment Sources
1. **Email history** → `mail-context enrich-person` or `mail-context enrich-org`
2. **LinkedIn** → Use browser automation to pull profile data
3. **User conversation** → Capture details shared verbally

### Surfacing Protocol
- At session start, after startup protocol, run quick scan
- Report: "Found X profiles that could be enriched: [names]"
- Offer to enrich 1-2 during the session if time permits
- Prioritize by: recent email activity > mutual project involvement > staleness
