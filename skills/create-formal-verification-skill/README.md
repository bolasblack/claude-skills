# create-formal-verification-skill

Generate a project-local skill that formally verifies the code where a bug costs the most and tests reach the least. It chooses the target from the code, lets the question choose the tool (TLA+ by default for event ordering, a code-level verifier or a prover where those fit), shows each property failing on a broken variant, and proves the generated skill by catching a scratch break in the real code before handing it over.

People and agents can both invoke it on every supported host. The description names only explicit requests, so ordinary discussion should not start it.

`maintain-formal-verification-skill` is the companion upkeep loop. Generated skills for TLA+ models read their results with `statechart` when it is installed; it is a separate skill, installed on its own.

## Source

Adapted from [Cursor's pstack `create-formal-verification-skill`](https://github.com/cursor/plugins/blob/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/create-formal-verification-skill/SKILL.md). Local adaptations:

- The generated skill's location names common project skill directories, because upstream relies on an adapter file this import does not include. Its frontmatter requirements are stated.
- `/statechart` is referenced by name instead of by a relative link that breaks when one skill is installed alone, and a generated skill falls back to the checker's own output where `/statechart` is not installed.
- Scratch breaks run in a temporary worktree or copy, so the user's checkout and uncommitted work stay untouched, and the proof step separates hand-written models from verifiers that run on the code.
- The agent asks before installing a tool and pins its version, and generated skills name secrets by environment variable.
- `disable-model-invocation: true` removed, so people and agents can invoke it on every host. OpenCode ignores the field, so explicit-only behavior could not hold everywhere.
- The description drops upstream's broad trigger clause, because the description now decides when agents start the skill.
- `license: MIT` added to the frontmatter.

The upstream MIT license and copyright notice are included in [LICENSE](LICENSE).
