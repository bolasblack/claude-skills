# Claude Extensions

Personal collection of Claude Code skills, commands, and agents.
Compatible with Claude Code, Codex, OpenCode, and pi.

**See [.agents/CLAUDE.md](.agents/CLAUDE.md) for the Agent Centric framework.**

## Structure

```
.
├── skills/          # Skill definitions (SKILL.md)
├── commands/        # Command definitions (COMMAND.md)
├── agents/          # Agent definitions (AGENT.md)
├── pi-extensions/   # Pi extension files and directories
└── scripts/         # Installation and utility scripts
```

## Usage

For end-user installation, follow the README flow: paste the install prompt into Claude Code, Codex, OpenCode, or any compatible AI coding agent.

Use `./scripts/install.sh` from the repo root for repository maintenance, local development, and testing symlink setup:

```bash
./scripts/install.sh ALL                    # Install all public extensions of all types
./scripts/install.sh __ALL                  # Install all extensions including experimental
./scripts/install.sh skills ALL             # Install all public skills
./scripts/install.sh skills __ALL           # Install all skills including experimental
./scripts/install.sh skills color-master    # Install specific skill
./scripts/install.sh commands ALL           # Install all commands
./scripts/install.sh agents code-reviewer   # Install specific agent
./scripts/install.sh pi-extensions ALL      # Install all pi extensions
./scripts/install.sh --tools claude,pi skills ALL  # Install to explicit tools
./scripts/install.sh --project /path/to/myapp --tools agents,claude skills ALL  # Install to a project
```

## Compatibility

| Type     | Claude Code | Codex | OpenCode | pi |
| -------- | ----------- | ----- | -------- | -- |
| Skills   | ✓           | ✓     | ✓        | ✓  |
| Commands | ✓           | ✗     | ✓        | ✗  |
| Agents   | ✓           | ✗     | ✓        | ✓  |
| Pi Extensions | ✗      | ✗     | ✗        | ✓  |

## Guidelines

- Keep each extension focused and single-purpose
- Write prompts in English for consistency
- Use the installation script to set up symlinks
- Update README.md whenever adding or removing any command, agent, or skill
- Experimental skills (under the "Experimental" subsection in README.md) are tied to the author's environment and not guaranteed to work elsewhere. Place environment-specific or unpublished skills there instead of the general list

## Thinking Principles

- Reason from first principles, not by analogy or convention.
- POSIWID: the purpose of a system is what it does. Judge designs by actual outcomes, not stated intentions.

## Task Delegation

- **Interactive tasks** (code changes, refactoring, debugging): do them directly in the main conversation.
- **Fire-and-forget tasks** (research, codebase exploration, analysis): delegate to background subagents (`run_in_background: true`). Inherit the current model and context where possible.

## Testing

- Red/green TDD: write a failing test first, then write the minimum code to make it pass.
- Tests describe and verify expected behavior, not implementation details.
- Test files colocated with source:
  - Python: `[name]_test.py`.
  - Others: `[name].test.[ext]`

## Modifying Agent Centric Scripts

**IMPORTANT:** Files in `.agents/scripts/` are auto-managed by the `agent-centric` skill. Do NOT edit them directly.

To modify these scripts:

1. Edit the source files in `skills/agent-centric/scripts/`
2. Run `./scripts/install.sh skills agent-centric` to sync changes
3. The sync script will automatically update `.agents/scripts/`
