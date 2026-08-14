# Skill Composer Specification

Status: normative current-state contract for Skill Composer.

This file defines the properties Skill Composer must preserve as it evolves. It does not describe the operational workflow; that belongs in `SKILL.md`. `SKILL.md` may retain the minimum branch-critical constraint or platform summary needed to execute a step, but `REFERENCE.md` is authoritative for full and volatile platform detail. Human-facing package guidance belongs in `README.md`, and release history in `CHANGELOG.md`.

Read this file before modifying or reviewing Skill Composer itself. Ordinary skill-authoring tasks do not need to load it.

## Scope

Skill Composer owns the policy for creating, updating, reviewing, and packaging agent skills. It supports model-invoked, user-invoked, and dual-invocation skills, from portable cross-agent packages to explicitly single-harness packages.

The user's request, repository rules, safety and permission boundaries, and verified target-platform requirements remain higher-authority constraints. Harness-injected authoring helpers are adapters under this contract; they do not replace it.

## Required Properties

### 1. Cross-Harness by Default

A skill is cross-harness by default unless its contract explicitly names a required harness.

A cross-harness skill has two layers:

- **Portable core:** goal, inputs, outputs, decision rules, ordered workflow, failure behavior, and completion criteria.
- **Harness enhancements:** optional capabilities such as hooks, dynamic context, subagent configuration, extra metadata, UI integration, or permission conveniences.

Removing an enhancement may reduce convenience, automation, or enforcement strength, but must not make the portable core impossible to complete. Every enhancement names its supporting harness, has a tested fallback, and does not become the sole owner of required state or input.

An explicitly single-harness skill may depend on host-only capabilities. Its description and compatibility documentation must state that dependency, and neither its documentation nor packaging may claim broader portability.

### 2. One Authoring Authority

Skill Composer owns scope, information architecture, quality gates, packaging policy, and portable release history. A harness helper may contribute scaffolding, validation, evaluation, or verified platform constraints, but its generic preferences remain advisory.

Optional collaborators such as `writing-for-agents` may sharpen writing quality. The resulting skill must remain usable when those collaborators are not installed.

### 3. Evidence Before Inference

Requirements, review findings, compatibility claims, and changelog rationale distinguish confirmed evidence from inference and unknowns. Unstable platform facts are checked against current primary documentation. Missing evidence remains visible; plausible explanations are not promoted into history or requirements.

### 4. Distinct Creation and Review Contracts

Creation starts from intended use cases, defines observable success, establishes a baseline, and writes only the instructions needed to improve it.

Review starts from an existing package, is read-only unless modification is authorized, and evaluates the whole package rather than only the current diff. It reconstructs the intended contract independently, inventories every packaged artifact and trust boundary, checks current target constraints, validates real behavior, and reports every unrun check or unknown.

Creation and review share quality gates, but neither is disguised as the other.

### 5. Behavior Is the Acceptance Boundary

Schema validation is necessary where available but never proves that a skill works. Acceptance evidence covers the applicable behavior surfaces:

- invocation and realistic boundaries;
- functional output and side effects;
- completion criteria and failure paths;
- isolation and coexistence with other skills; and
- the portable fallback without harness enhancements.

Evaluation size follows purpose and risk. A tuning heuristic must not become a universal release gate.

### 6. Progressive, Non-Duplicative Information

Runtime decisions, ordered process, and minimum branch-critical constraints stay in `SKILL.md`; any platform summary points to its authoritative detail. Full specifications, volatile platform facts, and review checklists stay in `REFERENCE.md`. This file keeps only stable product expectations.

Rules are co-located with the decisions they govern. References have explicit read conditions. Examples, troubleshooting, tables, and extra files exist only when they add material understanding or executable value. Historical pattern snapshots never override current specifications.

### 7. Portable Release Context

An independently versioned or independently distributed skill carries the release context required by Skill Composer's release policy inside its own package. Its changelog records evidence-backed `Changed` and `Why` entries; examples and migration notes remain conditional.

Packaging and validation are target-specific. Git history, repository-wide commits, or one platform's version identifier must not be the sole release record for a standalone skill.

## Change Acceptance

A change to Skill Composer is complete only when:

1. every affected required property above still holds, or this specification is deliberately updated with an evidence-backed reason;
2. `SPEC.md`, `SKILL.md`, `REFERENCE.md`, `README.md`, and `CHANGELOG.md` remain consistent with their distinct responsibilities;
3. every new host-only enhancement has a named target, portable fallback, and applicable test, unless the package is explicitly single-harness;
4. current primary sources support changed platform claims;
5. schema, links, instructions, and affected behavior have been validated, with unavailable checks reported; and
6. removed or replaced concepts leave no contradictory semantic residue elsewhere in the packaged skill.
