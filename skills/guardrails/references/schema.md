# Guardrail Schema

Use this reference when creating, editing, retiring, validating, or reviewing GRL files.

## Source Layout

```text
.agents/guardrails/index.md
.agents/guardrails/rules/GRL-<number>.md
.agents/guardrails/retired-rules/GRL-<number>.md
<SKILL_PATH>/scripts/guardrails.ts
```

`<SKILL_PATH>` means the loaded base directory of this skill. Use it in skill documentation. Use concrete installed paths only in repo-level executable files such as package scripts, Makefile targets, git hooks, or CI config. The three `.agents/guardrails` paths and the `GRL-` prefix are fixed by the CLI and are not configurable.

GRL numbers are stable identities. Moving or retiring a GRL must not change its number. One GRL number has exactly one source file across active and retired directories.

Active GRL filenames are exactly the GRL ID plus `.md`, such as `GRL-1.md`. Do not add a slug. This keeps lookup mechanical: `GRL-1` maps to `.agents/guardrails/rules/GRL-1.md` when active.

## Active Rule File

Active rule files live under `.agents/guardrails/rules/` and use YAML frontmatter plus optional Markdown body:

```md
---
number: GRL-1
short: A module's public interface is defined by its entry file; other modules import only from that entry file.
enforcement:
  review: true
  lint: []
references:
  - docs/architecture/module-boundaries.md
---

Optional detail, examples, and rule-defining prose.
```

Example paths in this document are illustrative. `validate` requires every `references` entry to point at a file that actually exists in your repository, so copy the shape, not the paths.

The guardrails CLI consumes the required and optional fields below. Extra frontmatter fields are allowed so other scripts can attach metadata, but the guardrails CLI ignores them.

Required active fields:

- `number`: non-empty string matching the filename.
- `short`: executable hard-rule summary shown by default render. It must be understandable without body detail, state when the rule applies, name the target, and say the required or prohibited behavior.
- `enforcement.review`: boolean.
- `enforcement.lint`: array of non-empty strings.

Optional active fields:

- `references`: array of real repo-root relative file paths, optionally with `:N` or `:N-M` line suffixes.
- `skip_index_reason`: non-empty string for pure lint rules that should not appear in the hot-path index.
- `lint_assist_reason`: non-empty string for lint-assisted review rules. It should say what lint catches and what review still owns; the validator only checks that it is a non-empty string when structurally required.

## Short Text

`short` is the default-render contract: a compact, executable hard-rule summary that tells a reader whether the rule applies and whether detail should be rendered. It must be understandable without body detail, state when the rule applies, name the target, and say the required or prohibited behavior.

Keep schema guidance to field meaning and shape. Put authoring tactics in `<SKILL_PATH>/references/authoring.md` and reviewer judgment in `<SKILL_PATH>/references/reviewing.md`.

The Markdown body may be empty. When present, it contains rationale, edge cases, examples, and other rule-defining prose. Keep Good/Bad examples in the body rather than adding separate example-path frontmatter fields.

Review-governed rules often need body detail, but that is reviewer judgment rather than a structural validation requirement.

## Retired Rule File

Retired rule files live under `.agents/guardrails/retired-rules/`. They use the same schema as active rule files and also require:

- `retire_reason`: non-empty string explaining why the rule is retired.

The directory determines retired status. Do not add a separate `retired: true` field.

Active and retired directories must not contain the same GRL number. Retired rules do not participate in index coverage, must not appear in `.agents/guardrails/index.md`, and cannot be rendered as active guardrails.

Retired rule body and metadata remain available for history and reviewer context.

## Enforcement Metadata

A GRL is an enforcement unit. The guardrail metadata recognizes only review and lint enforcement modes.

This section is the single source of truth for enforcement-mode selection, index visibility, the split/merge criterion, and the reason-field contracts. Other references in this skill point here instead of restating them.

Valid enforcement shapes:

Pure review:

```yaml
enforcement:
  review: true
  lint: []
```

Lint-assisted review:

```yaml
enforcement:
  review: true
  lint:
    - lint/no-cross-module-import
lint_assist_reason: lint/no-cross-module-import catches direct imports into another module's internal directory; review still owns whether the needed capability belongs in that module's public interface or in a shared module.
```

Pure lint:

```yaml
enforcement:
  review: false
  lint:
    - lint/no-test-import-in-runtime
skip_index_reason: lint/no-test-import-in-runtime names the offending import and the fix is always to move the helper out of the test directory, so no hot-path reading is required.
```

Invalid enforcement shape:

```yaml
enforcement:
  review: false
  lint: []
```

### Index Visibility Invariants

For active GRLs:

- Pure review rule: `review: true`, `lint: []`; must appear in `.agents/guardrails/index.md`, must not have `skip_index_reason`, and must not have `lint_assist_reason`.
- Lint-assisted review rule: `review: true`, non-empty `lint`; must appear in `.agents/guardrails/index.md`, must not have `skip_index_reason`, and must have non-empty `lint_assist_reason`.
- Pure lint rule: `review: false`, non-empty `lint`; must not appear in `.agents/guardrails/index.md`, must have non-empty `skip_index_reason`, and must not have `lint_assist_reason`.
- Invalid rule: `review: false`, `lint: []` has no enforcement mechanism and is rejected.

### Choosing the Mode

Choose by the remediation story:

- Pure lint: the diagnostic explains the complete rule well enough to fix it without pre-reading broader review guidance; the rule is mechanical, testable, scope-aware, and self-contained.
- Lint-assisted review: lint catches a mechanical failure mode of a broader rule, but remediation still needs review context, architecture judgment, exception judgment, or semantic ownership decisions. The lint message should point at the complete remediation story, not only the symptom it detected.
- Pure review: there is no reliable useful lint signal, lint would be noisy, or compliance depends on design, product, ownership, type/runtime, or product-graph judgment that is not accepted as skip backing.

### Splitting and Merging

Split one GRL into two only when the mechanical and review parts have independent remediation stories. Do not split merely because lint catches one symptom of a broader rule.

Merge under the same criterion: when two GRLs restate one remediation story on one target, fold the narrower rule into the broader one and retire the narrower ID with a `retire_reason` that names the absorbing rule and the shared remediation story.

### Reason Field Contracts

- `skip_index_reason` must say why lint fully replaces hot-path reading. It is valid only on active pure lint rules.
- `lint_assist_reason` must say what lint catches and what review still owns.
- `retire_reason` must preserve enough history to explain why the ID no longer appears in the active router.

The validator only checks that each reason is a non-empty string when structurally required; it does not judge the prose. A guardrails reviewer decides whether a reason is sufficient.

## Why Only Review and Lint

The schema recognizes exactly two enforcement mechanisms. Type checkers, tests, and code review habit are not accepted as enforcement metadata: a type or test diagnostic has no stable rule identity, usually covers only part of a guardrail, and needs a reviewer's judgment about how much it covers. Accepting them would make removing a rule from the hot path depend on a claim no validator can check. Only a named lint diagnostic can buy a `skip_index_reason`. See `<SKILL_PATH>/references/design-rationale.md`.

## References Metadata

`references` is a flat array of paths:

```yaml
references:
  - docs/architecture/module-boundaries.md
  - .agents/guardrails/index.md:1-20
```

Do not encode references as nested fields such as `references.kind` or `references.type`. Do not use bare document IDs. Do not use globs.

`references` entries must be real repo-root relative paths. A reference may add a line suffix:

- `path/to/file.md:N` for one line.
- `path/to/file.md:N-M` for an inclusive line range.

Line numbers are 1-based positive integers. Ranges must be ordered (`N <= M`).

The validator checks that the referenced file path exists, does not escape the repository, and that any line range is valid for the target file.

Prefer precise, useful references. Use line ranges when the rule depends on a specific section rather than an entire file. A reviewer may judge whether a path or line range points close enough to the rule's source of truth.
