# create-verification-skill

Generate a project-local `verify-<app>` skill that drives the real application the way a user does: launch it, health-check it, exercise a feature through its real UI, CLI, or API surface, capture evidence, and clean up. The generator interviews the repository rather than the user, seeds a feature map (one file per user-facing feature), and proves the generated skill by running it end to end once before handing it over.

Works for any language, framework, or platform. The skill lands in `.claude/skills/verify-<app>/` (or the project skill directory the current host reads). Its feature map lives in project documentation, using the existing map or `docs/features/` by default. This lets feature investigation, test planning and verification share the same project knowledge. `maintain-verification-skill` is the companion upkeep loop that keeps the map honest as the app changes.

People and agents can both invoke it on every supported host. The description names only explicit requests, so ordinary discussion should not start it.

## Source

Adapted from [Cursor's pstack `create-verification-skill`](https://github.com/cursor/plugins/tree/ae5650febf4320793844c12c4adaa937f417f8da/pstack/skills/create-verification-skill). Local adaptations:

- Output path retargeted from `.cursor/skills/verify-<app>/` to `.claude/skills/verify-<app>/`, with a note for hosts that read `.agents/skills/`.
- Feature maps are project documents reached through a conditional pointer from the generated skill.
- The Launch section requires naming env vars and their source instead of copying secret values or `.env` contents into the generated skill.
- The Evidence section requires a gitignored or out-of-repo artifact location; evidence is never committed.
- The description trigger reads "make a verification skill for this repo" instead of upstream's "control skill" vocabulary.
- `disable-model-invocation: true` removed, so people and agents can invoke it on every host. OpenCode ignores the field, so explicit-only behavior could not hold everywhere.
- The description drops upstream's broad trigger clause, because the description now decides when agents start the skill.
- `license: MIT` added to the frontmatter.

The upstream MIT license and copyright notice are included in [LICENSE](LICENSE).
