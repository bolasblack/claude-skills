#!/bin/bash
# SessionStart hook: make every Bash command re-sync the mise environment of its own directory.
# Claude Code sources $CLAUDE_ENV_FILE before each Bash command.
# Never blocks session start: always exits 0.
[ -n "$CLAUDE_ENV_FILE" ] && command -v mise >/dev/null 2>&1 &&
  echo 'eval "$(mise hook-env -s bash -q)"' >> "$CLAUDE_ENV_FILE" 2>/dev/null
exit 0
