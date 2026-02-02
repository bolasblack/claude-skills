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

## Modifying Agent Centric Scripts

**IMPORTANT:** Files in `.agents/scripts/` are auto-managed by the `agent-centric` skill. Do NOT edit them directly.

To modify these scripts:

1. Edit the source files in `skills/agent-centric/scripts/`
2. Run `./scripts/install.sh skills agent-centric` to sync changes
3. The sync script will automatically update `.agents/scripts/`
