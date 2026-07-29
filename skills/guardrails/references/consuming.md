# Consuming Guardrails

Use this reference when guardrails are needed for ordinary implementation or code review context.

## Workflow

1. Read `.agents/guardrails/index.md` first.
2. Pick the GRL IDs relevant to the task.
3. Render only those IDs with `bun <SKILL_PATH>/scripts/guardrails.ts render`.
4. Render with `--detail` when the rule's `short` directs it, or when your change touches that rule's constrained target and `short` alone does not tell you whether a carve-out applies. Otherwise the summary is enough.

Do not open every rule file directly for ordinary implementation context.

## Router Input

`.agents/guardrails/index.md` supplies IDs. It is a routing map, not a catalog and not a rule summary.

The order of IDs in the router is human-curated reading order, not numeric order. Preserve the task-relevant order when passing IDs to `render`.

## Commands

```bash
bun <SKILL_PATH>/scripts/guardrails.ts render GRL-<id1> GRL-<id2>
bun <SKILL_PATH>/scripts/guardrails.ts render --detail GRL-<id1> GRL-<id2>
```

Argument rules, ID handling, and exactly what each rendering mode prints are documented in `<SKILL_PATH>/references/tooling.md`.

## Cost Model

The default guardrail cost of a task is one router file plus the `short` line of each ID you selected. Opening rule files directly, or rendering every ID in the router, throws that away.

Escalate to `--detail` per rule, not per task, and only on the two triggers above: the rule's `short` says to, or `short` alone does not settle whether a carve-out applies to your change. A task that renders detail for every selected ID has paid for the whole rule set again.
