---
name: release-notes
description: "Create release.json from a supplied changes.json file."
---

# Release Notes

## Workflow

1. Read `changes.json`, remove entries with a blank `summary`, and sort the
   remaining entries by numeric `id`.
2. Manually write `release.json` with `version` first and `entries` second. Each
   entry keeps only `id` and `summary` in that order.
3. Explain which blank entries were omitted without rewriting any retained
   summary.

Let the user choose the release version. Never infer it from Git tags.
