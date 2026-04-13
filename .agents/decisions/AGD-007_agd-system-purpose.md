---
title: "AGD System Purpose"
description: "AGD exists to preserve a stable, growing history of project decisions for traceability and reevaluation"
tags: skills/agent-centric
related: AGD-003, AGD-006
---

## Context

We needed to state the core purpose of the AGD system itself, not just its file format or relationship semantics.

The project needs a stable way to record why important decisions were made, especially decisions that explain why code is implemented in a particular way. Those reasons should not disappear when code evolves, teams change, or local context is forgotten.

When revisiting an area later, we want to quickly answer questions such as:

- Why was this implemented this way at the time?
- What constraints or trade-offs led to that choice?
- Has this decision been updated or replaced since then?
- Should we redo this now, or keep it for the moment?

## Decision

Treat AGD as a system for building a **persistent, growing history of project decisions** with stable references.

More specifically:

1. Every important decision should have a stable AGD reference that can be cited from code, docs, and future discussions.
2. Decision records are archival and should not disappear simply because the code changed.
3. New AGDs should extend decision history rather than erase it.
4. The system should make it easy to trace from a current implementation back to its original rationale.
5. The system should also make it easy to see whether a decision still stands, has been updated, or has been replaced.
6. The purpose of AGD is not only documentation, but also support for future reevaluation: whether to preserve existing work or redesign it.

Terminology note:

- "Decision history tree" is a useful intuition.
- But structurally AGD is more accurately a **decision history graph**, because relationships such as `updates`, `obsoletes`, and `related` can create non-tree connections.

## Consequences

**Benefits:**
- Gives the project durable memory instead of relying on tribal knowledge
- Makes implementation rationale discoverable long after the original discussion is gone
- Supports safer refactoring and redesign by exposing whether current code follows an active, updated, or obsolete decision
- Encourages citing stable decision refs in code and documentation

**Trade-offs:**
- Writing AGDs adds overhead at decision time
- A growing decision history requires discipline in naming, linking, and searching
- If relationships are not maintained well, the history becomes harder to navigate
