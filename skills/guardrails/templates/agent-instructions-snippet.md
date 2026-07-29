<!--
Paste the section below into this repository's agent instruction file
(CLAUDE.md, AGENTS.md, or equivalent). Replace every <INSTALLED_SKILL_PATH>
with the path where the guardrails skill is installed for this repository,
for example .claude/skills/guardrails. Delete this comment when you do.
-->

## Guardrails

Hard rules for this repository live in `.agents/guardrails/`.

- Read `.agents/guardrails/index.md` first, before writing or reviewing code.
- Take the rule IDs listed for your task and render only those:

  ```bash
  bun <INSTALLED_SKILL_PATH>/scripts/guardrails.ts render GRL-3 GRL-7
  bun <INSTALLED_SKILL_PATH>/scripts/guardrails.ts render --detail GRL-3
  ```

  `GRL-3` and `GRL-7` are examples; pass the IDs your task row listed. Escalate to `--detail` per rule, not per task: render detail when the rule's summary says to, or when your change touches that rule's target and the summary does not settle whether a carve-out applies.
- Do not open `.agents/guardrails/rules/*.md` directly for ordinary implementation context, and do not read the whole rules directory.
- Do not create, edit, or retire rule files, and do not edit `.agents/guardrails/index.md`, without loading the `guardrails` skill. It owns the frontmatter schema, the enforcement modes, the router invariants, and the retirement workflow.
- Structural problems are caught by `bun <INSTALLED_SKILL_PATH>/scripts/guardrails.ts validate`, which runs in this repository's lint gate. Whether a rule's text, reasons, or enforcement mode are adequate is a human judgment, never a tool's.
