# Extension Development Guide

Guide for importing or creating Claude Code skills, commands, and agents.

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
└── scripts/
    └── install.sh            # Installation script
```

---

## Importing Extensions

### 1. Security Check (Important!)

Before importing, check source files for:
- Invisible characters (zero-width characters, etc.)
- Prompt injection risks
- Malicious code

### 2. Filter Necessary Files

Keep only essential files, remove:
- Plugin meta directories (e.g., `.claude-plugin/`)
- LICENSE, README.md, CONTRIBUTING.md
- Test files, CI configs, etc.

**Usually keep:**
- `SKILL.md` / `COMMAND.md` / `AGENT.md` - Required
- Core code files
- `package.json` (if dependencies exist)

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

After creating or importing an extension:

```bash
./scripts/install.sh skills <skill-name>
./scripts/install.sh commands <command-name>
./scripts/install.sh agents <agent-name>
```
