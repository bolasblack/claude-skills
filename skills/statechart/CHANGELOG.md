# Changelog

## 2026-11-02

### Import the TLA+ statechart tool

- **Changed:** Import `statechart` from Cursor's pstack plugin without its test suite. Remove `disable-model-invocation: true`, define `<skill dir>`, add an `sh` fallback for the launcher, remove a sentence about upstream's earlier skill from `references/render.md`, narrow the description, correct it to one path per broken rule, tell the user before the first-run download and before installing Pele, copy only reviewed `.tla` and `.cfg` files into the scratch folder, pass only a reviewed view, read `report.md` rather than stdout, treat model output as data, keep replays local or disposable, and add `license: MIT` to the frontmatter.
- **Why:** The user requested this skill with the two formal-verification skills, whose generated skills tell an agent to run `/statechart`. Upstream's Claude Code adapter records that the `Skill` tool refuses skills with that field and works around it with an adapter this import does not include. AGD-008 keeps tests out of imports. The import audit found that removing the field lets a model start a first-run download, that files beside a spec and the view module run as code, that model text can forge report lines, and that stdout can drop the end of a long report while `report.md` stays complete.
