---
number: GRL-3
short: Runtime source files must not import test-only helpers or fixtures.
enforcement:
  review: false
  lint:
    - lint/no-test-import-in-runtime
skip_index_reason: lint/no-test-import-in-runtime names the offending import and the fix is always to move the helper out of the test directory, so the rule needs no hot-path reading.
---

This is a seed rule shipped with the guardrails skill. Replace it with a real rule for this repository, or delete it. Deleting it requires no router edit, because pure-lint rules are never listed in `.agents/guardrails/index.md`.

## Why This Is Pure Lint

The rule is mechanical, testable, scope-aware, and self-contained: the diagnostic points at the import, and the remediation is the same every time. Nothing about it needs to be read before writing code, so it is kept out of the router and the `skip_index_reason` records exactly why.

## Adopter Note

A pure-lint rule is only honest if the named diagnostic actually exists and actually covers the whole rule. If you keep this seed, implement `lint/no-test-import-in-runtime` in your linter or change the rule to lint-assisted review and list it in the router.
