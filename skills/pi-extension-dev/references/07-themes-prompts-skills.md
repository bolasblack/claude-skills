# 07. Themes, Prompts, and Skills

## Themes

Themes are JSON files with all 51 required color tokens. Use the schema for validation:

```
"$schema": "https://raw.githubusercontent.com/badlogic/pi-mono/main/packages/coding-agent/src/modes/interactive/theme/theme-schema.json"
```

Requirements:
- `name` must be unique.
- `vars` is optional for reusable colors.
- `colors` must define every token (no omissions).
- Optional `export` section overrides HTML export colors (`pageBg`, `cardBg`, `infoBg`).
  Export colors resolve theme variables the same way as `colors`.

Discovery:
- Built-in: `dark`, `light`
- Global: `~/.pi/agent/themes/*.json`
- Project: `.pi/themes/*.json`
- Package `themes/` directory or `pi.themes` entries
- CLI: `--theme <path>`

Hot reload: editing the active custom theme file reloads it automatically.

Disable discovery with `--no-themes`.

## Prompt templates

Format:

```markdown
---
description: Review staged git changes
---
Review the staged changes (`git diff --cached`). Focus on bugs and error handling.
```

Arguments:
- `$1`, `$2` positional args
- `$@` or `$ARGUMENTS` for all args joined
- `${@:N}` for args from the Nth position (1-indexed)
- `${@:N:L}` for `L` args starting at N

Discovery:
- `~/.pi/agent/prompts/*.md`
- `.pi/prompts/*.md`
- Package `prompts/` or `pi.prompts`
- CLI: `--prompt-template <path>`

Note: prompt discovery in `prompts/` is non-recursive unless you add subdirectories in settings.

Disable discovery with `--no-prompt-templates`.

## Skills

Structure:

```
my-skill/
├── SKILL.md
├── references/
└── scripts/
```

Frontmatter requirements:
- `name` (lowercase, hyphenated, matches directory, max 64 chars)
- `description` (what it does and when to use; max 1024 chars)

Optional frontmatter:
- `license` — License name or reference.
- `compatibility` — Environment requirements (max 500 chars).
- `metadata` — Arbitrary key-value mapping.
- `allowed-tools` — Space-delimited pre-approved tools (experimental).
- `disable-model-invocation` — When `true`, skill is hidden from system prompt. Users must use `/skill:name`.

Discovery:
- Global: `~/.pi/agent/skills/`, `~/.agents/skills/`
- Project: `.pi/skills/` and `.agents/skills/` ancestry (up to git root)
- Package `skills/` or `pi.skills`
- CLI: `--skill <path>` (even when `--no-skills` is set)

Discovery rules:
- In `~/.pi/agent/skills/` and `.pi/skills/`, root `.md` files are discovered as individual skills.
- In all locations, directories containing `SKILL.md` are discovered recursively.
- In `~/.agents/skills/` and project `.agents/skills/`, root `.md` files are **ignored**.

Disable discovery with `--no-skills`.

Skill commands:
- `/skill:name` loads and runs the skill content
- `/skill:name args` appends args as `User: <args>`
- `enableSkillCommands` toggles command registration

Using skills from other harnesses:
```json
{
  "skills": ["~/.claude/skills", "~/.codex/skills"]
}
```
