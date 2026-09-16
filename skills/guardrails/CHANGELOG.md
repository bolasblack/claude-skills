# Changelog

## [Unreleased]

### Establish independent release ownership

- **Changed:** Added a machine-readable `VERSION` owner initialized to the existing `1.1.0` baseline and moved the recorded version history out of the runtime instructions.
- **Why:** Independent skill releases need one version owner and a portable history without repeating release metadata in the skill prompt.

## Migrated version history

The following entries preserve the former in-file history verbatim. Missing
rationales and publication evidence are not reconstructed.

- v1.1.0 (2026-07-29): Consolidated enforcement doctrine into `references/schema.md` and CLI semantics into `references/tooling.md`, with pointers replacing the duplicated passages; routed the existing-codebase audit workflow to `references/auditing.md`; added a troubleshooting section to `references/tooling.md`; `render --detail` is accepted in any argument position; hardened the skill-local test suite.
- v1.0.0 (2026-07-29): Initial public release of the rendered guardrail framework skill.
