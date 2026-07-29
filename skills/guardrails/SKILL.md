---
name: guardrails
description: "Rendered guardrail framework: keep a repo's hard rules in one-rule-per-file GRL sources behind a compact router, and render only the rules a task needs. Use when gathering guardrail context before implementing or reviewing code, when creating, editing, retiring, or reviewing GRL rule files or .agents/guardrails/index.md, when running the guardrails CLI (validate, render, review-metadata, next-id), or when setting up, adopting, or bootstrapping a guardrail framework in a repo that does not have one yet. Do NOT use for ordinary lint rule authoring unless the lint rule backs a guardrail, for runtime safety guardrails such as rate limiting, destructive-command protection, or input validation, for LLM or AI output guardrails, or for soft conventions and style preferences that are not hard rules."
compatibility: "Requires Bun (https://bun.sh) to run scripts/guardrails.ts. review-metadata additionally requires git."
---

# Guardrails

A repository accumulates hard rules that an agent must know before writing code. When those rules live in grouped topic documents, routing an agent to a group loads every rule's text, examples, and rationale at once, and burns a large share of the context window before any task code is read.

This framework keeps the default hot-path cost to one compact router file plus the one-line summaries of the IDs a task actually selected. Rule bodies, examples, and rationale stay on disk and are rendered on demand.

`<SKILL_PATH>` means the loaded base directory of this skill. Use it in skill documentation; use concrete installed paths only in repo-level executable files such as package scripts, Makefile targets, git hooks, or CI config.

## What the Framework Owns

- `.agents/guardrails/index.md` — compact routing document that lists GRL IDs per task or scenario. Read first, read whole.
- `.agents/guardrails/rules/GRL-<number>.md` — active one-rule-per-file sources. Never opened directly for ordinary implementation context.
- `.agents/guardrails/retired-rules/GRL-<number>.md` — retired sources, kept for ID history.
- `<SKILL_PATH>/scripts/guardrails.ts` — Bun CLI for validation, rendering, review metadata, and next-id lookup.

These paths and the `GRL-` ID prefix are fixed by the CLI and are not configurable.

## Requirements

- Bun on PATH (https://bun.sh).
- git, for `review-metadata`.
- Commands run from anywhere inside the repository; the CLI resolves the repository root itself.

## Pick the Workflow

- Consuming guardrails for implementation or code review context: read `references/consuming.md`.
- Creating, editing, moving, or retiring GRLs, or changing the router: read `references/authoring.md` and `references/schema.md`.
- Reviewing guardrail source changes: read `references/reviewing.md` and `references/schema.md`.
- Auditing an existing codebase against the guardrails, rather than reviewing one change: read `references/auditing.md`.
- Running or documenting CLI commands: read `references/tooling.md`.
- Setting up the framework in a repo that has no `.agents/guardrails/` yet, or wiring `validate` into a lint or CI gate: read `references/adoption.md`.
- Deciding whether a convention should become a guardrail at all, and moving it through decision, guardrail, and lint stages: read `references/rule-change-workflow.md`.
- Understanding why the framework is shaped this way, or proposing a change to the framework itself: read `references/design-rationale.md`.
- Changing the CLI or validation/render behavior: read `references/tooling.md`, `references/schema.md`, and inspect `<SKILL_PATH>/scripts/guardrails.ts`.

## Common Commands

```bash
bun <SKILL_PATH>/scripts/guardrails.ts validate
bun <SKILL_PATH>/scripts/guardrails.ts render GRL-<id1> GRL-<id2>
bun <SKILL_PATH>/scripts/guardrails.ts render --detail GRL-<id1> GRL-<id2>
bun <SKILL_PATH>/scripts/guardrails.ts review-metadata --base <ref>
bun <SKILL_PATH>/scripts/guardrails.ts next-id
```

`validate` is structural; wire it into your repo's lint or CI gate (see `references/adoption.md`). `render` is the normal way to assemble selected guardrail context. `review-metadata` lists changed active/retired GRL files and router changes with grouped reviewer instructions; it is a review helper, not a lint gate. Without `--base`, `review-metadata` uses `GUARDRAILS_BASE`, then `origin/HEAD`, then `HEAD`.

## Key Rules

- Read `.agents/guardrails/index.md` first when consuming guardrails for ordinary implementation.
- Render selected GRL IDs instead of opening every rule file directly.
- Keep `.agents/guardrails/index.md` compact and route-shaped; every `GRL-<number>` token anywhere in that file counts as listed, including prose, notes, and examples.
- Keep one GRL number in exactly one active or retired source file; never reuse or renumber.
- Keep required guardrail metadata schema-shaped; extra frontmatter fields are allowed but ignored by the CLI. See `references/schema.md`.
- Pick the enforcement mode and honor the index-visibility invariants and the `skip_index_reason` / `lint_assist_reason` contracts defined in `references/schema.md`; do not restate them elsewhere.
- Retired rules live under `.agents/guardrails/retired-rules/` and require `retire_reason`; retire by moving the file, never by deleting it.
- When changing `scripts/*`, update and run the skill-local tests with `bun test` in `<SKILL_PATH>/scripts`.

## Done Checklist

Before finishing guardrail source work, confirm:

- Active GRLs live under `.agents/guardrails/rules/`.
- Retired GRLs, if any, live under `.agents/guardrails/retired-rules/` with `retire_reason`.
- `index.md` stayed compact and route-shaped.
- GRL numbers remain stable and unique.
- Enforcement metadata matches the real enforcement model.
- `validate` passes.
- `review-metadata` was run when GRL files changed.

## Version History

- v1.1.0 (2026-07-29): Consolidated enforcement doctrine into `references/schema.md` and CLI semantics into `references/tooling.md`, with pointers replacing the duplicated passages; routed the existing-codebase audit workflow to `references/auditing.md`; added a troubleshooting section to `references/tooling.md`; `render --detail` is accepted in any argument position; hardened the skill-local test suite.
- v1.0.0 (2026-07-29): Initial public release of the rendered guardrail framework skill.
