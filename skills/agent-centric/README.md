# Agent Centric

Framework for agent-centric development with AGD (Agent-centric Governance Decision) tracking.

## What is AGD?

AGD (Agent-centric Governance Decision) is a decision record mechanism, similar to ADR or RFC. Each AGD has a unique number (e.g., AGD-001) that records important decisions, rationale, and impact.

Unlike traditional ADRs that focus solely on architecture, AGD covers **any important decision**:

- Design patterns and conventions
- Tool and library choices
- Process decisions
- API contracts
- Team agreements

AGD follows the RFC archival model: original files are preserved, and later decisions express how earlier ones evolve.

- **updates**: extends or modifies an earlier decision; the earlier decision remains partially valid
- **obsoletes**: completely replaces an earlier decision; the earlier decision is no longer current
- **related**: reference-only connection, similar to RFC `see-also`; does not change validity of either decision

AGD exists to build a persistent, growing history of project decisions with stable references. Decision records do not disappear when code changes; they preserve why an implementation, convention, or process was chosen, make that rationale easy to recover later, and help determine whether a decision still stands, has been updated, or has been replaced.

People may describe this as a "decision history tree", but structurally it is closer to a decision history graph because AGDs can point to multiple related decisions.

## Installation

Paste this into Claude Code, Codex, OpenCode, or any compatible AI coding agent:

> Read https://raw.githubusercontent.com/bolasblack/claude-skills/master/llms.install.md and follow the instructions to install the `agent-centric` skill.

## Quick Start

1. **Initialize** - The skill auto-initializes on first load, creating:
   - `.agents/decisions/` - Decision storage
   - `.agents/scripts/` - Skill scripts
   - `.agents/config.json` - Configuration file

2. **Define tags** - Add allowed tags to `.agents/config.json`:

   ```json
   {
     "tags": ["core", "auth", "api", "database"]
   }
   ```

3. **Create a decision** - Ask Agent or manually create AGD files:

   ```
   .agents/decisions/AGD-001_use-postgresql.md
   ```

4. **Automatic validation** - PostToolUse hooks validate files and regenerate indexes after AGD changes

5. **Relationship indexing** - `INDEX-AGD-RELATIONS.md` records:
   - `-(u)->` for updates
   - `-(o)->` for obsoletes
   - `-(r)->` for related/reference-only links

## Script Auto-Update

Scripts in `.agents/scripts/` are automatically synced from the skill directory on each load.

To disable auto-update for specific scripts:

```json
{
  "disableAutoUpdateScripts": ["validate-agds.py"]
}
```

To disable all script updates:

```json
{
  "disableAutoUpdateScripts": true
}
```

## Works Well With

The [guardrails](../guardrails/) skill is the natural companion: an AGD records *why* a decision was made, and when a decision produces a hard rule the repository must enforce, that rule becomes a guardrail (GRL) whose `references` field points back at the AGD. AGD keeps the decision history; guardrails keep the enforceable rules. Both frameworks live side by side under `.agents/`.

## Acknowledgments

Inspired by [caoer](https://github.com/caoer).
