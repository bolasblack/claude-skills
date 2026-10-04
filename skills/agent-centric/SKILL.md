---
name: agent-centric
description: "Track decisions (AGD) with validation and indexing. Use when making design decisions, recording important choices, discussing trade-offs, or when user mentions AGD or decision record."
hooks:
  PostToolUse:
    - matcher: "Bash|Write|Edit"
      hooks:
        - type: command
          command: 'if [ -n "$CLAUDE_PROJECT_DIR" ] && python3 "$CLAUDE_PROJECT_DIR/.agents/scripts/check-setup.py" "$CLAUDE_PROJECT_DIR" >/dev/null 2>&1; then CLAUDE_PROJECT_DIR="$CLAUDE_PROJECT_DIR" "$CLAUDE_PROJECT_DIR/.agents/scripts/validate-agds.py"; fi'
        - type: command
          command: 'if [ -n "$CLAUDE_PROJECT_DIR" ] && python3 "$CLAUDE_PROJECT_DIR/.agents/scripts/check-setup.py" "$CLAUDE_PROJECT_DIR" >/dev/null 2>&1; then CLAUDE_PROJECT_DIR="$CLAUDE_PROJECT_DIR" "$CLAUDE_PROJECT_DIR/.agents/scripts/generate-index.py"; fi'
---

# Agent Centric

Framework for agent-centric development. Currently provides AGD (Agent-centric Governance Decision) tracking.

## Required Setup Check

Before using this skill in a project, run the bundled read-only check. Resolve
`CLAUDE_SKILL_DIR` to the directory containing this `SKILL.md` and
`CLAUDE_PROJECT_DIR` to the target project root; supply these paths explicitly when
the host does not provide them.

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/check-setup.py" "${CLAUDE_PROJECT_DIR}"
```

Continue only when the command exits `0`. The check requires AGD configuration,
the decisions directory, and runtime scripts; an existing `.agents/` directory
alone is insufficient.

If the check fails or cannot run, **stop using this skill**. Briefly report the
missing setup and continue the user's task without AGD operations. Do not
initialize, sync, repair configuration, or create decisions/indexes to bypass the
check. Setup is a separate action: only follow [Setup](README.md#setup) when the
user explicitly requests it, then rerun this check.

After a successful check, sync the initialized project's managed files:

```bash
CLAUDE_PROJECT_DIR="${CLAUDE_PROJECT_DIR}" CLAUDE_SKILL_DIR="${CLAUDE_SKILL_DIR}" bash "${CLAUDE_SKILL_DIR}/scripts/sync-scripts.sh"
```

The sync respects `disableAutoUpdateScripts`. If files were updated, briefly inform
the user. Rerun the setup check on each skill load and whenever the target project
changes.

## What is AGD?

AGD (Agent-centric Governance Decision) is a decision record mechanism, similar to ADR or RFC. Each AGD has a unique number (e.g., AGD-001) that records important decisions, rationale, and impact.

AGD covers **any important decision**, not just architecture - including design patterns, conventions, tool choices, process decisions, etc.

AGD follows the RFC archival model: original files are preserved, and later decisions express how earlier ones evolve.

- **updates**: extends or modifies an earlier decision; the earlier decision remains partially valid
- **obsoletes**: completely replaces an earlier decision; the earlier decision is no longer current
- **related**: reference-only connection, similar to RFC `see-also`; does not change validity of either decision

AGD exists to give the project stable references for important decisions and durable rationale that survives code evolution. It should let us trace from today's implementation back to why it was chosen, and then judge whether that decision still stands, has been updated, or has been replaced.

## When to Use

- Making important design/architecture decisions
- User explicitly asks to record a decision
- Discussing trade-offs that should be documented
- Referencing or searching existing decisions

## Automatic Behaviors

In Claude Code, the bundled PostToolUse hooks check setup before running AGD
validation and index generation after Write/Edit/Bash calls:

- **Validates** all AGD files (tags, references)
- **Regenerates** indexes automatically (silent on success)

If validation fails, you'll see errors and should fix them (e.g., add missing tags to config.json).

If hooks are unavailable, or script auto-update is disabled and the project lacks
the hook's `check-setup.py` copy, run validation after AGD changes yourself, after
the required setup check passes:

```bash
python3 "${CLAUDE_PROJECT_DIR}/.agents/scripts/validate-agds.py" "${CLAUDE_PROJECT_DIR}" </dev/null
```

Successful validation also regenerates indexes.

## Creating AGD Files

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
related: AGD-003
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

## Release history

See [CHANGELOG.md](CHANGELOG.md) for version history. `VERSION` is the machine-readable version owner.
