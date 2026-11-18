---
name: skill-composer
description: "Use when the user asks to create a new Agent Skill, revise an existing skill's authored behavior or activation, audit a complete skill package, design its eval suite, port it across agent harnesses, or prepare and validate its release. When a generic skill-authoring helper overlaps, this skill owns scope, structure, portability, validation, and release history. If the work neither changes nor audits an Agent Skill package, do not load this skill."
license: LICENSE.md
---

# Skill Composer

When modifying, reviewing, testing, or releasing Skill Composer itself, first read [SPEC.md](SPEC.md) in full. Otherwise do not inspect its eval manifests, fixtures, package tests, or eval runner implementation; Step 7 says when to run its scripts' public CLIs, and the target needs no runner copy.

## Authoring Authority

Skill Composer owns skill-authoring policy. Use an injected helper such as `skill-creator` only for platform scaffolding, schema validation, or evaluation; its authoring advice is advisory, but a target's verified format requirement binds.

## Core Design Principles

### Bounded Entry Point

These rules apply to every skill you create, update, or review:

- `SKILL.md` stays within **15,000 bytes** ([why](SPEC.md)).
- Keep every standing rule (one that applies across a whole run) in `SKILL.md`, must-follow gates first. A reference holds one branch's workflow or lookup material.
- Point at whole reference files, each with its read condition, and tell the agent to read the file in full.
- Point to another skill by telling the agent to **invoke it by name through the host's skill mechanism** (in Claude Code, the Skill tool). **Reading its `SKILL.md` with a file tool is not invocation**: an agent reading the file tends to take only part of it and miss gates written elsewhere ([why](SPEC.md)).
- Script what a script can check; state the rest once as a terse requirement with at most its core reason; put detailed explanation in a reference or `SPEC.md` behind a link.

Within the cap, every passage still earns its place.

### Portability

Required behavior, the **portable core** (goal, inputs, outputs, decision rules, workflow, failure behavior, completion criteria), must run without host-only features. Give each **harness enhancement** a named host and a tested portable fallback; require a host-only feature only when the description and compatibility contract declare that host.

**Harness research:** before creating, changing, or reviewing a target-specific claim about discovery, schema, invocation, permissions, hooks, installation, packaging, validation, or host enhancements, read [HARNESS-RESEARCH.md](HARNESS-RESEARCH.md) in full. A portable core that names multiple compatible harnesses remains portable-only when it encodes no harness-specific fact; skip research then.

Never scan home or user-level skill directories for examples, validators, or target evidence. Use the workspace, a validator command the package or primary documentation names, and primary target documentation. Do not enumerate `PATH`, installation directories, or language package registries to hunt for validators; record a missing validator as `unknown`.

### Environment-Native Automation

Script repeated, deterministic mechanics with stable inputs and outputs; keep judgment in instructions. Before adding or changing a script, read [references/package-layout.md](references/package-layout.md) in full. Invoke the `tdd` skill by name when available and follow it; otherwise follow the red-green loop in that file.

## Choose the Workflow

- **Create:** plan in [Planning Before Creating or Updating](#planning-before-creating-or-updating), then follow [Creating or Updating a Skill](#creating-or-updating-a-skill) in order.
- **Update:** inventory the current package, lock its behavior contract, and record its passing baseline. If the inventory contains `evals/evals.json` or `evals/trigger-eval.json`, or the user explicitly asks for eval work, read the [Evaluation Reference](references/evaluation.md) in full before editing the target. Otherwise keep that reference unopened. Then follow [Planning Before Creating or Updating](#planning-before-creating-or-updating) and the affected steps; preserve unrelated behavior and user-owned files, and remove what a retired concept leaves behind.
- **Review:** read [references/review.md](references/review.md) in full and follow it. Stay read-only unless the user authorizes fixes; enter the update branch only after reporting findings.
- **Package or release:** after the package is complete, read [references/release.md](references/release.md) in full and follow it.

**Done when:** the request has one selected workflow and combined operations have explicit transitions.

## Planning Before Creating or Updating

Write one concrete use case for every real usage branch: trigger, ordered steps, required tools or domain rules, and observable result. Do not invent cases to meet a quota. When the shape is unclear, read [references/authoring-examples.md](references/authoring-examples.md) in full.

Before writing instructions, run representative tasks without the skill when a baseline matters and choose proportionate evidence (existing tests or evals, disposable manual scenarios, target-host checks); rerun the same checks after writing. For a model-invoked skill, include near-miss and ambiguous trigger cases. Compare efficiency only after correctness.

Run evaluations against a disposable fixture or sandbox. A real API write, outbound message, charge, publication, irreversible effect, or live call that spends credentials, quota, or paid tokens needs explicit user authorization for that effect and a cleanup plan; otherwise use a fixture and keep live behavior `unknown`.

**Done when:** every usage branch has a use case with a checkable result that can be rerun, and every external side effect is isolated, authorized, or `unknown`.

## Creating or Updating a Skill

### Step 1: Choose Target and Scope

Name the target harness, surface, invocation mode, and distribution form. Read [references/distribution.md](references/distribution.md) in full for scope, delivery, discovery, updates, and validation. When the skill has a host enhancement or MCP dependency, read [references/portability.md](references/portability.md) in full.

**Done when:** target, surface, invocation policy, distribution form, portable core, and every enhancement or host requirement are named without an unsupported compatibility claim.

### Step 2: Create File Structure

Keep an update's structure unless the change requires otherwise. Before changing layout, read [references/package-layout.md](references/package-layout.md) in full and choose the smallest pattern that fits within the [Bounded Entry Point](#bounded-entry-point). Add `SPEC.md` only when it passes that file's admission test.

**Done when:** every file has one purpose and owner, and unrelated user-owned files are preserved.

### Step 3: Write YAML Frontmatter

Read [references/frontmatter.md](references/frontmatter.md) in full.

**Done when:** frontmatter satisfies the portable schema, every extension traces to target evidence, both applicable validators pass or are `unknown`, and any `allowed-tools` has surface evidence and is not presented as a portable restriction.

### Step 4: Write the Description

Make the skill model-invoked only when the agent or another skill must reach it unprompted, which trades the user's cognitive load for context load on every turn; prefer explicit invocation when timing or side effects need deliberate control. Give each model-invoked branch one discriminating trigger in users' words; add a negative boundary only for a realistic near-neighbor, and test it. For description examples, read [references/authoring-examples.md](references/authoring-examples.md) in full.

**Done when:** the invocation policy is explicit, each model-invoked branch has one tested pointer and boundary, and target controls have evidence or are `unknown`.

### Step 5: Write Instructions

When the `writing-for-agents` skill is available, invoke it by name and follow it; otherwise read [references/writing.md](references/writing.md) in full and follow it. Add troubleshooting or examples only for an evidenced branch. For a starting shape, read [references/authoring-examples.md](references/authoring-examples.md) in full; when the use cases imply no instruction shape, also read [references/workflow-patterns.md](references/workflow-patterns.md) in full.

**Done when:** `writing-for-agents` or `references/writing.md` was applied, every branch has an ordered path, every step has a completion criterion, every reference has a read condition, and failure behavior is defined where an operation can fail.

### Step 6: Record Portable Release History

When the skill has its own releases or independent distribution, update its `CHANGELOG.md` in the same change. First read [references/changelog.md](references/changelog.md) in full and follow it.

**Done when:** the mode follows the reference, each entry passes the Evidence gate, and runtime instructions hold no release history.

### Step 7: Validate Behavior and Maintain Admitted Evals

Packaged evals are opt-in:

- When the user explicitly asks to add or change evals, build the smallest suite covering the request.
- When the target already contains an eval suite, preserve it and update affected existing cases; add a case only for changed behavior or an uncovered branch.
- Otherwise do not create eval manifests, fixtures, or runner copies. If a material risk warrants repeatable evals, recommend the smallest useful suite and ask the user before adding it.

In that last branch, do not search, grep, or open the Evaluation Reference, and do not inspect or invoke `eval-skill.py`. Before creating, updating, running, tuning, or maintaining an admitted eval suite, read the [Evaluation Reference](references/evaluation.md) in full.

Run the **package check** on every target you create or update: `python3 <this skill's directory>/scripts/check-skill.py <target-skill-dir>`. Fix every finding and rerun it to `OK`. Without Python, apply the checks its docstring lists by hand, recording any left unchecked as `unknown`.

Keep one **validation ledger** listing every applicable gate: the package check, package and target schema, bundled tests, fresh-session behavior, the portable fallback, clean installation when packaging, and the eval contract when admitted. Derive its rows from the locked package inventory, accounting for every discovered test entry point and executable script, with its baseline result before editing and final evidence whether retained, replaced, or removed; keep unrun baseline behavior as `unknown`. Each row is `pass`, `fail`, or `unknown` with evidence; add gates found later.

Run affected behavior scenarios in a fresh session, through a verified target adapter or manually, and the full owned suite before release.

Frontmatter, body, changelog, and final report may call a target verified, supported, or tested only when its matching target-behavior ledger row is `pass`. Static schema validation, a manual walkthrough, or a pass on another target is not behavior proof.

When a check fails, read [references/troubleshooting.md](references/troubleshooting.md) in full. Report every row in the final response; the overall result is green only when every required row passes.

**Done when:** every branch has an observable validation result, every gate is `pass`, `fail`, or `unknown`, unsafe or unavailable checks stay visible, and an admitted suite passes its contract and affected cases.
