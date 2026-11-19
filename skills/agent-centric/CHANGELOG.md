# Changelog

Changes are recorded by date, newest first. Entries dated 2026-04-13 and earlier were moved from `SKILL.md` and are kept as written.

## 2026-11-19

### Read the setup steps from a reference only on request

- **Changed:** The initialization steps, and what initialization creates, moved from the README's Setup section to `references/setup.md`. When the user explicitly requests project setup, the agent reads that file in full, follows it, and reruns the setup check. The README now tells users to ask the agent for setup.
- **Why:** The skill pointed the agent at one section of the README (`README.md#setup`). A file tool cannot jump to a section, so the agent could read a fragment and miss the steps and gates around it.

### Link the companion skill by repository URL

- **Changed:** The README links the guardrails companion skill by its repository URL instead of a relative path to a sibling directory.
- **Why:** A relative link that leaves the skill points at nothing when the skill is installed on its own.

### Point the agent at the index format reference

- **Changed:** The skill instructions now tell the agent to read `references/index.md` when looking up decisions by tag or by relationship.
- **Why:** No instruction linked that reference, so the agent never read the documented index formats.

## 2026-10-04

### Require project setup before skill use

- **Changed:** Skill use begins with a read-only setup check. Missing or incomplete setup stops AGD operations; initialization requires an explicit user request. Automatic hooks use the same check before validation or index generation.
- **Why:** The agent must establish that the target project has AGD setup before using the skill. A shared `.agents/` directory alone does not establish that prerequisite.

## 2026-04-13

- Fully manage `updated_by`/`obsoleted_by` by syncing and pruning reverse references, skip validation of auto-generated reverse fields
- Add `related` relationship with RFC-style `see-also` semantics, extend relation index with `-(r)->`, clarify archival relationship model

## 2026-01-23

- Remove PreToolUse hook (PostToolUse validation sufficient), fix exit codes to use code 2 for blocking errors

## 2026-01-22

- Add PreToolUse hook to block invalid AGD creation, auto-detect project dir
- Split references/, renamed validate-agds.py
- Split to SKILL.md + REFERENCE.md
- Merged index files, hooks in frontmatter, auto-init
- Initial version
