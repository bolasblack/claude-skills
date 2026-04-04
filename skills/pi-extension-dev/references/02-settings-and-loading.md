# 02. Settings and Resource Loading

## Settings layers

- Global: `~/.pi/agent/settings.json`
- Project: `.pi/settings.json` (overrides global)

Nested objects are merged; arrays/primitives override.

## Resource keys

- `packages`
- `extensions`
- `skills`
- `prompts`
- `themes`
- `enableSkillCommands`

## Globs and filters

Arrays accept:
- `pattern` (glob)
- `!pattern` (exclude)
- `+path` (force-include exact path)
- `-path` (force-exclude exact path)

Package entries can be objects to filter resources by type (see `references/03-packaging-and-distribution.md`).

## Discovery defaults

Auto-discovery roots include:
- `~/.pi/agent/extensions`, `.pi/extensions` (also auto-detects `extensions/*/index.ts`)
- `~/.pi/agent/skills`, `.pi/skills`, `~/.agents/skills`, `.agents/skills` ancestry
- `~/.pi/agent/prompts`, `.pi/prompts`
- `~/.pi/agent/themes`, `.pi/themes`

## Skill/prompt/theme discovery rules

- Skills: top-level `.md` files in `~/.pi/agent/skills/` and `.pi/skills/` (not in `.agents/skills/`). Nested `SKILL.md` folders are discovered recursively in all locations.
- Prompts: non-recursive in `prompts/` by default; add subdirectories via `prompts` settings or package manifests.
- Themes: `.json` files under `themes/` directories.

CLI overrides:
- `--skill <path>` adds an explicit skill even with `--no-skills`.
- `--prompt-template <path>` adds a prompt template even with `--no-prompt-templates`.
- `--theme <path>` loads a theme file directly.
- `--no-skills`, `--no-prompt-templates`, `--no-themes` disable auto-discovery.

## Recommended project baseline

```json
{
  "extensions": ["./extensions"],
  "skills": ["./skills"],
  "prompts": ["./prompts"],
  "themes": ["./themes"],
  "enableSkillCommands": true
}
```

## Useful runtime settings

- model defaults: `defaultProvider`, `defaultModel`, `defaultThinkingLevel`
- thinking: `hideThinkingBlock`, `thinkingBudgets`
- compaction: `compaction.enabled`, `reserveTokens`, `keepRecentTokens`
- branch summary: `branchSummary.reserveTokens`, `branchSummary.skipPrompt`
- retries: `retry.*`
- queueing: `steeringMode`, `followUpMode`
- transport: `transport` (`"sse"`, `"websocket"`, `"auto"`)
- shell: `shellPath`, `shellCommandPrefix`, `npmCommand`
- sessions: `sessionDir`
- model cycling: `enabledModels`
- markdown: `markdown.codeBlockIndent`

## Enable/disable resources

Use `pi config` to enable or disable extensions, skills, prompts, and themes from installed packages and local directories. Works for both global and project scopes.

## Resource troubleshooting

1. Not loading?
   - check path resolution and scope
   - run `/reload`
   - check for error diagnostics at startup
2. Conflicts?
   - duplicate command/tool/flag names across extensions
   - commands get numeric suffixes (e.g., `/review:1`, `/review:2`)
3. Skills not showing?
   - verify frontmatter `name`/`description`
   - check `enableSkillCommands`
   - root `.md` files are ignored in `.agents/skills/` directories
