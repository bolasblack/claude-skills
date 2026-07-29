# Adopting Guardrails

Use this reference when a repository has no `.agents/guardrails/` yet, or when wiring `validate` into a lint or CI gate.

## Prerequisites

- Bun on PATH (https://bun.sh). Verify with `bun --version`.
- git, if `review-metadata` will be used.
- The skill installed and readable at `<SKILL_PATH>`.

## 1. Create the Layout

Run from the repository root:

```bash
mkdir -p .agents/guardrails/rules .agents/guardrails/retired-rules
cp <SKILL_PATH>/templates/index.md .agents/guardrails/index.md
cp <SKILL_PATH>/templates/rules/GRL-1.md <SKILL_PATH>/templates/rules/GRL-2.md <SKILL_PATH>/templates/rules/GRL-3.md .agents/guardrails/rules/
bun <SKILL_PATH>/scripts/guardrails.ts validate
```

`validate` must print `Guardrail validation OK.` before you go further. If it does not, fix the layout before writing any rule.

These three paths are fixed by the CLI. Do not rename `.agents/guardrails/`, `rules/`, or `retired-rules/`, and do not change the `GRL-` prefix.

## 2. Replace the Example Rules

`templates/rules/GRL-1.md`, `GRL-2.md`, and `GRL-3.md` are seeds. They exist to demonstrate the three enforcement modes — pure review, lint-assisted review, and pure lint — and to give `validate` something to check. They are not rules to keep.

Either rewrite them as real rules for the repository, or delete them:

- Deleting `GRL-1.md` or `GRL-2.md` also requires removing their IDs from `.agents/guardrails/index.md`, because the validator checks index coverage in both directions.
- Deleting `GRL-3.md` changes nothing else, because pure-lint rules are never listed in the router.

Deleting seed rules before any real rule exists is the one case where deleting instead of retiring is correct. Once a rule has governed real code, retire it by moving it to `retired-rules/` instead.

## 3. Write the First Real Rule

Find the next free ID:

```bash
bun <SKILL_PATH>/scripts/guardrails.ts next-id
```

Then:

1. Create `.agents/guardrails/rules/GRL-<n>.md` following `<SKILL_PATH>/references/schema.md`.
2. Choose the enforcement mode by the remediation story, per `<SKILL_PATH>/references/authoring.md`.
3. Add the ID to the relevant router rows if the rule is review-governed. Pure-lint rules stay out of the router and carry `skip_index_reason` instead.
4. Run `validate`.

## 4. Wire validate Into a Gate

`validate` is structural and cheap. It belongs in whatever single command the repository already runs before merge, so guardrail breakage surfaces at gate time rather than at review time. Four common shapes, all runtime-neutral:

A package script, then chained into the repository's existing `lint` script so there is still one lint entrypoint:

```json
{
  "scripts": {
    "lint:guardrails": "bun .claude/skills/guardrails/scripts/guardrails.ts validate"
  }
}
```

A Makefile target:

```make
lint-guardrails:
	bun .claude/skills/guardrails/scripts/guardrails.ts validate
```

A `pre-commit` or `pre-push` git hook:

```bash
#!/bin/sh
bun .claude/skills/guardrails/scripts/guardrails.ts validate || exit 1
```

A CI step that invokes the repository's own lint command, which now includes guardrail validation.

In every example above the path depends on where the skill is installed: `.claude/skills/guardrails/`, `.agents/skills/guardrails/`, `~/.claude/skills/guardrails/`, or a vendored copy. Substitute the real location.

A skill installed under the user's home directory is not available to CI or to other contributors. If `validate` runs in CI, commit the skill into the repository — for example under `.claude/skills/guardrails/` or `.agents/skills/guardrails/` — and point the gate at the committed copy, or add an equivalent install step to the CI job.

Do not put `review-metadata` in the gate. Its output requires human judgment; it is a review helper, not a check.

## 5. Tell Agents to Use the Router

Paste `<SKILL_PATH>/templates/agent-instructions-snippet.md` into the repository's agent instruction file — `CLAUDE.md`, `AGENTS.md`, or whatever the repository uses. Then:

- Replace every `<INSTALLED_SKILL_PATH>` placeholder in the pasted commands with the path where the skill is installed for this repository, for example `.claude/skills/guardrails`. An agent instruction file is repo-level executable context, so it carries a concrete path rather than `<SKILL_PATH>`.
- Leave the example GRL IDs in the commands as they are. They illustrate the invocation shape; an agent substitutes the IDs its task row actually listed. The router itself must still carry no command examples with real IDs.
- Delete the leading HTML comment.

Without this step the framework still validates, but nothing routes agents to the router first. Agents keep reading whatever they used to read, and the context savings never materialize. Adoption is not complete until an agent starting a task reads `.agents/guardrails/index.md` before it reads code.

## 6. Review Loop

When a change touches guardrail sources, run:

```bash
bun <SKILL_PATH>/scripts/guardrails.ts review-metadata --base <ref>
```

The base ref resolves in this order: `--base <ref>` or `--base=<ref>`, then the `GUARDRAILS_BASE` environment variable, then `origin/HEAD`, then `HEAD`.

A repository whose trunk is not `main` should either pass `--base` explicitly or set `GUARDRAILS_BASE` in the review command it documents, so reviewers do not silently diff against `HEAD` and see nothing.

Then apply `<SKILL_PATH>/references/reviewing.md`.

## Migrating From Grouped Rule Documents

If the repository already keeps rules grouped into topic documents:

- Split them one rule per file. Any granularity coarser than one rule per file recreates the problem the framework exists to solve.
- Assign each rule a new sequential ID with `next-id`, and never renumber afterwards. Old in-document numbering is not an identity you have to preserve.
- Write each rule's `short` as the executable one-sentence contract. If a paragraph cannot be reduced to one, it is probably two rules.
- Build `index.md` by task or scenario, not by topic. The router answers "I am about to do X, what must I know", not "what rules exist about Y".
- Set enforcement per rule and let that decide router visibility. Do not carry over a topic document's visibility habits.
- Delete the old grouped documents only after `validate` passes on the new sources.
- Do not create retired rules for content that was never a GRL. `retired-rules/` records the history of IDs this framework issued, not the history of the old documents.

## Sizing Expectations

For calibration, one production deployment of this framework runs roughly 120 active rules routed by a router of about 75 lines holding about 20 task rows. Of those rules, about 80 percent are pure review, about 8 percent are lint-assisted review, and about 12 percent are pure lint. Roughly 9 in 10 rules carry a Markdown body.

Read that distribution as the expected shape. Review-only rules with example-bearing bodies are the normal case. Lint-backed removal from the hot path is the rare, audited exception, not the goal to optimize toward.
