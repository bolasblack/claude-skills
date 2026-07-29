# Reviewing Guardrails

Use this reference when reviewing a change to guardrail source files, retired rules, the guardrail router, or guardrail tooling.

For rule file schema and enforcement metadata, read `<SKILL_PATH>/references/schema.md` first. For command semantics, read `<SKILL_PATH>/references/tooling.md`. To audit an existing codebase against the guardrails rather than review one change, read `<SKILL_PATH>/references/auditing.md`.

## Review Metadata

Print changed guardrail review sections for reviewer judgment:

```bash
bun <SKILL_PATH>/scripts/guardrails.ts review-metadata --base <ref>
```

When `--base` is omitted, the base ref is resolved in this order: the `GUARDRAILS_BASE` environment variable, then `origin/HEAD` if the remote head is configured, then `HEAD`. The `--base=<ref>` form is also accepted. If the base ref does not exist the command fails with an actionable message instead of a raw git error. `review-metadata` requires git and requires the guardrails root to be the git repository root.

It detects changed active GRL files, retired GRL files, deleted active GRL files, and router changes relative to the base ref. Renaming or renumbering a rule reports the old path as a removal, because git rename detection is disabled; moving a rule into `retired-rules/` reports it as a retirement instead. It compares changed GRL metadata/text against the base ref when both sides can be parsed, then prints only the relevant reviewer instruction sections for categories such as enforcement, `skip_index_reason`, `lint_assist_reason`, `references`, `short`/body text, `retire_reason`, active rule removal, parse issues, and router changes. Each section lists every applicable file; there is no separate upfront changed-file list.

The instructions are prompts for manual review, not verdicts. Their prose is maintained in per-category files under `<SKILL_PATH>/references/review-metadata-instructions/`; missing, unknown, or malformed catalog entries make the command fail closed. The CLI owns category detection and file grouping. `review-metadata` is not a lint gate. It is a review helper because its output requires human judgment.

## Structural Validation

Run:

```bash
bun <SKILL_PATH>/scripts/guardrails.ts validate
```

For what `validate` checks, see `<SKILL_PATH>/references/tooling.md`.

## Manual Review Expectations

Reviewers still judge:

- whether `short` is truthful, compact, executable, and understandable without detail;
- whether `short` states when the rule applies, its target, and the required or prohibited behavior;
- whether detail and examples clarify the intended boundary without duplicating overlong summary prose;
- whether enforcement metadata truthfully chooses pure review, lint-assisted review, or pure lint based on the rule's remediation story;
- whether pure lint claims are mechanical, testable, scope-aware, self-contained, and fully diagnosable without pre-reading review guidance;
- whether `references` points to useful existing files or line ranges;
- whether `skip_index_reason` is justified for pure lint rules;
- whether `lint_assist_reason` explains what lint catches and what review still owns for lint-assisted review rules;
- whether `retire_reason` is justified;
- whether `.agents/guardrails/index.md` stayed compact and route-shaped;
- whether no skipped or retired GRL IDs are accidentally mentioned in the router.

## Router Review

Every `GRL-<number>` token in `.agents/guardrails/index.md` counts as listed. Check examples, prose, and notes as well as table cells.

The router should not include generated summaries, long detail, examples, skipped-rule prose, retired-rule notes, or command examples with real GRL IDs.

Duplicate IDs are allowed when a rule is relevant to multiple tasks. Numeric ordering is not required; routing order is human-curated reading order.

## Skip, Lint Assist, and Retirement Review

The validator checks that `skip_index_reason`, `lint_assist_reason`, and `retire_reason` exist when structurally required. It does not decide whether any reason is sufficient.

Judge each reason against its contract in `<SKILL_PATH>/references/schema.md`.

## Done Signal

A guardrail review should have:

- structural validation output;
- `review-metadata` output with relevant instruction sections and per-section file lists;
- manual judgment for changed rule text, metadata, skip reasons, lint-assist reasons, retire reasons, and router visibility.
