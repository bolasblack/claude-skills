---
name: mise-env
description: Gives each Claude Code Bash command the mise environment of the directory it runs in, through a SessionStart hook this skill ships. Use when Bash commands show mise variables or tool versions from the wrong directory, such as one inherited from a shared `claude --bg` daemon, or when asked how mise env works in Claude Code sessions.
compatibility: Claude Code only (hook plugin). Needs mise on PATH and bash.
---

# mise-env

Installed in the user's skills directory, this skill loads as its own plugin, `mise-env@skills-dir`. Its `SessionStart` hook runs `scripts/mise-env-hook.sh`, which appends

```
eval "$(mise hook-env -s bash -q)"
```

to the file named by `$CLAUDE_ENV_FILE`. Claude Code sources that file before each Bash command, so mise recomputes the environment for the command's starting directory. Without it, a session keeps the mise variables of the directory where Claude Code or the shared `claude --bg` daemon started.

The hook does nothing, silently, when `CLAUDE_ENV_FILE` is empty or `mise` is not on PATH, and it always exits 0, so a session start never breaks. The cost is about 8 ms per command.

## Gaps

- `cd X && cmd` inside one command still runs `cmd` with the old environment: the sync happens before the command starts. The next command is correct.
- The Claude process, other hooks and MCP servers keep their inherited environment. Only Bash tool commands are corrected.

## Check that it works

1. `claude plugin list` (or `/plugin`) lists `mise-env@skills-dir` as enabled.
2. In a directory with a `.mise.toml` that sets `X=a`, then a directory without one, run these as separate Bash commands: `echo $X`, `cd <dir with .mise.toml>`, `echo $X`, `cd <other dir>`, `echo $X`. Expect unset, then `a`, then unset.
3. `bash scripts/mise-env-hook.test.sh` passes.

The user switches the hook off in `/plugin`. An agent leaves the plugin files as they are.
