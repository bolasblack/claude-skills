# Claude Extensions

Personal collection of Claude Code skills, commands, and agents.
Compatible with **Claude Code**, **Codex**, **OpenCode**, and **pi**.

Legend: `⭐` recommended, `🌐` imported or adapted from an external source.

## Installation

Paste this into Claude Code, Codex, OpenCode, or any compatible AI coding agent:

> Read https://raw.githubusercontent.com/bolasblack/claude-skills/master/llms.install.md and follow the instructions to install extensions.

The agent will analyze your project, recommend relevant extensions, and walk you through the installation interactively.

> [!TIP]
> Prefer manual installation? See [Manual Installation](#manual-installation).

Skills can also be installed with the [skills CLI](https://github.com/vercel-labs/skills):

```bash
npx skills add bolasblack/claude-skills --skill <skill-name>
```

## Skills

| Skill | Description |
|-------|-------------|
| ⭐ [agent-centric](./skills/agent-centric/) | Framework for agent-centric development with AGD (decision records) tracking, validation and indexing |
| ⭐ [guardrails](./skills/guardrails/) | Rendered guardrail framework for bounded agent context. Keeps hard project rules in one-rule-per-file GRL sources behind a compact router, with a Bun CLI to validate, render on demand, and review changes |
| ⭐ [mcp-skill-generator](./skills/mcp-skill-generator/) | Convert MCP servers to Claude Code skills with progressive disclosure. Generates programmatic API for AI to write code that calls MCP tools |
| ⭐ [skill-composer](./skills/skill-composer/) | **Create and maintain skills that work across agents—with repeatable eval infrastructure built in.** [See the full comparison →](./skills/skill-composer/README.md#beyond-scaffolding) |
| [git-hook](./skills/git-hook/) | Adopt reusable Git hooks with a repo-owned Lefthook runner, Git-private binary, verified bootstrap, and fresh-clone setup path |
| [dependency-safety-check](./skills/dependency-safety-check/) | Screen third-party dependencies for vulnerabilities and supply-chain risk with a bundled `check-deps.py` gate before installation |
| [mise-env](./skills/mise-env/) | Claude Code hook plugin: each Bash command sees the mise environment of the directory it runs in, not the one the session or `claude --bg` daemon started in |
| [design-md](./skills/design-md/) | Create, update, validate, diff, or export DESIGN.md files following Google's [Stitch DESIGN.md spec](https://stitch.withgoogle.com/docs/design-md/overview) |
| 🌐 [frontend-design](./skills/frontend-design/) | Create distinctive, production-grade frontend interfaces with high design quality |
| 🌐 [caveman](./skills/caveman/) | Terse caveman voice: answer first, drop ceremony, keep every technical fact. Stays on until "stop caveman" |
| 🌐 [grill-me](./skills/grill-me/) | Stress-test plans and designs one question at a time, resolving decision dependencies and confirming shared understanding |
| 🌐 [teach-me](./skills/teach-me/) | Learn an unfamiliar topic through a beginner-friendly HTML explainer with large visuals and concise captions |
| 🌐 [show-me](./skills/show-me/) | See the current structure, flow, or change through concise diagrams, code sketches, and focused HTML artifacts |
| 🌐 [create-verification-skill](./skills/create-verification-skill/) | Generate a project-local `verify-<app>` skill that launches, drives, and proves the real app the way a user does, with a seeded feature map. Companion to `maintain-verification-skill` |
| 🌐 [maintain-verification-skill](./skills/maintain-verification-skill/) | Periodic upkeep pass for a verification skill and its feature map: parallel source readers, one live pass over every feature, at most one PR of proven corrections |
| 🌐 [create-formal-verification-skill](./skills/create-formal-verification-skill/) | Generate a project-local skill that formally verifies the code where a bug costs the most, with whichever tool fits, and proves it by catching a scratch break. Companion to `maintain-formal-verification-skill` |
| 🌐 [maintain-formal-verification-skill](./skills/maintain-formal-verification-skill/) | Bring formal verification back in line after the code changes: update the model from the code, rerun, and separate drift in the verification from bugs in the code |
| 🌐 [statechart](./skills/statechart/) | Check a TLA+ model and draw it as a Mermaid statechart, with a shortest path for each rule that breaks |
| [pi-extension-dev](./skills/pi-extension-dev/) | Guide for developing, debugging, and shipping pi-coding-agent extensions and packages |
| 🌐 [seo-site-audit](./skills/seo-site-audit/) | Website SEO / technical SEO audit with engineering-ready backlog. Covers robots.txt, sitemap, canonical, redirects, meta tags, OG/Twitter, JSON-LD, internal linking, Core Web Vitals |
| 🌐 [seo-article-optimizer](./skills/seo-article-optimizer/) | Single article/landing page SEO optimization. Includes keyword analysis, readability scoring, heading structure, meta title/description, URL slug, internal links, featured snippet opportunities |
| [mcp-context7](./skills/mcp-context7/) | Query up-to-date library documentation and code examples using Context7 |
| [mcp-deepwiki](./skills/mcp-deepwiki/) | Access and query GitHub repository documentation using DeepWiki's AI-powered knowledge base |
| [mcp-fetch](./skills/mcp-fetch/) | Web content fetching and conversion to markdown for efficient LLM consumption |
| [mcp-grep](./skills/mcp-grep/) | Search GitHub repositories for real-world code examples using grep.app |
| [playwright](./skills/playwright/) | Complete browser automation with Playwright. Auto-detects dev servers, writes test scripts, takes screenshots, validates web functionality |

## Agents

| Agent | Description |
|-------|-------------|
| [security-auditor](./agents/security-auditor/) | Expert security auditor specializing in comprehensive security assessments, compliance validation, and risk management |
| [prompt-injection-auditor](./agents/prompt-injection-auditor/) | Expert in detecting prompt injection attacks, invisible characters, AI security review bypasses, and LLM-specific security risks |

## Pi Extensions

| Extension | Description |
|-----------|-------------|
| [permission-guard](./pi-extensions/permission-guard/) | Tool permission guard with deny-by-confirmation policy and persisted allow rules |
| [system-notify](./pi-extensions/system-notify/) | System-level notifications for pi events, used by permission-guard for action prompts |
| [web-search](./pi-extensions/web-search/) | Multi-provider web search tool for pi with automatic retry and zero external dependencies |

## Manual Installation

The installer copies extensions by default. Use `--mode symlink` for relative symlinks during local development; copied installations need reinstalling after source changes. Without `--project`, installation targets detected tools under the home directory; use `--tools` to select explicit targets.

Skills use the tools' native discovery directories:

| Targets | Home installation | Project installation |
|---------|-------------------|----------------------|
| `agents`, [Codex](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills), [OpenCode](https://opencode.ai/docs/skills/#place-files), [pi](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md#locations) | `~/.agents/skills` | `.agents/skills` |
| [Claude Code](https://code.claude.com/docs/en/skills#choose-where-skills-load) | `~/.claude/skills` | `.claude/skills` |

Selecting several targets that share a directory installs each skill once. Skills in the shared directory are available to all tools that read it; uninstalling a shared skill affects all of those tools.

After a successful shared installation, the installer removes matching copies or links managed by this repository from the selected tools' individual skill directories. Uninstall checks both locations. Unmanaged entries are preserved and reported. Commands, agents, and pi extensions use their tool-specific directories.

```bash
git clone --depth 1 https://github.com/bolasblack/claude-skills.git ~/.c4-skills
cd ~/.c4-skills

./scripts/install.sh ALL                    # Install all public extensions of all types
./scripts/install.sh __ALL                  # Also include supported private entries (see below)
./scripts/install.sh skills ALL             # Install all public skills
./scripts/install.sh skills __ALL           # Install all skills including private
./scripts/install.sh skills guardrails      # Install specific skill
./scripts/install.sh commands ALL           # Install all public commands
./scripts/install.sh agents security-auditor  # Install specific agent
./scripts/install.sh pi-extensions ALL      # Install all public pi extensions
./scripts/install.sh --mode symlink skills guardrails  # Install using relative symlinks

# Install to explicit tools (agents, claude, codex, opencode, pi):
./scripts/install.sh --tools claude,pi skills ALL

# Install to a specific project directory:
./scripts/install.sh --project /path/to/myapp --tools agents,claude skills ALL
```

`ALL` scans public extensions. For skills, commands, and agents, `<type> __ALL` also scans the matching `private/` directory; private entries can also be installed by name, with public names taking precedence. Top-level `__ALL` only visits types whose public directory exists, and private pi extensions are not supported by these scripts. See [Private Extensions](CLAUDE.md#private-extensions) for details.

## Compatibility

| Type     | Claude Code | Codex | OpenCode | pi |
|----------|-------------|-------|----------|----|
| Skills   | ✓           | ✓     | ✓        | ✓  |
| Commands | ✓           | ✗     | ✓        | ✗  |
| Agents   | ✓           | ✗     | ✓        | ✓  |
| Pi Extensions | ✗      | ✗     | ✗        | ✓  |

## Structure

```
.
├── skills/
│   ├── guardrails/
│   │   ├── SKILL.md
│   │   └── ...
│   └── ...
├── commands/
│   └── <command-name>/
│       └── COMMAND.md
├── agents/
│   ├── security-auditor/
│   │   └── AGENT.md
│   └── ...
├── pi-extensions/
│   ├── permission-guard/
│   │   └── index.ts
│   ├── system-notify/
│   │   └── index.ts
│   └── web-search/
│       └── index.ts
├── scripts/
│   └── install.sh
└── _sunset/              # retired extensions, same layout; not installable
```

## Sunset

Sunset extensions are no longer installable and will be removed in the future. To remove an old install, run `./scripts/uninstall.sh <type> <name>`.

| Extension | Why | Use instead |
|-----------|-----|-------------|
| [codex](./_sunset/skills/codex/) | Wrapped the vendor's headless CLI with its own flags and stream parser, which broke with CLI updates and could not guarantee the read-only behaviour it promised | The runner's built-in code review, or gstack's `/codex` skill for a Codex second opinion |
| [grok](./_sunset/skills/grok/) | Wrapped the vendor's headless CLI with its own flags and stream parser, which broke with CLI updates and could not guarantee the read-only behaviour it promised; on Grok 1.0.70, plan mode does not block shell writes | The runner's built-in code review, or gstack's `/codex` skill for a Codex second opinion |
| [command-creator](./_sunset/skills/command-creator/) | Claude Code merged custom slash commands into the skill system, so new commands should be written as skills | [skill-composer](./skills/skill-composer/) |
| 🌐 [parallel-agent-workflow](./_sunset/skills/parallel-agent-workflow/) | Claude Code now runs subagents in their own git worktrees (`isolation: "worktree"`) and orchestrates them with Workflows, so a hand-rolled worktree workflow adds little | Claude Code's built-in worktree isolation and Workflows |
| [code-reviewer](./_sunset/agents/code-reviewer/) | A persona-style reviewer with no change scope, no spec, no requirement to verify findings, and no rule for what happens to a finding, so its reviews mostly produce nitpicks and design suggestions nobody needs | The code review built into your agent runner (Claude Code's `/code-review`, Codex's `codex review`, and the like) |
| 🌐 [js-code-simplifier](./_sunset/agents/js-code-simplifier/) | An unmodified import of Anthropic's official `code-simplifier` agent that presents one upstream project's code style (prefer the `function` keyword, explicit return types, and so on) as if it were the current project's standards, and tells itself to run proactively without being asked | The simplify command built into your agent runner (Claude Code's `/simplify`), or the upstream [`code-simplifier`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier) plugin for the original |

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on importing or creating extensions.

## License

Extensions, scripts, and docs written in this repository are under its license: personal use.

Imported extensions keep their own upstream licenses. The license text and attribution live with the imported extension. See [AGD-008](.agents/decisions/AGD-008_repository-and-imported-licenses.md).
