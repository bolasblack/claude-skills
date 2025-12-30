# Claude Skills

Personal collection of Claude Code skill prompts.

## Skills

| Skill | Description |
|-------|-------------|
| [color-master-skill](./color-master-skill/) | Convert colors between formats (HEX, RGB, HSL, CMYK, LAB, LCH, oklch, ANSI), generate color harmonies, check WCAG accessibility, and simulate color blindness |
| [frontend-design-skill](./frontend-design-skill/) | Create distinctive, production-grade frontend interfaces with high design quality |
| [playwright-skill](./playwright-skill/) | Complete browser automation with Playwright. Auto-detects dev servers, writes test scripts, takes screenshots, validates web functionality |

## Usage

1. Copy a skill directory to your Claude Code skills location:
   - Global: `~/.claude/skills/<skill-name>/`
   - Project: `<project>/.claude/skills/<skill-name>/`

2. The skill will be available in your Claude Code conversations.

## Structure

```
.
├── color-master-skill/
│   ├── SKILL.md
│   ├── package.json
│   └── scripts/color.ts
├── frontend-design-skill/
│   └── SKILL.md
├── playwright-skill/
│   ├── SKILL.md
│   ├── run.js
│   ├── lib/
│   └── package.json
└── ...
```

Each skill has its own directory with a `SKILL.md` file containing the skill definition and usage instructions.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines on importing or creating skills.

## License

Personal use. Individual skills may have their own licenses.
