# Claude Extensions

Personal collection of Claude Code skills, commands, and agents.
Compatible with **Claude Code**, **Codex**, **OpenCode**, and **pi**.

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
| [grok](./skills/grok/) | Independent second opinion from xAI's Grok via the grok CLI — diff review with a pass/fail gate, adversarial challenge, and free-form consult with session continuity |
| [codex](./skills/codex/) | Independent second opinion from OpenAI Codex via the codex CLI — diff review with a pass/fail gate, adversarial challenge, and free-form consult with session continuity |
| [dependency-safety-check](./skills/dependency-safety-check/) | Screen third-party dependencies for vulnerabilities and supply-chain risk with a bundled `check-deps.py` gate before installation |
| [design-md](./skills/design-md/) | Create, update, validate, diff, or export DESIGN.md files following Google's [Stitch DESIGN.md spec](https://stitch.withgoogle.com/docs/design-md/overview) |
| [frontend-design](./skills/frontend-design/) | Create distinctive, production-grade frontend interfaces with high design quality |
| [pi-extension-dev](./skills/pi-extension-dev/) | Guide for developing, debugging, and shipping pi-coding-agent extensions and packages |
| [seo-site-audit](./skills/seo-site-audit/) | Website SEO / technical SEO audit with engineering-ready backlog. Covers robots.txt, sitemap, canonical, redirects, meta tags, OG/Twitter, JSON-LD, internal linking, Core Web Vitals |
| [seo-article-optimizer](./skills/seo-article-optimizer/) | Single article/landing page SEO optimization. Includes keyword analysis, readability scoring, heading structure, meta title/description, URL slug, internal links, featured snippet opportunities |
| [mcp-context7](./skills/mcp-context7/) | Query up-to-date library documentation and code examples using Context7 |
| [mcp-deepwiki](./skills/mcp-deepwiki/) | Access and query GitHub repository documentation using DeepWiki's AI-powered knowledge base |
| [mcp-fetch](./skills/mcp-fetch/) | Web content fetching and conversion to markdown for efficient LLM consumption |
| [mcp-grep](./skills/mcp-grep/) | Search GitHub repositories for real-world code examples using grep.app |
| [parallel-agent-workflow](./skills/parallel-agent-workflow/) | Coordinate multiple agents working in parallel using git worktrees to avoid file conflicts. Use for multi-component refactoring or parallel feature development |
| [command-creator](./skills/command-creator/) | Guide for creating Claude Code slash commands. Helps define command structure, frontmatter, arguments, and best practices |
| [playwright](./skills/playwright/) | Complete browser automation with Playwright. Auto-detects dev servers, writes test scripts, takes screenshots, validates web functionality |

## Agents

| Agent | Description |
|-------|-------------|
| [code-reviewer](./agents/code-reviewer/) | Principled code reviewer in Uncle Bob's tradition - direct, principle-based, focused on craftsmanship |
| [js-code-simplifier](./agents/js-code-simplifier/) | Simplifies and refines JavaScript/TypeScript code for clarity, consistency, and maintainability while preserving all functionality |
| [security-auditor](./agents/security-auditor/) | Expert security auditor specializing in comprehensive security assessments, compliance validation, and risk management |
| [prompt-injection-auditor](./agents/prompt-injection-auditor/) | Expert in detecting prompt injection attacks, invisible characters, AI security review bypasses, and LLM-specific security risks |

## Pi Extensions

| Extension | Description |
|-----------|-------------|
| [permission-guard](./pi-extensions/permission-guard/) | Tool permission guard with deny-by-confirmation policy and persisted allow rules |
| [system-notify](./pi-extensions/system-notify/) | System-level notifications for pi events, used by permission-guard for action prompts |
| [web-search](./pi-extensions/web-search/) | Multi-provider web search tool for pi with automatic retry and zero external dependencies |

## Manual Installation

```bash
git clone --depth 1 https://github.com/bolasblack/claude-skills.git ~/.c4-skills
cd ~/.c4-skills

./scripts/install.sh ALL                    # Install all public extensions of all types
./scripts/install.sh __ALL                  # Install all public and private extensions
./scripts/install.sh skills ALL             # Install all public skills
./scripts/install.sh skills __ALL           # Install all skills including private
./scripts/install.sh skills guardrails      # Install specific skill
./scripts/install.sh commands ALL           # Install all commands
./scripts/install.sh agents code-reviewer   # Install specific agent
./scripts/install.sh pi-extensions ALL      # Install all pi extensions
./scripts/install.sh --mode symlink skills guardrails  # Install using relative symlinks

# Install to explicit tools (agents, claude, codex, opencode, pi):
./scripts/install.sh --tools claude,pi skills ALL

# Install to a specific project directory:
./scripts/install.sh --project /path/to/myapp --tools agents,claude skills ALL
```

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
│   ├── code-reviewer/
│   │   └── AGENT.md
│   └── ...
├── pi-extensions/
│   ├── permission-guard/
│   │   └── index.ts
│   ├── system-notify/
│   │   └── index.ts
│   └── web-search/
│       └── index.ts
└── scripts/
    └── install.sh
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on importing or creating extensions.

## License

Personal use. Individual extensions may have their own licenses.
