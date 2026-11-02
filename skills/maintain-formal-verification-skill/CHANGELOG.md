# Changelog

## 2026-11-02

### Import the formal-verification maintenance loop

- **Changed:** Import `maintain-formal-verification-skill` from Cursor's pstack plugin. Name common project skill directories for verify-skill discovery, run the temporary break in a temporary worktree or copy, separate hand-written models from verifiers that run on the code, confirm a changed verify skill or harness with the user before running it, stop accepting a commit message alone as evidence for changing a property, keep replays local or disposable, stage only verification files, remove `disable-model-invocation: true`, narrow the description to explicit requests, and add `license: MIT` to the frontmatter.
- **Why:** The user requested this skill as the upkeep companion to `create-formal-verification-skill`. Upstream resolves Cursor paths through a Claude Code adapter file this import does not include. The import audit found that the text forbade product edits while requiring a break in product code with nothing protecting uncommitted work, that a commit message alone could turn a broken promise into a changed property, and that the skill ran repository commands before reading changes to them. The user chose one invocation behavior on every host. OpenCode ignores the field, so explicit-only behavior could not hold everywhere, and the field stops other skills, agents, and session scheduled tasks from invoking the skill.
