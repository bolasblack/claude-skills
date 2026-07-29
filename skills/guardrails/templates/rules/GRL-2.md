---
number: GRL-2
short: Cross-module imports go through the target module's entry file; importing from another module's internal directory is prohibited.
enforcement:
  review: true
  lint:
    - lint/no-cross-module-import
lint_assist_reason: lint/no-cross-module-import catches direct imports into another module's internal directory; review still owns whether the needed capability belongs in that module's public interface or in a shared module.
---

This is a seed rule shipped with the guardrails skill. Replace it with a real rule for this repository, or delete it and remove its ID from `.agents/guardrails/index.md`.

## Why This Is Lint-Assisted Review

The diagnostic reliably detects the mechanical failure, an import that reaches past a module's entry file. It cannot decide the remediation: sometimes the capability should be promoted into the target module's public interface, sometimes it belongs in a shared module, and sometimes the dependency should not exist at all. Because review still owns that decision, the rule stays in the router.

## Good

- The capability is promoted into the target module's entry file and imported from there.
- The shared behavior is extracted into a module both sides may depend on.

## Bad

- The import path is rewritten to satisfy the diagnostic while the dependency direction stays wrong.
- The diagnostic is suppressed inline instead of resolving where the capability belongs.
