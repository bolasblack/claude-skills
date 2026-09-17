# create-verification-skill

Generate a project-local `verify-<app>` skill that drives the real application the way a user does: launch it, health-check it, exercise a feature through its real UI, CLI, or API surface, capture evidence, and clean up. The generator interviews the repository rather than the user, seeds a feature map (one file per user-facing feature), and proves the generated skill by running it end to end once before handing it over.

Works for any language, framework, or platform. The output lands in `.claude/skills/verify-<app>/` (or the project skill directory the current host reads) alongside a `features/` map. `maintain-verification-skill` is the companion upkeep loop that keeps the map honest as the app changes.

Invoke it explicitly with `/create-verification-skill`. The frontmatter sets `disable-model-invocation: true`, which Claude Code and pi honor, so those hosts never trigger it on their own. OpenCode ignores the field, and Codex controls implicit invocation through its own `agents/openai.yaml` instead.

## Source

Adapted from [Cursor's pstack `create-verification-skill`](https://github.com/cursor/plugins/tree/e31650eea443aaea1e84cc15d88c13f40080b275/pstack/skills/create-verification-skill). Local adaptations:

- Output path retargeted from `.cursor/skills/verify-<app>/` to `.claude/skills/verify-<app>/`, with a note for hosts that read `.agents/skills/`.
- The Launch section requires naming env vars and their source instead of copying secret values or `.env` contents into the generated skill.
- The Evidence section requires a gitignored or out-of-repo artifact location; evidence is never committed.
- The description trigger reads "make a verification skill for this repo" instead of upstream's "control skill" vocabulary.
- `license: MIT` added to the frontmatter.

The upstream MIT license and copyright notice are included in [LICENSE](LICENSE).
