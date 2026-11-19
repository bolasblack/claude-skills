# Project Setup

Read this file in full only when the user explicitly requests project setup. Run
initialization only on that request; never run it to get past a failed setup check.

Set the project root and installed skill directory first, then initialize and rerun
the setup check:

```bash
export CLAUDE_PROJECT_DIR="/absolute/path/to/project"
export CLAUDE_SKILL_DIR="/absolute/path/to/agent-centric"
bash "$CLAUDE_SKILL_DIR/scripts/init.sh"
python3 "$CLAUDE_SKILL_DIR/scripts/check-setup.py" "$CLAUDE_PROJECT_DIR"
```

Initialization creates `.agents/decisions/`, runtime scripts, configuration,
indexes, and project instructions. Skill use requires the final check to exit `0`.
The check itself only reads the project; it does not initialize, sync, validate
decisions, regenerate indexes, or execute configured project scripts.
