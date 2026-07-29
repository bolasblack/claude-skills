# Authoring Guardrails

Use this reference when creating, editing, moving, retiring, or changing GRL entries and the guardrail router.

For rule file schema and enforcement metadata, read `<SKILL_PATH>/references/schema.md` first. For command semantics, read `<SKILL_PATH>/references/tooling.md`. For whether a convention should become a guardrail at all, read `<SKILL_PATH>/references/rule-change-workflow.md`.

## Identify the Target

- Router change: edit `.agents/guardrails/index.md`.
- Active rule change: edit exactly the relevant `.agents/guardrails/rules/GRL-<number>.md` files.
- New active rule: use the next available ID and create `.agents/guardrails/rules/GRL-<number>.md`.
- Retirement: move the rule to `.agents/guardrails/retired-rules/GRL-<number>.md` and add `retire_reason`.
- Tooling change: edit `<SKILL_PATH>/scripts/guardrails.ts` and cover the behavior in `<SKILL_PATH>/scripts/guardrails.test.ts` (`bun test` in that directory).

## Next ID

Find the next available ID:

```bash
bun <SKILL_PATH>/scripts/guardrails.ts next-id
```

`next-id` scans active and retired GRLs, prints max ID + 1, and does not create files.

## Rule Text

Keep each GRL focused. A GRL is an enforcement unit.

Choose the enforcement mode by the remediation story; the three modes and their selection criteria are defined in `<SKILL_PATH>/references/schema.md`.

### Writing `short`

Write `short` as the executable hard-rule summary shown by default render.

It should:

- be truthful, compact, and usually one sentence;
- state when the rule applies, the constrained target, and the required or prohibited behavior;
- include essential scope qualifiers that change implementation or review behavior;
- help the reader decide whether default render is enough or `render --detail` is needed.

If compliance depends on body-only carve-outs, examples, or interpretation, `short` may explicitly require `render --detail`. Still name the trigger or constrained target and why detail is required; do not write a bare "read detail" summary.

Good:

- `When adding a new external dependency, render detail before implementation; compliance depends on the duplicate-capability test and the vendored-code carve-out.`
- `Cross-module imports must go through the target module's entry file; render detail before importing from another module's internal directory.`
- `A module's public interface is defined by its entry file; render detail before adding or removing an export, because deprecation and ownership carve-outs apply.`

Bad:

- `Read detail for this rule.`
- `This rule is complicated; read detail.`
- `Route guidance.`

Do not put rationale, history, migration notes, long exception lists, or examples in `short`; put them in the Markdown body.

The Markdown body may be empty. Review-governed rules often need body detail, but that is reviewer judgment rather than a structural validation requirement.

## Router Rules

`.agents/guardrails/index.md` is routing only. It lists GRL IDs under task/scenario sections, in any readable Markdown format such as a table.

It should:

- list relevant `GRL-<number>` IDs for each task/scenario;
- avoid rule summaries, long detail, examples, skipped-rule prose, and retired-rule notes;
- avoid command examples with real GRL IDs;
- avoid mentioning skipped or retired GRL IDs anywhere, because every `GRL-<number>` token counts as listed.

Duplicate IDs are allowed when a rule is relevant to multiple tasks. Numeric ordering is not required. The order is human-curated reading order.

## Skip Index

Use `skip_index_reason` only for active pure lint rules that should not appear in the hot-path router.

The index-visibility invariants and the `skip_index_reason` / `lint_assist_reason` contracts are defined in `<SKILL_PATH>/references/schema.md`.

## Retirement

Retire by moving the rule file to `.agents/guardrails/retired-rules/` without changing its number. Add `retire_reason` and keep the normal rule schema.

Do not delete retired rules outright. Retiring by moving to `retired-rules/` preserves ID history and prevents accidental reuse without adding active hot-path context.

Retired rules must not appear in `.agents/guardrails/index.md` and cannot be rendered.

## Splitting and Merging

Split and merge are governed by one criterion, defined in `<SKILL_PATH>/references/schema.md`.

## Validation

After guardrail source changes, run structural validation:

```bash
bun <SKILL_PATH>/scripts/guardrails.ts validate
```

For what `validate` checks, see `<SKILL_PATH>/references/tooling.md`. It does not decide whether rule text, skip reasons, retirement reasons, or enforcement metadata are semantically sufficient.
