# Changelog

This file records Skill Composer releases so the history travels with standalone distributions that do not include the source repository's Git history.

## [3.2.1] - 2026-08-14

### Preserve only user-owned maintenance invariants

- **Changed:** Reduced `SPEC.md` to the three requirement groups the user identified as non-negotiable: cross-harness behavior, a proportionate context footprint, and package-local maintenance context. Authoring authority, evidence policy, and the creation/review distinction remain operational Skill Composer rules rather than self-specification requirements.
- **Why:** The user requires generated skills to remain cross-harness, avoid consuming excessive agent context through oversized discovery text or `SKILL.md` bodies, and preserve the distinct purposes and reasons for `SPEC.md` and `CHANGELOG.md`. Promoting other current policies into the self-specification would turn implementation choices into permanent product constraints and duplicate rules already enforced by the skill itself.

### Keep maintenance artifacts conditional

- **Changed:** Skill Composer now treats `SPEC.md` as an exceptional optional file for explicit, stable requirements that constrain future rewrites but are unnecessary during ordinary execution. Creation and review apply a four-part admission test and require a conditional maintenance pointer. `CHANGELOG.md` remains independently conditional on a skill having releases of its own or independent distribution.
- **Why:** The user clarified that most skills, including principle-driven and workflow-routing skills, keep their enduring rules in the runtime `SKILL.md` and gain nothing from a separate specification. A routine `SPEC.md` would duplicate or hide required instructions; the rare separate file preserves maintainer-only constraints without loading them during normal runs. Release history addresses a different failure mode: its causal context can disappear when a skill leaves its repository or shares commits with other skills.

## [3.2.0] - 2026-08-14

### Make Skill Composer the authoring owner

- **Changed:** Front-loaded Skill Composer's ownership and helper-conflict trigger in its description. Harness-injected authoring helpers now act as platform adapters rather than replacing Composer's scope, packaging, release-history, or quality decisions.
- **Why:** The installed generic helper told authors not to include `CHANGELOG.md`, while this release explicitly required a portable, skill-local changelog. The user therefore required the helper to remain subordinate to Skill Composer rather than overwrite its packaging decisions.

### Make release history portable and causal

- **Changed:** Moved Skill Composer's history into a skill-local `CHANGELOG.md` and required each new logical change to record `Changed` and `Why`, with `Example` only when it adds material understanding and `Migration` only when downstream action is required. Changelog reviews now re-test every retained example, not only examples added by the current diff.
- **Why:** A repository commit may combine several skills, an installed skill may contain no Git metadata, and a what-only entry does not preserve the decision that future maintainers need to evaluate. Making `Example` mandatory would instead encourage redundant filler or unsupported reconstruction.

### Require evidence-backed release explanations

- **Changed:** Required every changelog claim to trace to an explicit user explanation in the current or a retrievable earlier conversation, a requirement or spec, observed diff or code, test or log output, or an existing release record. De-identification may transform supported details but may not add a missing cause.
- **Why:** A plausible explanation can turn an agent's guess into durable false history, while an earlier user conversation may contain the real reason even when the current request only names the change.

### Compose optionally with writing-for-agents

- **Changed:** Documented `writing-for-agents` as an optional editorial pass while Skill Composer retains ownership of skill mechanics, packaging, validation, and release records.
- **Why:** The user explicitly wanted Skill Composer to point authors to `writing-for-agents` for a stronger combined result. Inspection showed complementary coverage without changing which skill owns authoring and packaging policy.

### Add a full-package review workflow

- **Changed:** Added a separate, default-read-only workflow for reviewing an existing skill. It locks the review contract, inventories the entire package and its trust boundaries, reconstructs every usage branch, audits the agent-facing contract, validates real behavior, and reports evidence-backed findings with completion criteria.
- **Why:** Skill Composer's description claimed review support, but its body only provided a creation workflow, a mixed development checklist, and a changelog-specific review rule. That structure could validate the current diff while missing stale content elsewhere in the installed skill.

### Make cross-agent portability structural

- **Changed:** Split cross-agent skills into a portable core and optional harness enhancements. Host-only features such as hooks, dynamic context, subagent configuration, UI metadata, and permission conveniences now require a portable fallback unless the skill explicitly declares itself single-harness.
- **Why:** The user required skills to work across agents without forbidding useful Claude Code-only capabilities. Treating those capabilities as enhancements preserves cross-agent core behavior while still allowing a deliberately Claude Code-only skill to depend on them.

### Add a normative self-specification

- **Changed:** Added `SPEC.md` as the normative current-state contract for Skill Composer itself, with explicit document responsibilities and change-acceptance criteria. Normal skill-authoring tasks do not load it; modifying or reviewing Skill Composer does.
- **Why:** The user wanted high-level expectations such as cross-harness support to survive future rewrites without being scattered across runtime procedures or earlier conversations. A separate specification preserves those expectations without turning `SKILL.md` into a second maintenance history.

### Refresh current platform guidance

- **Changed:** Aligned size and name checks, `allowed-tools` semantics, invocation modes, evaluations, upload navigation, organization provisioning, Skills API versioning, Agent SDK behavior, and security review with current primary documentation. Target-specific rules are now labeled instead of presented as portable requirements.
- **Why:** Review against current sources found several old universal rules that were no longer accurate, including word-based size limits, a universal 10-20-query release gate, an arbitrary skill-count consolidation threshold, mandatory metadata versioning, unrelated negative tests, the former slash-command split, and obsolete UI paths. Those rules could reject valid cross-agent skills or falsely pass weak ones.

Versions before 3.2.0 were migrated from the former in-file history. Their entries preserve the facts recorded at the time; missing rationales and examples are not reconstructed.

## [3.1.0] - 2026-03-03

- Aligned the guide with Anthropic's Complete Guide to Building Skills PDF.

## [3.0.0] - 2026-03-02

- Rewrote the guide from Anthropic's official material and merged the existing community patterns and examples.
- The former `REFERENCE.md` history separately recorded its initial standalone reference document as v3.0.0 on 2026-03-03. The two legacy files therefore did not record one shared date, and this consolidation does not infer one.

## [2.0.0] - 2025-11-15

- Renamed `write-skills` to `skill-composer` and restructured its documentation.

## [1.0.0] - 2025-11-03

- Published the initial version.
