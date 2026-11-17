---
name: skill-composer
description: "Use when the user asks to create a new Agent Skill, revise an existing skill's authored behavior or activation, audit a complete skill package, design its eval suite, port it across agent harnesses, or prepare and validate its release. When a generic skill-authoring helper overlaps, this skill owns scope, structure, portability, validation, and release history. If the work neither changes nor audits an Agent Skill package, do not load this skill."
license: LICENSE.md
---

# Skill Composer

Create well-structured, discoverable agent skills from the current Agent Skills specification, target-platform documentation, and community practice.

When modifying or reviewing Skill Composer itself, read [SPEC.md](SPEC.md) first. It holds maintainer-only requirements; ordinary skill-authoring tasks do not need it.

Skill Composer's own eval manifests, fixtures, package tests, and eval runner's
implementation are maintainer evidence. Do not inspect them while using Skill Composer
to author another skill. The runner's documented public CLI is a shared validator, and
Step 8 owns when to invoke that CLI. The target is not expected to contain a runner
copy; invoke the public seam without inspecting the runner implementation. Read
maintainer evidence only when asked to modify, review, test, or release Skill Composer
itself.

## Authoring Authority

Skill Composer owns skill-authoring policy whenever a task creates or changes a skill. Use an injected helper such as `skill-creator` for platform scaffolding, schema validation, or evaluation, but treat its authoring defaults as advisory; it does not decide scope, structure, packaging, release history, or quality. A target's verified format requirement stays a compatibility constraint. This precedence never overrides the host's safety, permission, or instruction hierarchy.

## Core Design Principles

### Bounded Entry Point

These rules apply to every skill you create, update, or review:

- `SKILL.md` is at most **15,000 UTF-8 bytes**, frontmatter included. Measure it with `wc -c SKILL.md`; a larger file fails validation. Hosts may keep only the start of an invoked skill once context is compacted ([why](SPEC.md#bounded-entry-point)).
- Keep every standing rule (one that applies across a whole run) in `SKILL.md`, must-follow gates first. A reference holds one branch's workflow or lookup material and can drop out of context.
- Point at whole reference files, each with its read condition, and tell the agent to read the file in full. Split a reference that would need a section anchor.
- Point to another skill by telling the agent to invoke it by name.

Within the cap, every passage still earns its place.

### Progressive Disclosure

Frontmatter supports discovery, the `SKILL.md` body loads on invocation, and linked files load only when a branch needs them. Discovery and content lifecycle are target-specific; verify them per harness.

### Composability

Skills coexist with others and never assume they are alone. Optionally compose with Matt Pocock's [writing-for-agents](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents) when the user requests it or both skills are invoked. Do not seek or load it merely because it is installed, and do not make the result depend on it.

### Portability

Default to a **portable core** (goal, inputs, outputs, decision rules, workflow, failure behavior, completion criteria) plus **harness enhancements** (hooks, dynamic context, subagents, UI metadata, permission conveniences). Name each enhancement's host and give it a portable fallback. A skill may require a host-only feature only when its description and compatibility contract say so.

**Harness research:** before creating, changing, or reviewing a target-specific claim about discovery, schema, invocation, permissions, hooks, installation, packaging, validation, or host enhancements, read [HARNESS-RESEARCH.md](HARNESS-RESEARCH.md) in full and build fresh evidence. A portable core that names multiple compatible harnesses remains portable-only when it encodes no harness-specific fact; skip research then.

Never scan home or user-level skill directories for examples, validators, or target evidence. Use the workspace, a validator command the package or primary documentation names, and primary target documentation. Do not enumerate `PATH`, installation directories, or language package registries to hunt for validators; record a missing validator as `unknown`.

### Environment-Native Automation

Script repeated, deterministic mechanics with stable inputs and outputs; keep judgment in instructions. Name the public seam and invoke the `tdd` skill when available, or apply its loop directly: run the public-seam test and preserve its observed failure before writing the implementation, then make the minimum change and rerun the same test to green. Choose a runtime every claimed environment already provides, add a dependency only when it removes more than it costs, and keep a portable manual fallback for host-enhancement scripts. Before adding a script, read [references/package-layout.md](references/package-layout.md) in full.

## Choose the Workflow

- **Create:** plan in [Planning Before Creating or Updating](#planning-before-creating-or-updating), then follow [Creating or Updating a Skill](#creating-or-updating-a-skill) in order.
- **Update:** inventory the current package and lock its contract. If the inventory contains `evals/evals.json` or `evals/trigger-eval.json`, or the user explicitly asks for eval work, read the [Evaluation Reference](references/evaluation.md) before editing the target and enter Step 8 for that branch. Otherwise keep that reference unopened. Then follow [Planning Before Creating or Updating](#planning-before-creating-or-updating) and the affected steps; preserve and update affected regression cases.
- **Review:** read [references/review.md](references/review.md) in full and follow it. Stay read-only unless the user authorizes fixes; enter the update branch only after reporting findings.
- **Package or release:** after the package is complete, read [references/release.md](references/release.md) in full and follow it. Packaging does not prove activation or runtime behavior.

**Done when:** the request has one selected workflow, combined operations have explicit transitions, and no review silently becomes an edit.

## Planning Before Creating or Updating

Write one concrete use case for every real usage branch: trigger, ordered steps, required tools or domain rules, and observable result. Do not invent cases to meet a quota. When the shape is unclear, read [references/authoring-examples.md](references/authoring-examples.md).

Define success before writing instructions. Run representative tasks without the skill when a baseline matters, give each use case a checkable result, choose proportionate evidence (existing tests or evals, disposable manual scenarios, target-host checks), write the minimum instructions, then rerun the same checks. For a model-invoked skill, cover intended triggers, near-misses, and ambiguous cases. Compare efficiency only after correctness.

Run evaluations against a disposable fixture or sandbox. A real API write, outbound message, charge, publication, or irreversible effect needs explicit user authorization for that effect and a cleanup plan; otherwise use a fixture and keep live behavior `unknown`.

**Done when:** every usage branch has a use case with a checkable result that can be rerun, and every external side effect is isolated, authorized, or `unknown`.

## Creating or Updating a Skill

For an update, first capture the package inventory, behavior contract, and passing baseline; preserve unrelated behavior and user-owned files, and remove what a retired concept leaves behind.

### Step 1: Choose Target and Scope

Name the target harness, surface, invocation mode, and distribution form. Define the portable core, then add verified enhancements with fallbacks. Read [references/distribution.md](references/distribution.md) for scope, delivery, discovery, updates, and validation. When the skill has a host enhancement or MCP dependency, read [references/portability.md](references/portability.md).

**Done when:** target, surface, invocation policy, distribution form, portable core, and every enhancement or host requirement are named without an unsupported compatibility claim.

### Step 2: Create File Structure

Keep an update's structure unless the change requires otherwise. Before changing layout, read [references/package-layout.md](references/package-layout.md) and choose the smallest pattern that fits within the [Bounded Entry Point](#bounded-entry-point). Add `SPEC.md` only when it passes that file's admission test; add no human-facing file that repeats runtime instructions.

**Done when:** every file has one purpose and owner, `SKILL.md` is within 15,000 bytes, unrelated user-owned files are preserved, and all packaged links resolve inside the package.

### Step 3: Write YAML Frontmatter

Read [references/frontmatter.md](references/frontmatter.md). Write portable fields first; add a target-only field only with fresh research evidence.

**Done when:** frontmatter satisfies the portable schema, every extension traces to target evidence, and both applicable validators pass or are `unknown`.

### Step 4: Write the Description

Decide whether automatic model invocation is safe and useful. It reduces user cognitive load but spends discovery context load. Prefer explicit invocation when timing or side effects need deliberate control. A host that offers both adds a capability, not a third information architecture strategy.

Pattern: `[What it does] + [When to use it] + [Key capabilities]`. Give each model-invoked branch one discriminating pointer in users' words (file types, actions, domain terms). Add a negative boundary only for a realistic near-neighbor, and test it.

**Done when:** the invocation policy is explicit, each model-invoked branch has one tested pointer and boundary, and target controls have evidence or are `unknown`.

### Step 5: Write Instructions

Write ordered, specific steps with critical rules first; every step ends with **Done when:** and a checkable, exhaustive criterion. Put each rule beside the step it governs, give every reference a read condition, and add troubleshooting or examples only for an evidenced branch. For a starting shape or description examples, read [references/authoring-examples.md](references/authoring-examples.md).

**Done when:** every branch has an ordered path, every step has a completion criterion, every reference has a read condition, and failure behavior is defined where an operation can fail.

### Step 6: Consider Tool Pre-Approval

`allowed-tools` is experimental and host-specific. Before adding it, research the surface and read [references/frontmatter.md](references/frontmatter.md).

**Done when:** pre-approval is omitted, or each declaration has surface evidence and is not presented as a portable restriction.

### Step 7: Record Portable Release History

When the skill has its own releases or independent distribution, update its `CHANGELOG.md` in the same change. First read [references/changelog.md](references/changelog.md) in full: it selects date or version mode and holds the Evidence gate. Record each logical change once with `Changed` and `Why`.

**Done when:** the mode follows the reference, each entry passes the Evidence gate, and runtime instructions hold no release history.

### Step 8: Validate Behavior and Maintain Admitted Evals

Packaged evals are opt-in:

- When the user explicitly asks to add or change evals, build the smallest suite covering the request.
- When the target already contains an eval suite, preserve it and update affected existing cases; add a case only for changed behavior or an uncovered branch.
- Otherwise do not create eval manifests, fixtures, or runner copies. If a material risk warrants repeatable evals, recommend the smallest useful suite and ask the user before adding it.

In that last branch, do not search, grep, or open the Evaluation Reference, and do not inspect or invoke `eval-skill.py`; its `check` validates admitted eval contracts and is not a general package or target schema validator. Use the portable schema validator, any named target validator, bundled tests, and manual behavior checks. Before creating, updating, running, tuning, or maintaining an admitted eval suite, read the [Evaluation Reference](references/evaluation.md) in full.

Keep one **validation ledger** listing every applicable gate: the entry-point byte cap, package and target schema, bundled tests, fresh-session behavior, the portable fallback, clean installation when packaging, and the eval contract when admitted. Derive its rows from the locked package inventory, accounting for every discovered test entry point and executable script, with its baseline result before editing and final evidence whether retained, replaced, or removed; keep unrun baseline behavior as `unknown`. Each row is `pass`, `fail`, or `unknown` with evidence; add gates found later, and treat an absent or unrun gate as incomplete.

Run affected behavior scenarios in a fresh session, through a verified target adapter or manually, and the full owned suite before release.

Frontmatter, body, changelog, and final report may call a target verified, supported, or tested only when its matching target-behavior ledger row is `pass`. Static schema validation, a manual walkthrough, or a pass on another target is not behavior proof. Live calls that spend credentials, quota, or paid tokens need explicit user authorization.

When a check fails, read [references/troubleshooting.md](references/troubleshooting.md). Report every row in the final response; the overall result is green only when every required row passes.

**Done when:** every branch has an observable validation result, every gate is `pass`, `fail`, or `unknown`, unsafe or unavailable checks stay visible, and an admitted suite passes its contract and affected cases.

## Workflow Patterns

When the use cases do not imply an instruction shape, read [references/workflow-patterns.md](references/workflow-patterns.md) before Step 5 and choose the smallest pattern that keeps ordering, decisions, and stopping conditions in `SKILL.md`.
