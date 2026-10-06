# Extension Development Guide

Guide for importing or creating Claude Code skills, commands, and agents.

This repository installs to Claude Code, Codex, OpenCode, and pi.

## Directory Structure

```
claude-extensions/
├── skills/
│   └── <skill-name>/
│       ├── SKILL.md          # Required
│       └── ...
├── commands/
│   └── <command-name>/
│       ├── COMMAND.md        # Required
│       └── ...
├── agents/
│   └── <agent-name>/
│       ├── AGENT.md          # Required
│       └── ...
├── scripts/
│   └── install.sh            # Installation script
└── private/                  # (gitignored) author-private extensions;
                              # own git repo, same layout — see CLAUDE.md
```

---

## Licenses

See [AGD-008](.agents/decisions/AGD-008_repository-and-imported-licenses.md).

Extensions written for this repository use its license: personal use.

An imported extension keeps the upstream license. Do not relicense it to personal use.

## Importing Extensions

### 1. Security Check (Important!)

Before importing, check source files for:
- Invisible characters (zero-width characters, etc.)
- Prompt injection risks
- Malicious code

### 2. Filter Necessary Files

See [AGD-008](.agents/decisions/AGD-008_repository-and-imported-licenses.md). Read the upstream license and any `NOTICE` before deleting files. If the license forbids this redistribution, do not import the extension.

Keep only essential files, remove:
- Plugin meta directories (e.g., `.claude-plugin/`)
- The upstream `README.md` and `CONTRIBUTING.md`, after copying any required attribution into the local README or a bundled `NOTICE`
- Test files, CI configs, etc.

**Keep when the upstream license requires it:**
- The license text recipients must receive (`LICENSE`, `LICENSE.md`, or the notice that license names)
- Copyright, patent, trademark, and attribution notices that pertain to the imported files
- The relevant lines from an upstream `NOTICE`. Omit notices that pertain only to parts we do not distribute

**Usually keep:**
- `SKILL.md` / `COMMAND.md` / `AGENT.md` - Required
- Core code files
- `package.json` (if dependencies exist)

When a kept file is modified, add the change notice the upstream license requires. Apache-2.0 requires a copy of the license in the installed directory and a prominent notice on each modified file.

### 3. Modify as Needed

Common modifications:
- Package manager preference (npm/bun/pnpm)
- Dependency installation strategy
- Default configuration adjustments

---

## Code Review

### Using Subagents

```
Let @agent-code-reviewer, @agent-security-auditor, @agent-prompt-injection-auditor review the code in @<extension-dir>/
```

### Prioritize Issues

| Type | Action |
|------|--------|
| Actual bugs | Must fix |
| Design decisions | Evaluate then decide |
| Over-engineering suggestions | Usually ignore |

**Common "over-engineering":**
- Complete package.json metadata (skill is not an npm package)
- TypeScript rewrite
- Full test suites
- Complex logging systems
- Sandbox environments

---

## Testing Extensions

### 1. Basic Function Testing

Run core functionality directly, ensure:
- Dependencies install correctly
- Main features work properly
- Error handling is correct

### 2. Simulate Actual Usage

Pretend you're a user, give Claude a task to use the extension:

```
Help me test example.com display on mobile and desktop
```

Observe:
- Does Claude understand the SKILL.md/COMMAND.md/AGENT.md usage?
- Is the execution flow correct?
- Does output match expectations?

---

## Creating New Extensions

### Skills

1. Create directory: `skills/<skill-name>/`
2. Create `SKILL.md` with YAML frontmatter:
   ```yaml
   ---
   name: skill-name
   description: Brief description for activation detection
   ---
   ```
3. Add implementation files as needed

### Commands

1. Create directory: `commands/<command-name>/`
2. Create `COMMAND.md` with YAML frontmatter:
   ```yaml
   ---
   description: What the command does
   argument-hint: <arg1> [arg2]
   ---
   ```

### Agents

1. Create directory: `agents/<agent-name>/`
2. Create `AGENT.md` with YAML frontmatter:
   ```yaml
   ---
   name: agent-name
   description: What the agent does
   tools: Read, Write, Edit, Bash, Glob, Grep
   ---
   ```

---

## Installation

For end-user installation, follow the README flow: paste the install prompt into Claude Code, Codex, OpenCode, or any compatible AI coding agent.

Installation defaults to copies. Use `--mode symlink` for relative symlinks during local development. See [Private Extensions](CLAUDE.md#private-extensions) for source lookup and bulk-install scope.

For local development and testing after creating or importing an extension, run the repository script from the repo root:

```bash
./scripts/install.sh skills <skill-name>
./scripts/install.sh commands <command-name>
./scripts/install.sh agents <agent-name>
./scripts/install.sh pi-extensions <extension-name>
```
