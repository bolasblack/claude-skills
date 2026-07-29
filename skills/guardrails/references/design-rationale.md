# Why the Framework Is Shaped This Way

Use this reference before proposing a change to the framework itself, or when an adopter asks why an obvious improvement is missing.

## The Objective

The framework exists to make a repository's hard rules explicit and traceable while keeping the default agent hot-path context near zero. Every structural decision below trades authoring convenience for hot-path cost, and resolves in favor of hot-path cost. An improvement that makes rules easier to write but puts rule text back in front of every task is not an improvement.

## Rejected Alternatives

### Put each rule's `short` into the router

The router grows back into a summary document and rule text returns to the hot path. The router stays purely structural; content is rendered on demand.

### Add a shorter `label` field for the router

Same failure with an extra field to maintain and keep truthful. A label shorter than `short` is either redundant or misleading, and the router still carries rule text.

### Generate a digest file

A digest is a second hot-path entrypoint competing with the router, and it drifts from the sources it summarizes. One router, plus on-demand render.

### Keep rules grouped in topic documents

Reading a group couples rule text, examples, and detail, so a task pays for rules it will never touch. Any granularity coarser than one rule per file recreates the original problem.

### One YAML file holding many rules, or YAML-only rules

YAML is poor for prose, examples, and review diffs, and multi-rule files destroy per-rule diffs, retirement, and rendering. Markdown plus frontmatter gets structured metadata and readable detail in the same file.

### Nested reference fields, bare document IDs, or globs in `references`

A flat array of real repo-relative paths is simpler and machine-verifiable. The path itself tells the reader what kind of document it is, and the validator can prove the file exists; a bare ID or glob can prove neither.

### A generated manifest as the integrity model

The manifest existed to protect block boundaries inside grouped documents. One rule per file removes that failure mode entirely. Fix the file layout instead of adding a checksum for a bad layout.

### Type checking or tests as enforcement metadata

Type and test diagnostics have no stable rule identity, usually cover only part of a guardrail, and produce coverage claims that only a reviewer can judge. Only a named lint diagnostic can remove a rule from the review hot path; everything else leaves the rule review-governed. This is the sharpest constraint in the framework, and the one adopters most often try to relax.

### Let `review-metadata` decide whether metadata is sufficient

The tool detects and groups; humans judge. This line is what keeps `skip_index_reason` and `lint_assist_reason` honest — a machine verdict on reason quality would be trivially gamed by writing whatever the machine accepts.

### Delete retired rules

Moving preserves ID history and prevents accidental number reuse without adding hot-path context. A deleted rule leaves a hole that someone eventually refills with a different rule under the same number.

### Require dense or zero-padded IDs

IDs are stable identities, not a dense index. Padding and continuity buy nothing and force renumbering pressure the framework explicitly forbids.

### Example paths as frontmatter fields

One rule per file already lets Good and Bad examples live in the body without polluting other rules. External example fixtures can be added later if examples ever become long or testable.

### Section or task-name rendering (`render --section`)

The router stays human-readable and agents copy IDs out of it. This one is a revisitable trade-off, not settled doctrine. The observed cost is real: without section rendering, an automated audit harness is tempted to transcribe router rows into its own code, and a transcribed list silently drifts from the router until the audit is reviewing a stale rule set. If you build such a harness, parse the router at run time rather than copying it.

## Adopter-Configurable, Not Doctrine

- Runtime: the shipped CLI uses Bun because it parses YAML and Markdown without adding a dependency. The transferable criterion is to pick a runtime the repository already has that parses YAML natively; do not hand-roll a YAML subset.
- Gate placement: the requirement is that structural breakage fails early in one place. Which command that is belongs to the repository.

## Consequences You Are Signing Up For

- Default agent guardrail cost is the router plus the selected `short` lines.
- Review-governed rules, including lint-assisted ones, are necessarily visible in the router and cannot hide behind `skip_index_reason`.
- A mechanical rule leaves the hot path only with an explicit, reviewer-audited `skip_index_reason`.
- Reviewers judge both reason fields with opposite burdens: `skip_index_reason` must justify removing hot-path reading entirely; `lint_assist_reason` must truthfully describe partial coverage and name what review still owns.
- Guardrail structure breaks at lint time, not at review time.
- The CLI runtime becomes a project dependency.
- The framework deliberately ships without external example fixtures and without section-based rendering.

## A Lesson From Deployment

Satellite process documents drift from the schema. In the source deployment, a procedure document still described a fourth enforcement mechanism that the schema had already dropped, and it kept telling authors to record it. Keep the schema enforced in code, keep prose about the schema in one place, and treat any second description of the schema as a defect to remove rather than a copy to update.
