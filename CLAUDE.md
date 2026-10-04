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
├── scripts/         # Installation and utility scripts
└── private/         # (gitignored) author-private extensions — its own git repo, same layout
```

## Private Extensions

`private/` is gitignored by this public repo and versioned as its own git repository (rooted at `private/`, private remote). Personal, unpublished extensions live there, mirroring the top-level layout (`private/skills/`, `private/commands/`, `private/agents/`). Never reference private extension names from public files.

- **Setup order matters.** On a new machine: clone this public repo first, then clone the private repo into it as `private/` (`git clone <private-repo-url> private` from the repo root). Never clone the private repo standalone — the tooling assumes it lives at `claude-skills/private/`. If `private/` is missing, the working copy is still fully functional for public extensions.
- Full setup and install instructions live in `private/README.md` (once cloned).

- For skills, commands, and agents, named installs search the public directories first, then `private/<type>/<name>`. Private entries can be installed by name. `ALL` scans public entries; `<type> __ALL` also scans that type's private directory.
- Top-level `__ALL` only visits types whose public directory exists. Use `<type> __ALL` for a type that exists only under `private/`.
- Pi extensions are read from the public `pi-extensions/` directory (or its `extensions/` subdirectory). The install and uninstall scripts do not scan `private/pi-extensions/`.
- For skills, commands, and agents, `uninstall.sh <type> ALL` scans public and private source directories and removes matching managed installs. It does not discover entries already removed from those source directories.
- The private repo root contains `skills/<name>/SKILL.md`, so the skills CLI also works against it: `npx skills add <private-repo-url>` or `npx skills add ./private`.
- To publish a private extension: `mv private/<type>/<name> <type>/<name>`, add a README row, then commit the addition here and the removal in `private/`.

## Usage

For end-user installation, follow the README flow: paste the install prompt into Claude Code, Codex, OpenCode, or any compatible AI coding agent.

Use `./scripts/install.sh` from the repo root for repository maintenance and local installation. The default mode is `copy`; use `--mode symlink` for relative symlinks. Reinstall copied extensions after changing their source files.

Without `--project`, installation targets detected tools under the home directory. Use `--project` to install into a project and `--tools` to select explicit targets.

```bash
./scripts/install.sh ALL                    # Install all public extensions of all types
./scripts/install.sh __ALL                  # Also include supported private entries (see above)
./scripts/install.sh skills ALL             # Install all public skills
./scripts/install.sh skills __ALL           # Install all skills including private
./scripts/install.sh skills guardrails      # Install specific skill
./scripts/install.sh commands ALL           # Install all public commands
./scripts/install.sh agents code-reviewer   # Install specific agent
./scripts/install.sh pi-extensions ALL      # Install all public pi extensions
./scripts/install.sh --mode symlink skills guardrails  # Install using relative symlinks
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
- Use the installation script for copies or explicit `--mode symlink` installs
- Update README.md whenever adding or removing any command, agent, or skill
- Environment-specific or unpublished skills live in the private repo (`private/skills/`), not in the public list — see Private Extensions

## Thinking Principles

- Reason from first principles, not by analogy or convention.
- POSIWID: the purpose of a system is what it does. Judge designs by actual outcomes, not stated intentions.

## Task Delegation

- **Interactive tasks** (code changes, refactoring, debugging): do them directly in the main conversation.
- **Independent background work** (research, codebase exploration, analysis): delegate when the task benefits from parallel work and the current host supports it. Use the host's available subagent API and inherit the current model and context where supported. Otherwise, do the work in the main conversation.

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
2. From the repository root, sync this initialized project's managed files directly from the repository source:

   ```bash
   CLAUDE_PROJECT_DIR="$PWD" \
   CLAUDE_SKILL_DIR="$PWD/skills/agent-centric" \
   bash skills/agent-centric/scripts/sync-scripts.sh
   ```

3. Review the generated changes. The sync respects `disableAutoUpdateScripts` in `.agents/config.json` and also refreshes the managed `.agents/CLAUDE.md` template and `.agents/.gitignore`.

Installing `agent-centric` updates the skill in agent installation directories; it does not run this project sync. The skill calls for this sync only after its required setup check passes for the target project.
