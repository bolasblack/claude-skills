---
name: skill-composer
description: "Use when the user asks to create a new Agent Skill, revise an existing skill's authored behavior or activation, audit a complete skill package, design its eval suite, port it across agent harnesses, or prepare and validate its release. When a generic skill-authoring helper overlaps, this skill owns scope, structure, portability, validation, and release history. If the work neither changes nor audits an Agent Skill package, do not load this skill."
license: LICENSE.md
---

# Skill Composer

Create well-structured, discoverable agent skills. Based on the current Agent Skills specification, target-platform documentation, and community best practices.

When modifying or reviewing Skill Composer itself, read [SPEC.md](SPEC.md) first. It holds the rare maintainer-only requirements that must constrain future rewrites; ordinary skill-authoring tasks do not need it.

Skill Composer's own eval manifests, fixtures, package tests, and eval runner's
implementation are maintainer evidence, not examples or validators for a skill being
authored. Do not inspect them while using Skill Composer to author another skill. The
runner's documented public CLI is a shared validator, and Step 8 owns when to invoke
that CLI. The target is not expected to contain a runner copy. Invoke this public seam
without inspecting the runner implementation or Skill Composer's own eval package.
Read maintainer evidence only when the user asks to modify, review, test, or release
Skill Composer itself or to maintain its eval infrastructure.

## Authoring Authority

Treat Skill Composer as the owner of skill-authoring policy whenever it is installed and the task creates or changes a skill.

Harnesses may inject generic skill-authoring helpers such as `skill-creator`. Use their platform-specific scaffolding, schema validation, or evaluation capabilities when useful, but treat their authoring defaults as advisory inputs. Reconcile those inputs against the user's request, repository rules, verified target-platform constraints, and this skill. A helper must not replace this skill's decisions about scope, structure, packaging, release history, or quality.

This precedence applies to skill-authoring guidance, not to the host's safety, permission, or instruction hierarchy. A target platform's verified format requirement remains a compatibility constraint; a generic helper preference does not become a universal rule. For example, a helper's blanket preference against `CHANGELOG.md` does not override a requirement for a portable, skill-local release record.

## Skills & MCP

MCP supplies connectivity and tools; skills supply the workflow and domain judgment for using them. A skill may enhance MCP or stand alone. See [Skills and MCP Relationship](REFERENCE.md#skills-and-mcp-relationship) when that distinction affects scope.

## Core Design Principles

### Progressive Disclosure

Portable skills use a three-level system to minimize context usage:

1. **YAML frontmatter**: Small metadata used for discovery where the target supports model invocation.
2. **SKILL.md body**: Runtime instructions loaded when the skill is invoked.
3. **Linked files**: References, scripts, and assets loaded only when the workflow needs them.

Exact discovery and content-lifecycle behavior is target-specific; verify it for every supported harness and surface.

### Composability

Hosts can load multiple skills simultaneously. Skills should work well alongside others and never assume they are the only capability available.

For a stronger agent-facing writing pass, optionally compose this skill with Matt Pocock's [writing-for-agents](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents) when the user explicitly requests it or both skills are invoked for the task. Do not seek or load it merely because it is installed. Skill Composer owns skill scope, mechanics, packaging, and validation; `writing-for-agents` sharpens context pointers, completion criteria, information hierarchy, and pruning. Keep the composition optional so the resulting skill does not depend on a sibling skill being installed.

### Portability

Default to two layers:

1. **Portable core:** the goal, inputs, outputs, decision rules, ordered workflow, failure behavior, and completion criteria work across compatible agents.
2. **Harness enhancements:** hooks, dynamic context, subagent configuration, UI metadata, permission conveniences, and similar host-only features may improve ergonomics or enforcement but do not become the sole way to complete the core workflow.

Name each enhancement's host and provide a portable fallback. A skill may depend on a host-only feature only when its description and compatibility contract explicitly make the skill host-specific; do not claim cross-agent portability for that package.

**Harness research:** Before creating, changing, or reviewing a target-specific claim about discovery, schema, invocation, permissions, hooks, installation, packaging, validation, or host enhancements, read [HARNESS-RESEARCH.md](HARNESS-RESEARCH.md) and build fresh evidence for the named harness and surface. A portable core that names multiple compatible harnesses remains portable-only when it encodes no harness-specific fact or enhancement; do not fetch per-harness documentation merely to restate that portable contract. Skip the research branch in that case.

Never scan home or user-level skill directories for examples, validators, or target
evidence. Use the current workspace, an exact validator command already named by the
package or primary documentation, and the named target's primary documentation only
when the harness-research branch applies. Do not enumerate `PATH`, installation
directories, or language package registries to hunt for validators. If an applicable
validator cannot be resolved through those bounded sources, perform the portable
manual checks that remain available and record the missing validator as `unknown`.

### Environment-Native Automation

Script repeated, deterministic mechanics with stable inputs and outputs when that materially reduces agent reinterpretation; keep judgment and one-off adaptation in instructions. Before coding, name the public seam and invoke the `tdd` skill when available, or apply the same one-behavior public-seam red-green loop directly. Run the public-seam test and preserve its observed failure before writing the implementation; then make the minimum implementation change and rerun that same test to green. Do not create the test and implementation together and call the first green run red-green evidence.

Choose a runtime the supported environment already guarantees and minimize total installed and owned complexity. When every claimed environment provides Python and no native runtime is already selected, Python's standard library is a reasonable default for a standalone portable helper; target-specific skills prefer their environment's runtime. If the claimed environments have no common runtime, keep a portable manual path or provide tested environment adapters. Add a dependency when it removes substantially more code and maintenance than its installation and supply-chain surface add. A host-enhancement script retains a portable manual fallback. See [Script Requirements](REFERENCE.md#script-requirements) for packaging checks.

## Choose the Workflow

- **Create:** define use cases and validation evidence in [Planning Before Creating or Updating](#planning-before-creating-or-updating), then follow [Creating or Updating a Skill](#creating-or-updating-a-skill) in order.
- **Update:** inventory the current package and lock its existing contract first. If the inventory contains `evals/evals.json` or `evals/trigger-eval.json`, or the user explicitly asks for eval work, read the [Evaluation Reference](references/evaluation.md) before editing the target and enter Step 8 for that branch. Otherwise keep that reference unopened. Then follow [Planning Before Creating or Updating](#planning-before-creating-or-updating) and [Creating or Updating a Skill](#creating-or-updating-a-skill) for affected branches only. Preserve and update affected regression cases when the package already owns them.
- **Review:** follow [Reviewing an Existing Skill](#reviewing-an-existing-skill). Stay read-only unless the user authorizes fixes; if authorized, enter the update branch only after reporting the review findings.
- **Package or release:** follow [Packaging and Releasing a Skill](#packaging-and-releasing-a-skill) after the authored package is complete. Packaging is not proof that activation or runtime behavior works.

**Done when:** the requested operation has one selected workflow, every combined operation has an explicit transition between workflows, and no review request silently becomes an edit.

## Planning Before Creating or Updating

### Start with Use Cases

Ask yourself first:
- What does a user want to accomplish?
- What multi-step workflows does this require?
- Which tools are needed (built-in or MCP)?
- What domain knowledge or best practices should be embedded?

Identify at least one concrete use case for every real usage branch before writing anything. Do not invent extra cases to meet a quota.

**Good use case definition**:

```
Use Case: Project Sprint Planning
Trigger: User says "help me plan this sprint" or "create sprint tasks"
Steps:
1. Fetch current project status
2. Analyze team velocity and capacity
3. Suggest task prioritization
4. Create tasks with proper labels
Result: Fully planned sprint with tasks created
```

**Three common categories**:

| Category | Purpose | Key Techniques |
|----------|---------|----------------|
| **Document & Asset Creation** | Consistent, high-quality output (docs, code, designs) | Embedded style guides, templates, quality checklists |
| **Workflow Automation** | Multi-step processes with consistent methodology | Step-by-step workflow, validation gates, iterative refinement |
| **MCP Enhancement** | Workflow guidance on top of MCP tool access | Coordinate MCP calls, embed domain expertise, error handling |

**Real examples:**
- **Document & Asset Creation**: `frontend-design` skill — "Create distinctive, production-grade frontend interfaces with high design quality." Also see skills for docx, pptx, xlsx.
- **Workflow Automation**: `systematic-debugging` skill — a four-phase diagnosis workflow with explicit evidence gates.
- **MCP Enhancement**: `sentry-code-review` skill (from Sentry) — "Automatically analyzes and fixes detected bugs in GitHub Pull Requests using Sentry's error monitoring data via their MCP server."

Classify whether users start from a desired outcome or from a named tool; this affects the workflow pattern, not the portable contract. See [Problem-First vs Tool-First](REFERENCE.md#problem-first-vs-tool-first) when the choice is unclear.

**Done when:** every real usage branch has one concrete use case with a trigger, ordered actions, required tools or domain rules, and an observable result; no case exists only to satisfy a quota.

### Define Success Criteria and Validation Evidence

Define observable success before extensive instructions. Packaged eval artifacts follow
the admission rule in Step 8; planning a check does not by itself authorize creating
them.

1. Run representative tasks without the skill when a baseline comparison is material,
   and record the specific gap.
2. Define expected behavior and a checkable completion criterion for each real use case.
3. Select proportionate evidence: existing package tests or evals, disposable manual
   scenarios, or target-host checks.
4. Write the minimum instructions needed to improve the observed behavior.
5. Run the same checks with the skill and iterate from evidence.

When an eval suite is admitted, start with 2-3 scenarios tied to observed gaps and
expand only for real branches or risks. Otherwise keep the validation plan manual and
do not turn it into package files without the user's approval.

For a model-invoked skill, cover intended triggers, realistic near-misses, and ambiguous boundary cases. For every skill, measure task correctness, instruction following, tool or API failures, user correction, and any output contract that matters. Compare efficiency only after correctness; fewer tokens or tool calls are not improvements when behavior regresses.

Run evaluations against a disposable fixture or sandbox by default. A real API write,
outbound message, charge, publication, or non-recoverable external side effect requires
explicit user authorization for that exact effect and a cleanup plan. When that
authorization or a safe test surface is unavailable, use a faithful fixture and keep
live behavior `unknown`.

**Done when:** each use case and recorded baseline gap has expected behavior and a
checkable result, the same check can be repeated after the minimum instruction change,
and every external side effect is safely isolated, explicitly authorized, or marked
`unknown`; packaged eval artifacts exist only when Step 8 admits them.

## Creating or Updating a Skill

For an update, capture the current package inventory, behavior contract, and passing
baseline before Step 1. Map the requested change to affected usage branches, preserve
unrelated behavior and user-owned files, and remove obsolete files or terminology when
the change retires a concept. A new skill begins without that compatibility baseline.

### Step 1: Choose Target and Scope

Name the target harness, surface, invocation mode, and distribution form before choosing a path or frontmatter. Define the portable core first, then add verified target-only enhancements with fallbacks. If the skill is intentionally single-harness, state that contract explicitly instead.

Use [Distribution](REFERENCE.md#distribution) to decide scope, delivery, discovery,
update lifecycle, and validation. Resolve the named target's current path, commands,
UI flow, and host extensions through [Harness Research](HARNESS-RESEARCH.md) before
encoding target-specific guidance.

**Done when:** the target, surface, invocation policy, distribution form, portable core, and every host enhancement or explicit host requirement are named without an unsupported compatibility claim.

### Step 2: Create File Structure

For an update, keep the existing structure unless the requested behavior or packaging
contract requires a file to be added, moved, or removed.

Before changing the package layout, read [Directory Structure
Patterns](REFERENCE.md#directory-structure-patterns) and choose the smallest pattern
that contains the runtime instructions, required executable resources, and applicable
maintenance or release artifacts. Keep independently distributed dependencies and
artifacts inside the skill folder, and do not add a human-facing document that repeats
runtime instructions.

`SPEC.md` is intentionally absent from the default structure. Add it only when an explicit, stable requirement must constrain future modifications or rewrites but is not needed during ordinary skill execution. Put runtime principles and workflows in `SKILL.md`, branch-only lookup material in references, and release history in `CHANGELOG.md`. In the rare qualifying case, keep `SPEC.md` short, state each current requirement and why it must survive, and add a conditional pointer from `SKILL.md` for modifying or reviewing that skill itself. Apply the complete [Exceptional Maintainer Specifications](REFERENCE.md#exceptional-maintainer-specifications) admission test; importance, length, or complexity alone does not qualify a skill.

**Done when:** the selected layout satisfies the authoritative package rules, every file has one purpose and owner, updates preserve unrelated user-owned files, and all packaged links resolve inside the distribution boundary.

### Step 3: Write YAML Frontmatter

Before writing frontmatter, read the authoritative [YAML Frontmatter
Specification](REFERENCE.md#yaml-frontmatter-specification). Write the portable fields
first. Add a target-only field only when fresh [Harness
Research](HARNESS-RESEARCH.md) verifies that the named surface supports it, and keep
that extension out of the universal contract. For model invocation, write the
description in Step 4. Run both the portable validator and the target validator.

**Done when:** the folder and frontmatter satisfy the portable schema, every extension traces to current target evidence, and both applicable validators pass or remain explicitly `unknown`.

### Step 4: Write the Description

First decide whether automatic model invocation is safe and useful. Model invocation
reduces user cognitive load but spends discovery context load and requires a
discriminating description pointer. Prefer explicit user invocation when timing or
side effects need deliberate control, or when automatic discovery cost is not
justified. A host that exposes both paths adds a capability, not a third information
architecture strategy: still make the automatic-invocation decision explicitly. See
the current target controls only after this portable decision by using [Harness
Research](HARNESS-RESEARCH.md).

**Pattern**: `[What it does] + [When to use it] + [Key capabilities]`

```yaml
# Good - specific with trigger phrases
description: "Analyzes Figma design files and generates developer handoff
  documentation. Use when user uploads .fig files, asks for 'design specs',
  'component documentation', or 'design-to-code handoff'."

# Good - includes file types and actions
description: "Analyze Excel spreadsheets, create pivot tables, generate charts.
  Use when working with .xlsx files, spreadsheets, or tabular data analysis."

# Bad - no triggers
description: "Helps with projects"

# Bad - too technical, no user language
description: "Implements the Project entity model with hierarchical relationships"
```

For each real model-invoked branch, include one discriminating context pointer using terms users actually supply: file types, actions, domain terms, or states. Prefer positive scope. Add a negative boundary only for a realistic near-neighbor that positive wording cannot distinguish, then test that boundary directly.

**Done when:** the invocation policy states whether automatic selection is enabled and safe, each model-invoked branch has one realistic discriminating pointer and tested near-neighbor boundary, every explicit-only branch remains discoverable without false trigger prose, and current target controls have evidence or remain `unknown`.

### Step 5: Write Instructions

Clear, explicit, step-by-step. Put critical instructions at the top.

```markdown
## Instructions

### Step 1: Gather Context
Run `git diff --staged` to see changes.

**Done when:** the staged change and repository constraints are captured.

### Step 2: Generate Output
Create commit message with:
- Summary under 50 characters
- Detailed description of what and why
- Affected components listed

**Done when:** the message passes the repository's commit-message checks.
```

**Copy-and-adapt template** for main instructions:

```markdown
---
name: your-skill
description: [...]
---

# Your Skill Name

## Instructions

### Step 1: [First Major Step]
Clear explanation of what happens.

**Done when:** [observable completion criterion for Step 1]

### Step 2: [Second Major Step]
[...]

**Done when:** [observable completion criterion for Step 2]
```

**Best practices**:
- Be specific and actionable (not "validate things properly" but list exact checks)
- Give every step a checkable, exhaustive completion criterion
- Put a rule next to the step it governs; use references for lookup material, not split process state
- Reference bundled resources with explicit read conditions: `Before writing queries, consult references/api-patterns.md`
- Treat **5,000 tokens** or **500 lines** as prompts to investigate context cost, not universal pass/fail limits; size by observed behavior and verified surface caps, and move branch-only lookup material to one-level-deep references. See [Large Context Issues](REFERENCE.md#large-context-issues)
- Include troubleshooting and examples only when an evidenced branch needs them
- Apply [Environment-Native Automation](#environment-native-automation) when a step has stable repeated mechanics

**Done when:** every real branch has an ordered path, every step ends in a local observable completion criterion, every reference has a read condition, and failure behavior is defined wherever an operation can fail.

### Step 6: Consider Tool Pre-Approval

`allowed-tools` is experimental in the portable spec and varies by host. Before adding
it, use [Harness Research](HARNESS-RESEARCH.md) to establish the named surface's current
support, syntax, scope, and restriction mechanism. See [Tool
Pre-Approval](REFERENCE.md#tool-pre-approval).

**Done when:** pre-approval is omitted or every added declaration has current surface-specific evidence and is not misrepresented as a portable restriction policy.

### Step 7: Record Portable Release History

When a skill has releases of its own or independent distribution, update its local
`CHANGELOG.md` in the same change as released behavior. Before writing, read the
mandatory [Evidence gate](REFERENCE.md#evidence-gate) and [Portable Changelog
Format](REFERENCE.md#portable-changelog-format). Record each net logical change once
with evidence-backed `Changed` and `Why`; add `Example` only when its removal would
lose material causal understanding, and `Migration` only when a real downstream user
must act because a supported public invocation, input, output, installation, or
configuration contract changed. An internal implementation replacement with unchanged
public invocation, inputs, and outputs has no Migration entry. A caller's private
wrapper around a removed implementation detail does not establish a supported migration
unless the existing contract or direct evidence identifies that wrapper as public.
Re-test every retained example during review. Do not reconstruct missing
legacy rationale or narrate revisions made inside one unreleased change as migrations.
An unpublished, single-use skill does not need an empty changelog.

**Done when:** every applicable net change has one evidence-backed entry, every retained example adds material understanding, every migration names real downstream action, and runtime instructions contain no duplicate release history.

### Step 8: Validate Behavior and Maintain Admitted Evals

Treat packaged evals as opt-in maintenance artifacts, not a default for every skill:

- When the user explicitly asks to add or change evals, create or update the smallest
  suite that covers the requested behavior.
- When the target already contains an eval suite, preserve it and update affected
  existing cases. Add a case only when the change alters behavior or leaves a real
  branch or risk uncovered.
- When neither condition holds, do not create eval manifests, fixtures, or runner
  copies. Continue with applicable validators and manual behavior checks. If a material
  activation, regression, side-effect, or release risk would benefit from repeatable
  evals, recommend the smallest useful suite and ask the user before adding it;
  otherwise do not propose eval work.

When neither condition holds, stay in the no-suite branch: do not search, grep, or open the Evaluation Reference; do not inspect or invoke `eval-skill.py`, including `check`. That CLI validates admitted eval contracts and is not a general package or target schema validator. Use the applicable portable schema validator, named target validator, bundled tests, and manual behavior checks instead.

Before creating, updating, running, tuning, or maintaining an admitted eval suite, read
the [Evaluation Reference](references/evaluation.md). It owns the suite format, coverage
model, shared-runner boundary, target evidence, observability, and tuning loop; keep
those branch-only mechanics there.

Before running checks, create one **validation ledger** as the status owner for the
selected workflow. List every applicable gate, including package and target schema,
bundled tests, fresh-session behavior, the portable fallback, clean installation when
packaging, and the deterministic eval contract when a suite is admitted. Give every row
exactly one status: `pass`, `fail`, or `unknown`, plus its command or evidence, or
the reason it could not run. Add any gate discovered later; an absent or unrun gate is
incomplete. Derive its rows from the locked package inventory: account for every
discovered test entry point and executable script, record its baseline result before
editing, and record final evidence whether it is retained, replaced, or removed. If a
removed executable was not safe or authorized to run, keep its unrun baseline behavior
as `unknown`; deletion does not erase that gate.

Apply ledger evidence to every artifact: frontmatter, body, changelog, and final report may call a named target verified, supported, or tested only when the matching target-behavior ledger row is `pass`. Static schema validation, a manual walkthrough, portable-by-construction design, or a pass on one target does not prove behavior on another; use narrower design wording and keep unrun targets `unknown`.

Run applicable deterministic validators and affected behavior scenarios. For a
behavior-affecting change, use a verified target adapter or execute the planned scenario
manually in a fresh session; run the full owned suite before release when one exists. A
schema or eval-contract check is never behavior proof. Follow the side-effect boundary
locked during planning, and require explicit user authorization before any live target
call that consumes credentials, quota, or paid tokens or causes a real external effect.
Unavailable or unobservable evidence stays `unknown`.

Report every ledger row in the final response. The overall result is green only when
every required row passes. Host diagnostics may explain discovery or invocation
failures, but they do not substitute for behavior evidence.

**Done when:** every supported branch has an observable validation result, every
applicable gate is reported as `pass`, `fail`, or `unknown`, and every unsafe or
unavailable live check remains visible; an admitted suite also passes its deterministic
contract and affected cases.

## Reviewing an Existing Skill

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

**Done when:** every review rule and finding is accounted for with evidence, impact, smallest fix, and completion criterion; authorized fixes have affected gates and semantic residue rechecked; changelog evidence is updated where applicable; and no unknown or unrun check is presented as a pass. Use the full [Skill Review Checklist](REFERENCE.md#skill-review-checklist) as the coverage ledger.

## Packaging and Releasing a Skill

### Release Step 1: Lock the Release Contract

Record the exact skill, proposed version, target harnesses and surfaces, invocation
policies, distribution forms, and files that belong in the artifact.

**Done when:** one release ledger names the exact skill, proposed version, target harnesses and surfaces, invocation policies, distribution forms, artifact files, and every claimed gate before the artifact is built.

### Release Step 2: Build the Exact Artifact

Build from the skill directory only. Include every linked script, reference, asset,
dependency, license or attribution notice, and required release record; exclude
temporary research bundles, caches, secrets, and unrelated repository files.

**Done when:** an explicit artifact inventory contains every required file and no source-tree-only or temporary residue.

### Release Step 3: Validate Schema and Behavior

Run the portable schema validator, every claimed target validator, bundled tests, and
local link checks. Then use the evaluation side-effect boundary from Step 8 and run
fresh-context activation and functional scenarios on every claimed target, including
portable fallback, isolation, and coexistence where those claims apply. Record an
unavailable gate as `unknown`; do not convert it to a pass or silently narrow the
artifact after testing.

**Done when:** every locked gate has evidence or an explicit `unknown`, and no validator result is presented as behavior proof.

### Release Step 4: Prepare Release Records

Apply the [Evidence gate](REFERENCE.md#evidence-gate), update the skill-local changelog
under `Unreleased`, prepare target-owned version metadata, and state any compatibility
or migration effect without inventing rationale. Build and validate a release candidate
without presenting it as the completed release.

**Done when:** the candidate records each net change once, every migration corresponds to real downstream action, all metadata is ready for one proposed version while the changelog remains `Unreleased`, and candidate validation has a result for every locked pre-install gate.

### Release Step 5: Verify and Promote the Exact Artifact

Install the candidate artifact in a clean instance of each claimed surface and rerun at
least one representative scenario per real workflow branch. Compare the installed
inventory with the artifact so repository-only files cannot mask a broken package. If
the candidate passes, assign the version and date, build the final artifact, and repeat
the clean-install inventory and representative branch checks on that exact final
artifact. If promotion or the final checks fail, return the changelog to `Unreleased`
and do not publish.

**Done when:** the versioned final artifact itself matches the clean-install inventory on every claimed surface and exercises every supported branch without source-tree residue; otherwise the changelog is `Unreleased` and no versioned release state remains.

**Done when:** the exact artifact is self-contained, every claimed target has schema and
behavior evidence, every unavailable gate is visible, and a clean installation exercises
all supported branches without relying on source-tree residue.

## Workflow Patterns

When the instruction shape is not already implied by the use cases, read [Workflow
Patterns](REFERENCE.md#workflow-patterns) before writing Step 5. Select the smallest
pattern that preserves the real ordering, decisions, data flow, and stopping condition;
do not move branch-critical process state into a lookup file merely to shorten
`SKILL.md`.
