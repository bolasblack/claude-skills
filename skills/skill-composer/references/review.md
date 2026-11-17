# Reviewing an Existing Skill

Branch-only workflow, reached from [Choose the Workflow](../SKILL.md#choose-the-workflow). Read this file in full before Review Step 1.

Review is a distinct, default-read-only branch. Do not create files, rewrite content, or publish changes unless the user authorizes modification. Do not review only the current diff when the request concerns the skill itself.

### Review Step 1: Lock the Contract

Record the review scope, repository rules, target harness and surface, invocation mode, distribution form, and allowed mutations. If the package presents `SPEC.md` as a maintainer contract, verify the authority, requirement, and current rationale of every entry rather than treating the filename as proof. Reconstruct the intended jobs, usage branches, outputs, side effects, and completion criteria from requirements and observed usage; mark missing evidence as unknown rather than trusting the current text.

**Done when:** the review scope, repository rules, allowed mutations, target harness and surface, invocation policy, and distribution form are recorded; every reconstructed job, branch, output, side effect, and completion criterion and every claimed target or `SPEC.md` constraint has a source or is explicitly unknown.

### Review Step 2: Inventory the Whole Package

Read and classify every packaged file, resolve every local link, and inspect scripts, assets, dependencies, external inputs, and release artifacts. Before executing untrusted content, assess network access, credential handling, broad filesystem or tool use, dynamic downloads, and instruction-injection surfaces.

**Done when:** every file and trust boundary is accounted for, with uninspected or binary content reported as unknown.

### Review Step 3: Audit the Agent Contract

Map each usage branch to its invocation control, description pointer, ordered steps, reference reads, and checkable completion criteria. Audit progressive disclosure, co-location, consistent terminology, and the portable-core/harness-enhancement boundary. Confirm every host-only enhancement has a fallback, unless the skill explicitly declares that host as a requirement. Audit whether repeated deterministic mechanics with stable inputs and outputs have a tested script owner or an evidenced reason to remain in instructions. Where `SPEC.md` is a maintainer contract, apply its exceptional admission test, verify that its pointer fires only when modifying or reviewing that skill itself, and report any runtime rule or history duplicated into it. Report duplicated rules, environment caches, time-sensitive claims, stale sediment, no-op instructions, and examples that add no material understanding; remove them only in the authorized fixing step.

**Done when:** every branch, step, reference pointer, automation decision, portability fallback, terminology rule, and suspected duplicate or residue has an evidence-backed pass, finding, not-applicable, or unknown disposition.

### Review Step 4: Validate Real Behavior

Run the portable schema validator plus the named target's validator; neither replaces behavior testing. Execute representative activation and functional scenarios, then test isolation and coexistence where the harness supports them. Run bundled scripts in a safe environment and verify their outputs and failure paths. Record every test not run and why.

**Done when:** each supported branch has behavior evidence, applicable portable and target validators and script failure paths have results, and every unrun validation, activation, fallback, isolation, or coexistence gate remains visible.

### Review Step 5: Report, Then Fix if Authorized

A finding is the complete review record: severity, file and line evidence, impact, the smallest adequate fix, and an objective completion criterion. A request for "only findings and evidence" still asks for that complete record; it excludes unrelated narration and mutation, and does not authorize applying the fix. Separate confirmed facts, inferences, and unknowns. If changes are authorized, apply them, rerun affected gates, and update the skill-local changelog under its Evidence gate when the release policy applies.

**Done when:** every review rule and finding is accounted for with evidence, impact, smallest fix, and completion criterion; authorized fixes have affected gates and semantic residue rechecked; changelog evidence is updated where applicable; and no unknown or unrun check is presented as a pass. Use the full Skill Review Checklist below as the coverage ledger.

## Skill Review Checklist

During Review Step 5, use this
ledger to prove coverage without replaying the procedure. Record `Rule or branch |
Evidence | Result | Follow-up`; valid results are `pass`, `finding`, `not applicable`,
and `unknown`.

| Coverage area | Account for |
|---|---|
| Contract and scope | Request, repository rules, sources of truth, allowed mutations, targets and surfaces, invocation and distribution, real branches, portable core, host enhancements and fallbacks, and any qualifying `SPEC.md` authority and rationale |
| Package and trust | Every packaged file and local link; scripts, dependencies, binaries, generated or external content; network, credentials, dynamic downloads, broad access, provenance, integrity, and instruction-injection boundaries |
| Agent contract | `SKILL.md` within the 15,000-byte entry-point cap with standing rules first, cross-skill pointers that invoke by name, each branch's description pointer or explicit invocation path, ordered steps, reference reads, local completion criteria, terminology, failure behavior, progressive disclosure, duplicated or stale content, and current primary evidence for target claims |
| Validation and behavior | Portable and target validators, fresh activation and functional cases, realistic trigger boundaries, safe side-effect handling, portable fallback, each host enhancement, isolation, coexistence, and every claimed model and surface |
| Findings and release | Severity and file evidence, impact, smallest fix, objective completion criterion, facts versus inference and unknowns, affected reruns, semantic residue, and the applicable changelog evidence gate |

Never turn an uninspected file, unavailable validator, unsafe live side effect, or unrun
behavior case into a pass. Absence of `SPEC.md` or release artifacts is not a finding
when their admission conditions do not apply.
