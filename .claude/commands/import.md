---
description: Import a Claude Code skill, command, or agent and run security audits
argument-hint: <type> <source>
---

Import and audit a Claude Code extension from the provided source: $ARGUMENTS

**Arguments:**

- `type`: One of `skill`, `command`, or `agent`
- `source`: GitHub URL or other source

**Examples:**

- `/import-skill skill https://github.com/user/repo/tree/main/my-skill`
- `/import-skill agent https://github.com/user/repo/tree/main/code-reviewer`
- `/import-skill command https://github.com/user/repo/tree/main/my-command`

> **IMPORTANT**: Before proceeding, read the official Claude Code documentation:
>
> - Skills: https://code.claude.com/docs/en/skills
> - Commands: https://code.claude.com/docs/en/slash-commands
> - Agents: https://code.claude.com/docs/en/sub-agents

## Your Task

### 1. Parse Arguments

Parse `$ARGUMENTS` to extract:

- `type`: skill, command, or agent
- `source`: GitHub URL or other source

If arguments are missing or invalid, ask user to provide them.

### 2. Fetch Content (for GitHub URLs)

- Parse URL to extract: owner, repo, branch, path
- Convert `/tree/` URLs to API format: `https://api.github.com/repos/{owner}/{repo}/contents/{path}?ref={branch}`
- Fetch file list, then fetch each file via raw URL: `https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{path}`

### 3. Save to Local Directory

Follow the guidelines in `<project-root>/CONTRIBUTING.md`

| Type    | Directory          | Main File  |
| ------- | ------------------ | ---------- |
| skill   | `skills/<name>/`   | SKILL.md   |
| command | `commands/<name>/` | COMMAND.md |
| agent   | `agents/<name>/`   | AGENT.md   |

- Extract name from YAML frontmatter `name` field or directory name
- Write main file and other files

### 4. Run Security Audits (launch agents in parallel using Task tool)

- **Agent 1 - review files**

      - for skills: use `skill-reviewer` skill
      - for commands: use `command-creator` skill

- **Agent 2 - security-auditor**: Analyze for information security risks, code/configuration security, third-party risks, data privacy. Report by severity.

- **Agent 3 - prompt-injection-auditor**: Check for prompt injection patterns, invisible characters, encoding attacks, instruction hijacking, context manipulation. Report by severity.

- **Agent 4 - code-reviewer** (if contains code): Analyze for code quality, performance, accessibility, maintainability, and best practices. Report by severity.

### 5. Update Documentation

- **README.md**: Create `<type>s/<name>/README.md` with:
  - Brief description
  - Acknowledgments section (if source URL is available, credit the original repository with a link)
  - Other sections as appropriate

### 6. Report Results

- Extension location (file paths created)
- Audit summary from all agents
- Any warnings or recommendations
