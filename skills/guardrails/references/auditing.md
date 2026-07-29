# Auditing an Existing Codebase

Use this reference when auditing a whole codebase against the guardrails, rather than reviewing a single change. For reviewing one change, read `<SKILL_PATH>/references/reviewing.md`.

## Five Phases

1. Inventory: measure the tree and split it into balanced file chunks; do not let one reviewer hold the whole repo.
2. Review: run one reviewer per dimension over each chunk. Each reviewer loads context in a fixed order: the governing design or architecture documents, then `render` for exactly the GRL IDs assigned to that dimension, then whatever project config is needed to interpret the code (path aliases, module map).
3. Verify: re-judge each finding with a skeptic whose default stance is that the finding is wrong. Batch findings by cited rule so the rule is rendered once and each finding is judged independently. An unresolved verdict escalates to a tiebreaker that is not allowed to stay unresolved.
4. Gaps: ask a completeness critic what was not swept, then run bounded follow-up sweeps.
5. Synthesize: one report, findings consolidated as one entry per rule and pattern listing all affected files.

## Two Rules That Make It Work

- Before citing a GRL in a finding, run `render --detail` for that ID and confirm the exact scope and carve-outs. A finding that misquotes a rule's scope costs more than the finding is worth.
- Do not copy router rows into the audit harness. Read `.agents/guardrails/index.md` at run time and take the IDs from there. A transcribed ID list silently drifts from the router and the audit then reviews a stale rule set.

## Reviewer Contract

Every reviewer is read-only. Findings carry the rule ID, the affected paths, evidence, and an explicit confidence and coverage statement so the reader can tell reviewed-and-clean from not-reviewed.
