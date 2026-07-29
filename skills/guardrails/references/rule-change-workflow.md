# Rule Change Workflow

Use this reference when deciding whether a convention should become a guardrail, and when moving a rule through decision, guardrail, and lint stages.

## When This Applies

- Adding or changing a hard boundary such as an import policy or a dependency direction.
- Adding or changing a guardrail.
- Promoting an existing convention into enforcement.
- Defining directory carve-outs.

## Gate: Practice or Guardrail

If the rule is a recommendation that a reviewer may reasonably override, it is a practice note and does not enter this workflow. A guardrail is a hard rule; making something a guardrail means agreeing that violations block. Decide which one you are writing before you write anything, because the two have different costs: a practice note that turns out to be wrong is edited, a guardrail that turns out to be wrong has already blocked work.

## Principles

1. Discuss the rule before writing any enforcement.
2. Decision, then guardrail, then lint — in that order.
3. Keep the code migration workstream separate from the enforcement workstream.
4. Discuss every exception explicitly; never smuggle an exception into the lint implementation.
5. The implementer does not self-accept the enforcement change.

## Step 1: Interrogate the Carve-Outs

Answer all of these before writing any rule text:

- What is the main rule?
- Which directories are the normal path?
- Which directories are exceptions, and why?
- Does the rule differ for runtime imports versus type-only imports?
- What about test and fixture directories?
- What is in scope now, and what is deferred?
- Which part will be lint-enforced, and which part stays review-governed?

Unanswered carve-outs turn into lint escape hatches later. An exception discovered during implementation is an exception nobody agreed to.

## Step 2: Record the Decision

Update the decision document that already owns the boundary. Do not mint a new decision document whose only purpose is to justify a lint rule; that separates the rationale from the boundary it governs.

The update must state:

- the default rule;
- the exception;
- why the exception is valid;
- where the exception stops.

If the repository has no decision-record system, the guardrail's Markdown body and its `references` carry that rationale instead, and this step collapses into writing the body. The four items above are still required — only their location changes.

## Step 3: Write the Guardrail

Create or edit the GRL per `<SKILL_PATH>/references/authoring.md` and `<SKILL_PATH>/references/schema.md`. Choose the enforcement mode by the remediation story.

The enforcement modes, what does and does not count as enforcement metadata, and the selection criteria are defined in `<SKILL_PATH>/references/schema.md`.

## Step 4: Implement Lint, If Any

This step applies only to lint-assisted and pure-lint rules.

The diagnostic must name the whole remediation story, not the symptom it happened to detect. A message that reports what was found but not what the author should do instead pushes the reader back into the hot path, which is the cost the rule was supposed to avoid.

Keep the migration of existing violating code in a separate workstream from landing the enforcement, so a failing gate never forces a rushed rule change.

## Step 5: Validate and Review

```bash
bun <SKILL_PATH>/scripts/guardrails.ts validate
bun <SKILL_PATH>/scripts/guardrails.ts review-metadata --base <ref>
```

Then apply `<SKILL_PATH>/references/reviewing.md`.

## Step 6: Triage Failures

When the work fails, classify the failure before changing anything:

- The rule is not settled — the reviewer and the implementer disagree about what the rule means, or the carve-outs contradict each other. Stop and re-discuss the rule. Do not patch the lint.
- The implementation is incomplete — migration is unfinished or the diagnostic does not yet cover what the rule claims. Finish the enforcement; the rule stands.
- The reviewer or environment disagrees with the rule as written. Resolve the disagreement at the decision level before changing the enforcement.

The failure mode this ordering prevents is editing a rule to match a broken implementation.

## Checklist

- Carve-outs answered.
- Rationale recorded where the repository records rationale.
- GRL written with an honest enforcement mode.
- Lint implemented if the rule claims lint.
- Migration tracked separately from enforcement.
- `validate` passing.
- A second person accepted the enforcement change.
