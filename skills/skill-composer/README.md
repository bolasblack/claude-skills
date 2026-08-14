# Skill Composer

Primary policy for creating, updating, reviewing, and packaging agent skills. Based on the current [Agent Skills specification](https://agentskills.io/specification), target-platform documentation, and community patterns.

## Features

- Three-level progressive disclosure model (frontmatter > body > linked files)
- Exceptional `SPEC.md` convention for stable maintainer-only requirements, with Skill Composer itself as a qualifying case
- Explicit authority over harness-injected authoring helpers such as `skill-creator`
- Portable-core plus harness-enhancement architecture for cross-agent skills
- Planning-first creation workflow and a separate, default-read-only full-package review workflow
- Optional composition with Matt Pocock's [writing-for-agents](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents)
- Five workflow patterns (sequential, multi-MCP, iterative, context-aware, domain-specific)
- Model-, user-, and dual-invocation guidance with branch-specific context pointers
- Portable frontmatter and target-specific tool pre-approval guidance
- Evidence-first evaluations covering triggering, function, isolation, and coexistence
- MCP + Skills integration guidance
- Target-qualified distribution via repositories, claude.ai, Claude Code, Skills API, and Agent SDK
- Portable, evidence-backed skill-local changelogs with optional causal examples for independently distributed releases
- Seven annotated historical pattern snapshots from official and community repositories

## Files

- `SKILL.md` - Main skill definition, creation and review workflows, and quick checklist
- `SPEC.md` - Skill Composer's rare maintainer-only contract; generated skills omit it unless they pass the admission test
- `REFERENCE.md` - Technical specs, full review ledger, workflow patterns, testing, troubleshooting, and target-specific distribution
- `CHANGELOG.md` - Portable release history for Skill Composer
- `examples/` - 7 real-world skill patterns:
  - `tdd.md` - Test-Driven Development (discipline enforcement)
  - `systematic-debugging.md` - Four-phase debugging methodology
  - `webapp-testing.md` - Concise helper scripts pattern
  - `mcp-builder.md` - Comprehensive framework pattern
  - `xlsx.md` - Production standards pattern
  - `docx.md` - Decision tree pattern
  - `git-worktrees.md` - Safety workflow pattern

## Acknowledgments

Originally from [caoer](https://github.com/caoer). v3.0.0 was rewritten using Anthropic's official guide; current releases track the open specification and current target documentation.
