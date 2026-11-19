# Changelog

Changes are recorded by date, newest first. Entries dated 2026-07-29 were moved from `SKILL.md` and are kept as written.

## 2026-11-19

### Link the companion skill by repository URL

- **Changed:** The README links the agent-centric companion skill by its repository URL instead of a relative path to a sibling directory.
- **Why:** A relative link that leaves the skill points at nothing when the skill is installed on its own.

### Ship the review-metadata instruction catalog under `assets/`

- **Changed:** The per-category instruction files that `review-metadata` prints moved from `references/review-metadata-instructions/` to `assets/review-metadata-instructions/`. The CLI resolves the catalog there, so `scripts/` and `assets/` must stay siblings. Command output is unchanged.
- **Why:** The catalog is data the CLI reads and prints, not a reference the agent reads. Under `references/` it looked like agent documentation that no instruction linked.
- **Migration:** A copy that installs the skill's directories selectively must include `assets/` next to `scripts/`; edits to the catalog in an installed copy move to the new directory.

## 2026-07-29

- Consolidated enforcement doctrine into `references/schema.md` and CLI semantics into `references/tooling.md`, with pointers replacing the duplicated passages; routed the existing-codebase audit workflow to `references/auditing.md`; added a troubleshooting section to `references/tooling.md`; `render --detail` is accepted in any argument position; hardened the skill-local test suite.
- Initial public release of the rendered guardrail framework skill.
