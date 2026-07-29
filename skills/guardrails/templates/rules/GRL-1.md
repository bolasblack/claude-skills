---
number: GRL-1
short: A module's public interface is defined by its entry file; render detail before adding or removing an export, because deprecation and ownership carve-outs apply.
enforcement:
  review: true
  lint: []
# references:
#   - docs/architecture/module-boundaries.md
#   - docs/architecture/module-boundaries.md:12-40
---

This is a seed rule shipped with the guardrails skill. Replace it with a real rule for this repository, or delete it and remove its ID from `.agents/guardrails/index.md`.

## Why This Is Pure Review

There is no reliable diagnostic for whether a new export belongs in a module's public interface. Compliance depends on ownership and design judgment, so the rule stays in the router and is read before implementation.

## Good

- A new capability is added to the module's entry file after confirming it is the module's responsibility.
- A deprecated export is kept and marked, with the removal scheduled separately.

## Bad

- A helper is exported from the entry file only so one caller can reach it.
- An export is removed in the same change that migrates its callers, so the breakage and the migration cannot be reviewed apart.

## Uncommenting references

The `references` block above is commented out because `validate` requires every reference to point at a file that exists. Uncomment it and point it at a real path in this repository.
