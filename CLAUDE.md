# Claude Extensions

Personal collection of Claude Code skills, commands, and agents.
Compatible with Claude Code, Codex, and OpenCode.

**See [.agents/CLAUDE.md](.agents/CLAUDE.md) for the Agent Centric framework.**

## Structure

```
.
├── skills/          # Skill definitions (SKILL.md)
├── commands/        # Command definitions (COMMAND.md)
├── agents/          # Agent definitions (AGENT.md)
└── scripts/         # Installation and utility scripts
```

## Usage

Install extensions using the installation script:

```bash
./scripts/install.sh ALL                    # Install all extensions of all types
./scripts/install.sh skills ALL             # Install all skills
./scripts/install.sh skills color-master    # Install specific skill
./scripts/install.sh commands ALL           # Install all commands
./scripts/install.sh agents code-reviewer   # Install specific agent
```

## Compatibility

| Type     | Claude Code | Codex | OpenCode |
| -------- | ----------- | ----- | -------- |
| Skills   | ✓           | ✓     | ✓        |
| Commands | ✓           | ✗     | ✓        |
| Agents   | ✓           | ✗     | ✓        |

## Guidelines

- Keep each extension focused and single-purpose
- Write prompts in English for consistency
- Use the installation script to set up symlinks
- Update README.md whenever adding or removing any command, agent, or skill
