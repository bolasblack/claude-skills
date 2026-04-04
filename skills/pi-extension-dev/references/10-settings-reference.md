# Settings Reference (Local)

Summary of `packages/coding-agent/docs/settings.md` with the core settings that affect extensions, packages, and runtime behavior.

## Settings locations

- Global: `~/.pi/agent/settings.json`
- Project: `.pi/settings.json`
- Project settings override global (nested objects merge).

## Resource loading (extensions/skills/prompts/themes)

```json
{
  "packages": ["pi-skills"],
  "extensions": ["/path/to/ext.ts", ".pi/extensions"],
  "skills": ["/path/to/skills"],
  "prompts": ["/path/to/prompts"],
  "themes": ["/path/to/themes"],
  "enableSkillCommands": true
}
```

- Paths in global settings resolve relative to `~/.pi/agent`.
- Paths in project settings resolve relative to `.pi`.
- Arrays support glob patterns and exclusions (`!pattern`, `+path`, `-path`).

## Model & thinking

- `defaultProvider`, `defaultModel`, `defaultThinkingLevel`
- `hideThinkingBlock` — Hide thinking blocks in output.
- `thinkingBudgets` — Override token budgets per thinking level:

```json
{
  "thinkingBudgets": {
    "minimal": 1024,
    "low": 4096,
    "medium": 10240,
    "high": 32768
  }
}
```

- `enabledModels` — Model patterns for Ctrl+P cycling (same format as `--models`).

## UI & display

- `theme`, `quietStartup`, `collapseChangelog`
- `doubleEscapeAction` (`"tree"`, `"fork"`, `"none"`)
- `treeFilterMode` (`"default"`, `"no-tools"`, `"user-only"`, `"labeled-only"`, `"all"`)
- `editorPaddingX`, `autocompleteMaxVisible`, `showHardwareCursor`

## Compaction & branch summary

```json
{
  "compaction": {
    "enabled": true,
    "reserveTokens": 16384,
    "keepRecentTokens": 20000
  },
  "branchSummary": {
    "reserveTokens": 16384,
    "skipPrompt": false
  }
}
```

## Retry & transport

- `retry.enabled`, `retry.maxRetries`, `retry.baseDelayMs`, `retry.maxDelayMs`
  - When provider requests a retry delay longer than `maxDelayMs`, the request fails immediately. Set to `0` to disable the cap.
- `transport`: `"sse"`, `"websocket"`, or `"auto"`
- `steeringMode`, `followUpMode`: `"all"` or `"one-at-a-time"`

## Images & terminal

- `terminal.showImages`, `terminal.clearOnShrink`
- `images.autoResize`, `images.blockImages`

## Shell settings

- `shellPath` (custom shell)
- `shellCommandPrefix` (prefix for every bash command)
- `npmCommand` — Command argv for npm package operations:

```json
{
  "npmCommand": ["mise", "exec", "node@20", "--", "npm"]
}
```

## Sessions

- `sessionDir` — Directory for session file storage. Accepts absolute or relative paths. `--session-dir` CLI flag takes precedence.

```json
{ "sessionDir": ".pi/sessions" }
```

## Markdown

- `markdown.codeBlockIndent` — Indentation for code blocks (default: `"  "`).

## Project override semantics

Nested objects merge, so project settings can override only specific fields:

```json
// global
{ "compaction": { "enabled": true, "reserveTokens": 16384 } }

// project
{ "compaction": { "reserveTokens": 8192 } }

// effective
{ "compaction": { "enabled": true, "reserveTokens": 8192 } }
```
