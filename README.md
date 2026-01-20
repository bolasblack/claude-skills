# Claude Extensions

Personal collection of Claude Code skills, commands, and agents.
Compatible with **Claude Code**, **Codex**, and **OpenCode**.

## Skills

| Skill | Description |
|-------|-------------|
| [color-master](./skills/color-master/) | Convert colors between formats (HEX, RGB, HSL, CMYK, LAB, LCH, oklch, ANSI), generate color harmonies, check WCAG accessibility, and simulate color blindness |
| [frontend-design](./skills/frontend-design/) | Create distinctive, production-grade frontend interfaces with high design quality |
| [playwright](./skills/playwright/) | Complete browser automation with Playwright. Auto-detects dev servers, writes test scripts, takes screenshots, validates web functionality |
| [seo-site-audit](./skills/seo-site-audit/) | Website SEO / technical SEO audit with engineering-ready backlog. Covers robots.txt, sitemap, canonical, redirects, meta tags, OG/Twitter, JSON-LD, internal linking, Core Web Vitals |
| [seo-article-optimizer](./skills/seo-article-optimizer/) | Single article/landing page SEO optimization. Includes keyword analysis, readability scoring, heading structure, meta title/description, URL slug, internal links, featured snippet opportunities |
| [skill-reviewer](./skills/skill-reviewer/) | Reviews Claude Code skills against official best practices. Validates YAML frontmatter, checks SKILL.md length, verifies progressive disclosure patterns, assesses description quality |
| [parallel-agent-workflow](./skills/parallel-agent-workflow/) | Coordinate multiple agents working in parallel using git worktrees to avoid file conflicts. Use for multi-component refactoring or parallel feature development |
| [skill-composer](./skills/skill-composer/) | Create and improve Claude Code Skills following official best practices. Includes step-by-step workflow, description patterns, and real-world examples |
| [command-creator](./skills/command-creator/) | Guide for creating Claude Code slash commands. Helps define command structure, frontmatter, arguments, and best practices |
| [mcp-skill-generator](./skills/mcp-skill-generator/) | Convert MCP servers to Claude Code skills with progressive disclosure |
| [mcp-context7](./skills/mcp-context7/) | Query up-to-date library documentation and code examples using Context7 |
| [mcp-deepwiki](./skills/mcp-deepwiki/) | Access and query GitHub repository documentation using DeepWiki's AI-powered knowledge base |
| [mcp-fetch](./skills/mcp-fetch/) | Web content fetching and conversion to markdown for efficient LLM consumption |
| [mcp-grep](./skills/mcp-grep/) | Search GitHub repositories for real-world code examples using grep.app |

## Agents

| Agent | Description |
|-------|-------------|
| [code-reviewer](./agents/code-reviewer/) | Principled code reviewer in Uncle Bob's tradition - direct, principle-based, focused on craftsmanship |
| [js-code-simplifier](./agents/js-code-simplifier/) | Simplifies and refines JavaScript/TypeScript code for clarity, consistency, and maintainability while preserving all functionality |
| [security-auditor](./agents/security-auditor/) | Expert security auditor specializing in comprehensive security assessments, compliance validation, and risk management |
| [prompt-injection-auditor](./agents/prompt-injection-auditor/) | Expert in detecting prompt injection attacks, invisible characters, AI security review bypasses, and LLM-specific security risks |

## Installation

Install extensions as symlinks to your AI coding tool:

```bash
./scripts/install.sh ALL                    # Install all extensions of all types
./scripts/install.sh skills ALL             # Install all skills
./scripts/install.sh skills color-master    # Install specific skill
./scripts/install.sh commands ALL           # Install all commands
./scripts/install.sh agents code-reviewer   # Install specific agent
```

## Compatibility

| Type     | Claude Code | Codex | OpenCode |
|----------|-------------|-------|----------|
| Skills   | ✓           | ✓     | ✓        |
| Commands | ✓           | ✗     | ✓        |
| Agents   | ✓           | ✗     | ✓        |

## Structure

```
.
├── skills/
│   ├── color-master/
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
└── scripts/
    └── install.sh
```

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on importing or creating extensions.

## License

Personal use. Individual extensions may have their own licenses.
