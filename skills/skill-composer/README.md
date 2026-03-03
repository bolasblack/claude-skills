# Skill Composer

Create and improve Claude Code Skills following official best practices. Based on Anthropic's [Complete Guide to Building Skills for Claude](https://resources.anthropic.com/hubfs/The-Complete-Guide-to-Building-Skill-for-Claude.pdf) merged with community patterns.

## Features

- Three-level progressive disclosure model (frontmatter > body > linked files)
- Planning-first workflow: use cases, success criteria, then build
- Five workflow patterns (sequential, multi-MCP, iterative, context-aware, domain-specific)
- Discovery-optimized description patterns with negative triggers
- Tool restriction guidance with scoped bash syntax
- YAML frontmatter spec with new fields (license, compatibility, metadata)
- Testing methodology (triggering, functional, performance comparison)
- MCP + Skills integration guidance
- Distribution via GitHub, org deployment, and API
- Seven real-world example patterns from official and community repositories

## Files

- `SKILL.md` - Main skill definition, creation workflow, and quick checklist
- `REFERENCE.md` - Technical specs, workflow patterns, testing, troubleshooting, distribution
- `examples/` - 7 real-world skill patterns:
  - `tdd.md` - Test-Driven Development (discipline enforcement)
  - `systematic-debugging.md` - Four-phase debugging methodology
  - `webapp-testing.md` - Concise helper scripts pattern
  - `mcp-builder.md` - Comprehensive framework pattern
  - `xlsx.md` - Production standards pattern
  - `docx.md` - Decision tree pattern
  - `git-worktrees.md` - Safety workflow pattern

## Acknowledgments

Originally from [caoer](https://github.com/caoer). v3.0.0 rewritten using Anthropic's official guide.
