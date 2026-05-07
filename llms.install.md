# Installation Guide for AI Agents

You are helping a user install extensions from the claude-skills collection.
Follow this workflow step by step.

## Step 1: Gather context, present options, and confirm install target

Do these three things together, before asking the user anything:

1. **Check for existing repository clone**: `test -d ~/.c4-skills/.git`
2. **Analyze the current working directory**: Is this a project directory (has `package.json`, `Cargo.toml`, `go.mod`, `.git`, `pyproject.toml`, `Makefile`, etc.)? If so, scan briefly: languages, frameworks, existing tooling, test setup, CI config. Note the project root path.
3. **Read the README**: Fetch `https://raw.githubusercontent.com/bolasblack/claude-skills/master/README.md` to get the full list of available skills, agents, commands, and pi-extensions with their descriptions.

Then present your findings and ask the user **three things at once**:

### What to install

If the user specified a type in their original message (e.g. "install skills"), only list that type.

**If in a project directory** — recommend the most relevant extensions based on your project analysis, with a brief reason for each:

> I've analyzed your project (TypeScript + React, uses Playwright). Here are my recommendations:
>
> **Skills:**
> A) playwright — You already use Playwright; this automates browser testing with AI
> B) frontend-design — React project, helps create production-grade UI
> C) skill-composer — Useful if you want to create custom skills for this project
>
> **Agents:**
> D) code-reviewer — Principled code reviewer in Uncle Bob's tradition

**If in a home directory or non-project directory** — show at least 10 generally useful extensions across all types with brief descriptions.

### Where to install

**If in a project directory**, also ask:

> Install to:
> 1. Home directory (available in all projects)
> 2. This project only (`<project_dir>`)

**If in a home directory**, skip this question — install to home directory.

### Which tools to install for

Ask which target tools should receive the extensions:

> Install for which tools?
> - **Auto-detect** existing tool directories (default)
> - `agents` — generic `.agents/skills` project-compatible skills directory
> - `claude` — Claude Code
> - `codex` — Codex skills
> - `opencode` — OpenCode
> - `pi` — pi skills, agents, and extensions

If installing to a project directory, recommend explicit tools instead of auto-detect so the installer can create the intended project-local directories. Good defaults:
- Skills for broad project sharing: `agents,claude,pi`
- Claude Code only: `claude`
- Pi extensions: `pi`

### How to respond

Tell the user:

> Pick extensions by letter or name (e.g. "A, C, D" or "playwright, code-reviewer").
> Pick tools by name or say "auto" (e.g. "install A and D to this project for agents,claude").
> Say **"show all"** to see the complete list, or **"all"** / **"__all"** to install everything.

Wait for the user's response before proceeding.

## Step 2: Set up local repository

If `~/.c4-skills` exists, update it:

```bash
cd ~/.c4-skills && git pull
```

Set `REPO_DIR=~/.c4-skills`.

If it doesn't exist, clone to a temporary location:

```bash
git clone --depth 1 https://github.com/bolasblack/claude-skills.git /tmp/c4-skills
```

Set `REPO_DIR=/tmp/c4-skills`.

## Step 3: Install chosen extensions

Run the install script based on the user's choices from Step 1.

Use `--tools <comma-separated-tools>` when the user chose explicit tools. Omit `--tools` only for auto-detect.

```bash
# Home directory, auto-detect existing tool directories:
cd $REPO_DIR && ./scripts/install.sh skills <name1> <name2> ...

# Home directory, explicit tools:
cd $REPO_DIR && ./scripts/install.sh --tools claude,pi skills <name1> <name2> ...

# Project directory, explicit tools recommended:
cd $REPO_DIR && ./scripts/install.sh --project <project_dir> --tools agents,claude skills <name1> <name2> ...

# Same pattern for other types:
cd $REPO_DIR && ./scripts/install.sh [--project <dir>] [--tools <tools>] agents <name1> <name2> ...
cd $REPO_DIR && ./scripts/install.sh [--project <dir>] [--tools <tools>] commands <name1> <name2> ...
cd $REPO_DIR && ./scripts/install.sh [--project <dir>] [--tools pi] pi-extensions <name1> <name2> ...

# Or everything:
cd $REPO_DIR && ./scripts/install.sh [--project <dir>] [--tools <tools>] ALL
```

Show the install output to the user.

## Step 4: Persist repository and confirm

If the repository was cloned to `/tmp/c4-skills` (not already at `~/.c4-skills`), ask:

> Would you like to keep the repository at `~/.c4-skills` for faster updates next time?

- If yes: `mv /tmp/c4-skills ~/.c4-skills`
- If no: `rm -rf /tmp/c4-skills`

Tell the user:
- What was installed
- Skills/agents are ready to use immediately
- To update later: re-run the same process (if `~/.c4-skills` exists, it will `git pull` automatically)
