# 05. Skill Maintenance Playbook

Use this when pi updates and this skill must stay current.

## Update triggers

- `pi --version` changed
- extension/settings/packages docs changed
- new event/config/CLI behavior appears
- CHANGELOG entries reference breaking changes

## Maintenance procedure

1. Capture baseline:
   - current skill version
   - target pi version
2. Re-read authoritative docs:
   - `packages/coding-agent/README.md`
   - `packages/coding-agent/docs/extensions.md`
   - `packages/coding-agent/docs/settings.md`
   - `packages/coding-agent/docs/packages.md`
   - `packages/coding-agent/docs/skills.md`
   - `packages/coding-agent/docs/prompt-templates.md`
   - `packages/coding-agent/docs/themes.md`
   - `packages/coding-agent/docs/providers.md`
   - `packages/coding-agent/docs/custom-provider.md`
   - `packages/coding-agent/docs/keybindings.md`
   - `packages/coding-agent/docs/tui.md`
3. Read CHANGELOG for breaking changes and new features since last update.
4. Gap analysis:
   - added/removed events
   - changed defaults/settings keys
   - packaging semantics changes
   - new API methods and helpers
   - new examples worth incorporating
5. Update skill files:
   - keep `SKILL.md` concise workflow-first
   - push deep detail into `references/`
   - refresh `templates/` (extension, prompt, theme, settings)
   - mark removed APIs explicitly with migration notes
6. Regression smoke checks:
   - registerTool/registerCommand
   - one safety gate (`tool_call`)
   - package install/load flow
7. Validate against skill-composer checklist:
   - description includes WHAT and WHEN
   - no XML tags in frontmatter
   - instructions are specific and actionable
   - version history updated
8. Append Version History entry.

## Compatibility policy

- Prefer additive guidance.
- Mark deprecated/removed behavior explicitly with migration notes.
- Avoid hardcoding a provider unless the skill is provider-specific.

## Version entry template

```markdown
- vX.Y.Z (YYYY-MM-DD): Synced to pi vA.B.C; updated [sections], added [capability], deprecated [old behavior].
```
