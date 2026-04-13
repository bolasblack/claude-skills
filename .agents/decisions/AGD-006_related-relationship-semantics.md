---
title: "Related Relationship Semantics"
description: "Add related as a reference-only AGD relationship using RFC-style see-also semantics"
tags: skills/agent-centric
updates: AGD-003
---

## Context

We wanted to add a new `related` field to AGD frontmatter, but first needed to decide what semantic role it should play.

RFCs distinguish between relationships that change the status of an earlier document (`updates`, `obsoletes`) and relationships that are only helpful cross-references (`see-also`). We wanted AGD to follow that model rather than invent an ambiguous third kind of status-changing relationship.

We also needed to decide whether `related` should be reverse-synced into the target AGD's frontmatter.

## Decision

Adopt the RFC archival model for AGD relationships:

- `updates`: extends or modifies an earlier decision; the earlier decision remains partially valid
- `obsoletes`: completely replaces an earlier decision; the earlier decision is no longer current
- `related`: reference-only connection, aligned with RFC `see-also`; it does not change the validity of either decision

Implementation rules:

1. Add `related` as an optional frontmatter field.
2. Validate `related` references the same way as other AGD references.
3. Include `related` in `INDEX-AGD-RELATIONS.md` using the marker `-(r)->`.
4. Do **not** reverse-sync `related` into the target AGD frontmatter.
5. Keep auto-managed reverse fields only for status-changing relations:
   - `updated_by`
   - `obsoleted_by`
6. Do not introduce RFC/BCP-style `is-also` semantics unless we later need multi-number identity for the same decision set.

## Consequences

**Benefits:**
- Preserves a clean distinction between status-changing and reference-only relationships
- Matches the RFC mental model, which is familiar and well-tested
- Keeps AGD frontmatter cleaner by avoiding inferred reverse `related` entries
- Still supports reverse discovery through `INDEX-AGD-RELATIONS.md`

**Trade-offs:**
- Incoming `related` links are visible in the index, not directly in the target AGD frontmatter
- Users need to understand that `related` is informational only, not a weaker form of `updates` or `obsoletes`
