---
title: Active rule removed
---

- Confirm the active GRL was intentionally removed rather than accidentally dropped.
- Active GRLs should usually be retired by moving them to `.agents/guardrails/retired-rules/` with `retire_reason`, not silently deleted.
- If deletion is intentional, verify the review explains why ID history does not need a retired rule.
