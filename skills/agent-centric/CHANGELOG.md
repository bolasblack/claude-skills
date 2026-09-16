# Changelog

## [Unreleased]

### Establish independent release ownership

- **Changed:** Added a machine-readable `VERSION` owner initialized to the existing `1.6.1` baseline and moved the recorded version history out of the runtime instructions.
- **Why:** Independent skill releases need one version owner and a portable history without repeating release metadata in the skill prompt.

## Migrated version history

The following entries preserve the former in-file history verbatim. Missing
rationales and publication evidence are not reconstructed.

- v1.6.1 (2026-04-13): Fully manage `updated_by`/`obsoleted_by` by syncing and pruning reverse references, skip validation of auto-generated reverse fields
- v1.6.0 (2026-04-13): Add `related` relationship with RFC-style `see-also` semantics, extend relation index with `-(r)->`, clarify archival relationship model
- v1.5.0 (2026-01-23): Remove PreToolUse hook (PostToolUse validation sufficient), fix exit codes to use code 2 for blocking errors
- v1.4.0 (2026-01-22): Add PreToolUse hook to block invalid AGD creation, auto-detect project dir
- v1.3.0 (2025-01-22): Split references/, renamed validate-agds.py
- v1.2.0 (2025-01-22): Split to SKILL.md + REFERENCE.md
- v1.1.0 (2025-01-21): Merged index files, hooks in frontmatter, auto-init
- v1.0.0 (2025-01-21): Initial version
