# Troubleshooting

### Package or Validation Failure

1. Confirm the package contains `SKILL.md` at its expected root with exact casing.
2. Check YAML delimiters, indentation, value types, and the portable name constraints.
3. Use [Harness Research](../HARNESS-RESEARCH.md) to interpret the named surface's current
   diagnostic and validator behavior.

### Skill Doesn't Trigger

Quick checks:
- Is description too generic? ("Helps with projects" won't work)
- Does it include trigger phrases users would actually say?
- Does it mention relevant file types?

Run an actual activation case in a fresh session. A model repeating the description only proves that it can read the text.

### Skill Triggers Too Often

1. Be more specific: `"PDF legal documents for contract review"` not `"documents"`
2. Give each real branch one discriminating context pointer and remove synonym lists that add no distinction
3. Test the nearest competing skill or same-domain near-miss, then refine the positive boundary

### Instructions Not Followed

1. Reproduce the failure in a fresh session and identify the first skipped or misread branch.
2. Replace ambiguity such as "validate things properly" with an ordered action and observable completion criterion.
3. Co-locate the rule with the step it governs; move only lookup material into a reference with an explicit read condition.
4. Remove competing options, duplicate rules, and no-op encouragement that cannot change the decision path.

### Large Context Issues

Symptoms: Slow responses, degraded quality.

Solutions:
1. Apply the [Bounded Entry Point](../SKILL.md#bounded-entry-point): move one branch's workflow or lookup material out first, and keep standing rules in `SKILL.md`.
2. Measure recall on the actual target as skills are added; use the surface's currently documented cap instead of a generic count.
3. Ensure progressive disclosure is working and reference reads have explicit conditions.

### Skill Packs

If you have many related capabilities, consider grouping them into a **skill pack** — a single skill that bundles related functions together. This can reduce the number of simultaneously enabled skills and help the host select the right capability.

Consolidate only when coexistence evaluations show trigger conflicts or recall degradation and the combined skill preserves equal behavior. Shared domain or an arbitrary skill count alone is not enough.

### MCP Connection Issues

1. Use [Harness Research](../HARNESS-RESEARCH.md) to identify the named host's current connector or status diagnostic.
2. Check authentication (API keys valid, proper scopes)
3. Test MCP independently by asking the agent to call it without the skill
4. Verify tool names match MCP server documentation (case-sensitive)
