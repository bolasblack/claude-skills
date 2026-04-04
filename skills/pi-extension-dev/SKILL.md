---
name: pi-extension-dev
description: End-to-end workflow for developing, debugging, configuring, and shipping pi-coding-agent extensions and pi packages. Use when building or maintaining extensions, skills, prompt templates, themes, settings.json setups, provider integrations, or when updating this skill after pi releases. Do NOT use for general coding questions unrelated to pi extension development.
---

# Pi Extension Development

Build production-grade customization for `@mariozechner/pi-coding-agent` without forking core internals.

This skill is organized for progressive disclosure:
- This file: execution workflow
- `references/`: detailed technical guidance
- `templates/`: copy-paste starter files

## When to use this skill

Use this skill when you need to:
1. Build or modify an extension (tools, commands, events, UI, provider integrations)
2. Configure resource loading (`settings.json`, discovery paths, package sources)
3. Package and distribute reusable resources as a pi package (npm/git/local)
4. Validate extension behavior across interactive, print, json, and rpc modes
5. Update extension docs/skills after pi version changes

## Quick workflow

1. **Scope the request**
   - Identify target resource type(s): extension / skill / prompt / theme / package / settings
   - Identify runtime mode(s): interactive, print, json, rpc

2. **Pick implementation shape**
   - Small logic: single `*.ts` extension file
   - Multi-module logic: extension directory with `index.ts`
   - Team sharing: pi package with `pi` manifest in `package.json`

   **Model selection policy:** see `references/01-extension-api-cheatsheet.md` (subagent model policy section).

3. **Implement safely**
   - Add tool output truncation
   - Add guardrails for destructive operations (`tool_call` gate)
   - Ensure non-interactive compatibility (`ctx.hasUI` checks)

4. **Configure loading**
   - Wire `.pi/settings.json` (project) and/or `~/.pi/agent/settings.json` (global)
   - Verify resource discovery and `/reload` behavior

5. **Validate behavior**
   - Manual smoke checks for command/tool/event/UI paths
   - Validate mode-specific behavior
   - Check conflicts (tool/command/flag name collisions)

6. **Package and publish (if needed)**
   - Add `keywords: ["pi-package"]` and `pi` manifest
   - Validate dependency model (peerDependencies vs bundled dependencies)
   - Install/test via `pi install` and `pi update`

7. **Record maintenance metadata**
   - Update skill/version notes
   - Add or update migration guidance

---

## Mandatory references to load

For any non-trivial task, read these first:

- `references/01-extension-api-cheatsheet.md`
- `references/02-settings-and-loading.md`
- `references/03-packaging-and-distribution.md`
- `references/04-testing-and-debugging.md`
- `references/05-skill-maintenance-playbook.md`
- `references/06-provider-integrations.md`
- `references/07-themes-prompts-skills.md`

If task is extension-heavy, also read:
- `references/08-extensions-deep-dive.md`

If task is package-heavy, also read:
- `references/09-packages-reference.md`

If task is config-heavy, also read:
- `references/10-settings-reference.md`

---

## Execution policy

- Prefer extension APIs over patching pi core.
- Keep tool outputs bounded and informative.
- Never assume UI methods are available in non-interactive modes.
- Keep keybindings configurable (no hardcoded key checks).
- For path/tool policy enforcement, block in `tool_call` and explain the reason.

---

## Response contract

When delivering work, always provide:
1. What changed (files + purpose)
2. How to load/run it
3. Validation results
4. Known limitations / follow-ups
5. If relevant: migration notes for existing setups

---

## Fast start templates

Use these starter files:
- `templates/extension.index.ts`
- `templates/extension.tool.ts`
- `templates/extension.command.ts`
- `templates/settings.project.json`
- `templates/package.json`
- `templates/prompt.md`
- `templates/theme.json`

---

## Troubleshooting

- Extension not loading? Check path, run `/reload`, check startup diagnostics.
- Tool not appearing in system prompt? Add `promptSnippet` to tool definition.
- File mutation race conditions? Use `withFileMutationQueue()` for file-modifying tools.
- `getApiKey()` errors? Use `getApiKeyAndHeaders()` instead (removed in v0.63.0).
- `session_switch`/`session_fork` errors? Use `session_start` with `event.reason` (removed in v0.65.0).
- UI crashes in print/json mode? Guard with `ctx.hasUI` before all `ctx.ui.*` calls.

## Version History

- v3.0.0 (2026-04-04): Synced to pi v0.65.0. Removed `session_switch`, `session_fork`, `session_directory` events. Updated `getApiKey()` to `getApiKeyAndHeaders()`. Added `defineTool()`, `withFileMutationQueue()`, `prepareArguments`, `promptSnippet`/`promptGuidelines`, `ctx.signal`, `resources_discover` event, `sourceInfo` provenance, namespaced keybinding ids, overlay mode, `ctx.ui.setHiddenThinkingLabel()`, `getArgumentCompletions`, gallery metadata, `npmCommand`/`sessionDir`/`hideThinkingBlock` settings. Updated all references, templates, and examples catalog.
- v2.1.0 (2026-03-09): Added provider/theme/prompt coverage, clarified extension events/context/tool overrides/truncation and message injection guidance, expanded settings/package discovery rules, added new templates, and refreshed debugging/update playbook references.
- v2.0.0 (2026-03-09): Rewritten in English, split into multi-file structure, expanded coverage for extension APIs, settings/resource loading, pi package distribution, mode-aware validation, and skill update playbook.
- v1.0.0 (2026-03-09): Initial single-file version.
