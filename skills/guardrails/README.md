# Guardrails

A rendered guardrail framework for bounded agent context. It keeps your repository's hard rules ("guardrails") in one-rule-per-file GRL sources behind a compact router, and renders only the rules a task actually needs.

## Why

A repository accumulates hard rules an agent must know before writing code. When those rules live in grouped topic documents, routing an agent to a group loads every rule's text, examples, and rationale at once — burning a large share of the context window before any task code is read.

With this framework, the default cost of "know the guardrails" is one compact router file plus one-line summaries of the rules a task selected. Rule bodies, examples, and rationale stay on disk and are rendered on demand.

## How It Works

Guardrails live under `.agents/guardrails/` in your repository:

- `index.md` — a compact router listing GRL IDs per task or scenario.
- `rules/GRL-<number>.md` — one rule per file: structured metadata plus a Markdown body with examples and rationale.
- `retired-rules/GRL-<number>.md` — retired rules, kept so GRL numbers are never reused and history stays traceable.

Before a task, the agent reads the router, picks the relevant IDs, and renders exactly those rules. Each rule declares how it is enforced — by code review, by a named lint diagnostic, or by lint-assisted review — so it is always clear who catches a violation.

## What the Skill Can Do

- **Gather guardrail context** — before implementing or reviewing code, select and render just the rules that apply to the task.
- **Author rules** — create, edit, or retire guardrails and keep the router up to date, with a schema that ties every rule to a real enforcement story.
- **Review guardrail changes** — generate grouped reviewer instructions for changed rules and router edits, so guardrail edits get judged, not rubber-stamped.
- **Audit a codebase** — check existing code against the active guardrails, not just a single change.
- **Bootstrap a repo** — set up `.agents/guardrails/` from templates in a repository that has no guardrails yet, and wire validation into the lint or CI gate.
- **Keep the structure sound** — a bundled CLI (`validate`, `render`, `review-metadata`, `next-id`) enforces the file layout, schema, and router coverage mechanically.

## Requirements

[Bun](https://bun.sh) to run the bundled CLI, and git for review metadata. Commands work from any subdirectory of the repository.

## Works Well With

The [agent-centric](../agent-centric/) skill's AGD decision records are the natural companion: an AGD records *why* a decision was made, and a guardrail encodes the hard rule that decision produced. The rule-change workflow here ("decision, then guardrail, then lint") assumes a decision-record system — AGD fills that role, and a guardrail's `references` field can point at the AGD that motivated it. Both frameworks live side by side under `.agents/`.

## Scope

Use this skill for hard rules that gate code review. It is not for soft conventions or style preferences, runtime safety guardrails (rate limiting, input validation, destructive-command protection), or LLM output guardrails.
