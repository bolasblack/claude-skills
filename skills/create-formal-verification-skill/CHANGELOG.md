# Changelog

## 2026-11-02

### Import the formal-verification generator

- **Changed:** Import `create-formal-verification-skill` from Cursor's pstack plugin. Name common project skill directories and the required frontmatter for the generated skill, refer to `/statechart` by name with a fallback to the checker's own output, run every scratch break in a temporary worktree or copy, separate hand-written models from verifiers that run on the code in the proof step, ask before installing a tool, require secrets to be named by environment variable, remove `disable-model-invocation: true`, narrow the description to explicit requests, and add `license: MIT` to the frontmatter.
- **Why:** The user requested this skill with `maintain-formal-verification-skill` and `statechart`. Upstream resolves Cursor paths through a Claude Code adapter file this import does not include, and its relative link to `statechart` breaks when one skill is installed alone. The import audit found that a scratch break in the user's checkout could destroy uncommitted work, that a break in product code cannot change a hand-written model's result, and that upstream's broad description could start the generator from an ordinary discussion. The user chose one invocation behavior on every host. OpenCode ignores the field, so explicit-only behavior could not hold everywhere, and the field stops other skills, agents, and session scheduled tasks from invoking the skill.
