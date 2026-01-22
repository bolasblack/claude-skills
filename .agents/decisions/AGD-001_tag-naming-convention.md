---
title: "Tag Naming Convention"
description: "Tags follow the pattern {type}/{name} based on project structure"
tags: global
---

## Context

This project contains three types of extensions: skills, agents, and commands. Each extension is stored in its corresponding directory (`skills/`, `agents/`, `commands/`). We need a consistent way to tag AGD files to indicate which extensions they relate to.

## Decision

Tags follow the pattern `{type}/{name}` where:
- `{type}` is one of: `skills`, `agents`, `commands`
- `{name}` is the directory name of the extension

Examples:
- `skills/agent-centric`
- `agents/code-reviewer`
- `commands/some-command`

Tags are automatically derived from the project structure. Extensions that are gitignored should not be included as tags.

## Consequences

- Tags directly map to the project's directory structure, making it easy to understand which extensions an AGD relates to
- New extensions automatically suggest new tags
- Consistent naming makes searching by tag intuitive
