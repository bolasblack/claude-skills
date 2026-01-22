---
name: agent-centric
description: "Track decisions (AGD) with validation and indexing. Use when making design decisions, recording important choices, discussing trade-offs, or when user mentions AGD or decision record."
hooks:
  PreToolUse:
    - matcher: "Write"
      hooks:
        - type: command
          command: 'CLAUDE_PROJECT_DIR="$CLAUDE_PROJECT_DIR" "$CLAUDE_PROJECT_DIR/.agents/scripts/pre-validate-agd.py"'
  PostToolUse:
    - matcher: "Bash|Write|Edit"
      hooks:
        - type: command
          command: 'CLAUDE_PROJECT_DIR="$CLAUDE_PROJECT_DIR" "$CLAUDE_PROJECT_DIR/.agents/scripts/validate-agds.py"'
        - type: command
          command: 'CLAUDE_PROJECT_DIR="$CLAUDE_PROJECT_DIR" "$CLAUDE_PROJECT_DIR/.agents/scripts/generate-index.py"'
---

# Agent Centric

Framework for agent-centric development. Currently provides AGD (Agent-centric Governance Decision) tracking.

## What is AGD?

AGD (Agent-centric Governance Decision) is a decision record mechanism, similar to ADR or RFC. Each AGD has a unique number (e.g., AGD-001) that records important decisions, rationale, and impact.

AGD covers **any important decision**, not just architecture - including design patterns, conventions, tool choices, process decisions, etc.

Decisions can be **updated** (extended) or **obsoleted** (replaced) by later decisions, but original files are preserved, forming a complete decision history for future reference.

## When to Use

- Making important design/architecture decisions
- User explicitly asks to record a decision
- Discussing trade-offs that should be documented
- Referencing or searching existing decisions

## Setup

On each skill load, sync scripts and initialize if needed:

```bash
if [ ! -d "$CLAUDE_PROJECT_DIR/.agents" ]; then
  CLAUDE_PROJECT_DIR="$CLAUDE_PROJECT_DIR" CLAUDE_SKILL_DIR="$CLAUDE_SKILL_DIR" bash "$CLAUDE_SKILL_DIR/scripts/init.sh"
else
  CLAUDE_PROJECT_DIR="$CLAUDE_PROJECT_DIR" CLAUDE_SKILL_DIR="$CLAUDE_SKILL_DIR" bash "$CLAUDE_SKILL_DIR/scripts/sync-scripts.sh"
fi
```

If scripts were updated, briefly inform the user.

## Automatic Behaviors

Hooks run automatically when you use Write/Edit/Bash tools:

1. **PreToolUse:Write** - Validates tags BEFORE creating AGD
   - If tags are invalid, creation is **BLOCKED**
   - You'll see: `❌ BLOCKED: Invalid tags: ...`

2. **PostToolUse** - After any file operation on AGD files:
   - Validates all AGD files (errors shown if any)
   - Regenerates indexes automatically (silent on success)

## Creating AGD Files

**CRITICAL: Always use the Write tool** to create AGD files. This ensures PreToolUse validation runs before creation, blocking invalid AGD files.

### File Naming

```
AGD-{number}_{kebab-case-name}.md
```

Examples: `AGD-001_use-postgresql.md`, `AGD-002_adopt-hexagonal-architecture.md`

### File Format

```yaml
---
title: "Decision Title"
description: "Brief description"
tags: tag1, tag2
updates: AGD-001
obsoletes: AGD-002
---

## Context
Why this decision is needed.

## Decision
What was decided.

## Consequences
Impact of this decision.
```

See [references/agd.md](references/agd.md) for complete field documentation.

## Searching Decisions

**IMPORTANT**: Always use `grep` and `find` to search. Do NOT read files to search.

```bash
# By keyword
grep -r "keyword" "$CLAUDE_PROJECT_DIR/.agents/decisions/"

# By AGD number
find "$CLAUDE_PROJECT_DIR/.agents/decisions/" -name "AGD-001*"

# By tag
grep "#tagname" "$CLAUDE_PROJECT_DIR/.agents/INDEX-TAGS.md"

# By relationship
grep "AGD-001" "$CLAUDE_PROJECT_DIR/.agents/INDEX-AGD-RELATIONS.md"
```

## Managing Tags

Add tags to `.agents/config.json` before using them:

```json
{
  "tags": ["core", "auth", "api"]
}
```

See [references/config.md](references/config.md) for config details.

## Version History

- v1.4.0 (2026-01-22): Add PreToolUse hook to block invalid AGD creation, auto-detect project dir
- v1.3.0 (2025-01-22): Split references/, renamed validate-agds.py
- v1.2.0 (2025-01-22): Split to SKILL.md + REFERENCE.md
- v1.1.0 (2025-01-21): Merged index files, hooks in frontmatter, auto-init
- v1.0.0 (2025-01-21): Initial version
