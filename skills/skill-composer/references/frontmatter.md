# Skill Frontmatter

## YAML Frontmatter Specification

### Required Fields

```yaml
---
name: "skill-name"
description: "What it does and when to use it"
---
```

| Field | Type | Constraints |
|-------|------|-------------|
| `name` | string | 1-64 lowercase letters, digits, or hyphens; no leading, trailing, or consecutive hyphens; must match the parent directory. |
| `description` | string | 1-1024 chars; describes what the skill does and when to use it. |

### Optional Fields

```yaml
---
name: "skill-name"
description: "Description here"
allowed-tools: Read Grep Glob
license: MIT
compatibility: "Requires Git and a POSIX shell"
metadata:
  author: "Company Name"
  version: "1.0.0"
  mcp-server: server-name
  category: productivity
  tags: "project-management,automation"
  documentation: https://example.com/docs
  support: support@example.com
---
```

| Field | Type | Purpose |
|-------|------|---------|
| `allowed-tools` | string | Experimental, space-separated tool pre-approval; support varies by host |
| `license` | string | License name or bundled license file reference |
| `compatibility` | string | Environment requirements, 1-500 chars |
| `metadata` | object | Optional string-to-string extension map (author, version, mcp-server, etc.) |

### Target-Specific Validation

The portable specification and target harnesses may enforce different schemas. For a
named surface, use [Harness Research](../HARNESS-RESEARCH.md) to establish its current
required and optional fields, restrictions, validation path, and treatment of portable
packages. Run both the portable validator and the named target's validator, and keep
verified target-only fields in an explicit harness enhancement.

## Tool Pre-Approval

In the portable specification, `allowed-tools` is experimental and contains a space-separated set of pre-approved tools. Support and syntax vary between agent implementations.

Before using it, research the named surface's current support, syntax, invocation scope,
and distinction between pre-approval and restriction. Omitting `allowed-tools` does not
define a portable permission policy; use the verified host permission mechanism when
actual restriction is required.
