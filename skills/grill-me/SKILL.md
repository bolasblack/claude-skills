---
name: grill-me
description: Stress-test a plan, design, decision, or idea through a focused interview. Use when the user asks to be grilled, challenge their thinking, or resolve design choices before proceeding.
---

# Grill Me

Interview the user until the consequential decisions are clear enough to act on. Keep the interview within the user's goal and scope.

## 1. Establish the decision tree

Use the conversation to identify the goal, constraints, and decisions already settled. Map the remaining decisions and their dependencies: which answers must be known before another question can be usefully asked?

Look up facts in the available environment, code, and relevant documentation before asking the user. Respect existing project terminology and documented decisions. If a needed fact cannot be verified, make the uncertainty explicit and ask for missing information only when it affects the decision.

Begin questioning once you can identify the highest-impact open decision whose prerequisites are settled. Do not ask the user to repeat information already provided.

## 2. Interview one decision at a time

Ask one focused question, give your recommended answer with a brief reason, and wait for the user's response. Distinguish verified facts from your recommendation. Use concrete scenarios to expose ambiguous terms, trade-offs, or conflicting assumptions.

After each answer, update the decision tree. Resolve contradictions before moving to dependent decisions; leave questions whose prerequisites are still open for later. Revisit a settled decision only when new evidence or an answer changes its basis.

Continue until the decisions that materially affect the plan are resolved and any remaining uncertainties have an explicit disposition, such as an accepted assumption or a deferred experiment. Do not prolong the interview with hypothetical branches that would not change the plan.

## 3. Confirm shared understanding

Summarize the agreed direction, key constraints, and remaining assumptions or deferred questions. Let the user correct the summary and confirm it before acting on the plan. A clear instruction to proceed counts as confirmation; do not request it again.

The interview itself does not authorize implementation or documentation changes. After confirmation, carry out any next step already authorized by the user's request; otherwise finish with the agreed plan.
