# Skill Composer Reference

Portable specifications, review gates, workflow patterns, and durable decision maps for Agent Skills.

Research target-specific facts on demand through
[HARNESS-RESEARCH.md](HARNESS-RESEARCH.md). This file owns portable rules and durable
decision guidance; it does not cache current paths, commands, UI flows, schema
extensions, or host behavior.

## Contents

- [YAML Frontmatter Specification](#yaml-frontmatter-specification)
- [Tool Pre-Approval](#tool-pre-approval)
- [Directory Structure Patterns](#directory-structure-patterns)
- [Exceptional Maintainer Specifications](#exceptional-maintainer-specifications)
- [Portable Core and Harness Enhancements](#portable-core-and-harness-enhancements)
- [Workflow Patterns](#workflow-patterns)
- [Skill Review Checklist](#skill-review-checklist)
- [Testing Methodology](#testing-methodology)
- [Troubleshooting](#troubleshooting)
- [Distribution](#distribution)
- [Portable Changelog Format](#portable-changelog-format)
- [Resources and Community](#resources-and-community)

## Skills and MCP Relationship

MCP supplies connectivity and callable tools; skills supply reusable instructions, workflow, and domain judgment. Either can stand alone, and a skill may coordinate built-in tools, MCP tools, or no tools at all.

| MCP (Connectivity) | Skills (Knowledge) |
|--------------------|--------------------|
| Connects an agent to a service | Teaches an agent how to use capabilities effectively |
| Provides real-time data access and tool invocation | Captures workflows and best practices |
| What an agent can do | How an agent should do it |

Model-invoked skills may load automatically from context; user-invoked skills run only when selected. Do not describe automatic activation as a property of every skill.

## YAML Frontmatter Specification

### Required Fields

```yaml
---
name: "skill-name"
description: "What it does and when to use it"
---
```

| Field | Type | Constraints |
|-------|------|-------------|
| `name` | string | 1-64 lowercase letters, digits, or hyphens; no leading, trailing, or consecutive hyphens; must match the parent directory. |
| `description` | string | 1-1024 chars; describes what the skill does and when to use it. |

### Optional Fields

```yaml
---
name: "skill-name"
description: "Description here"
allowed-tools: Read Grep Glob
license: MIT
compatibility: "Requires Git and a POSIX shell"
metadata:
  author: "Company Name"
  version: "1.0.0"
  mcp-server: server-name
  category: productivity
  tags: "project-management,automation"
  documentation: https://example.com/docs
  support: support@example.com
---
```

| Field | Type | Purpose |
|-------|------|---------|
| `allowed-tools` | string | Experimental, space-separated tool pre-approval; support varies by host |
| `license` | string | License name or bundled license file reference |
| `compatibility` | string | Environment requirements, 1-500 chars |
| `metadata` | object | Optional string-to-string extension map (author, version, mcp-server, etc.) |

### Target-Specific Validation

The portable specification and target harnesses may enforce different schemas. For a
named surface, use [Harness Research](HARNESS-RESEARCH.md) to establish its current
required and optional fields, restrictions, validation path, and treatment of portable
packages. Run both the portable validator and the named target's validator, and keep
verified target-only fields in an explicit harness enhancement.

## Tool Pre-Approval

In the portable specification, `allowed-tools` is experimental and contains a space-separated set of pre-approved tools. Support and syntax vary between agent implementations.

Before using it, research the named surface's current support, syntax, invocation scope,
and distinction between pre-approval and restriction. Omitting `allowed-tools` does not
define a portable permission policy; use the verified host permission mechanism when
actual restriction is required.

## Directory Structure Patterns

Every portable package root contains a file named exactly `SKILL.md`. Its parent
directory matches the portable `name` field and therefore follows the same lowercase
letter, digit, and hyphen constraints. Keep runtime instructions in `SKILL.md`, lookup
material in directly linked references, executable resources in `scripts/`, and output
templates or media in `assets/`. Add human-facing, maintainer, license, and release
files only when their admission or distribution condition applies; keep all required
dependencies and notices inside a standalone artifact.

### Minimal (Single File)

```
skill-name/
└── SKILL.md
```

All instructions in one file. Best for focused, simple skills.

### With References

```
skill-name/
├── SKILL.md
└── references/
    ├── api-guide.md
    └── examples.md
```

Core workflow in SKILL.md. Technical details and examples in references/.

### With Scripts

```
skill-name/
├── SKILL.md
├── references/
│   └── api-guide.md
└── scripts/
    ├── process.py
    └── validate.sh
```

Scripts for programmatic validation and utilities. Add `chmod +x` and a shebang only when a script is intended to run directly.

### Full-Featured

```
skill-name/
├── SKILL.md
├── references/
│   ├── api-guide.md
│   └── examples.md
├── scripts/
│   ├── process.py
│   └── validate.sh
└── assets/
    ├── template.json
    └── report-template.md
```

Maximum organization. Assets for templates, fonts, icons used in output.

### Script Requirements

Apply [Environment-Native Automation](SKILL.md#environment-native-automation) before these low-level packaging checks.

- Keep scripts self-contained or document every dependency and supported environment.
- Include helpful error messages, validate inputs, and handle expected edge cases.
- Use portable forward-slash paths in instructions and code unless the target is explicitly platform-specific.
- Add executable permissions and a shebang when the script is meant to run directly; neither is required for every bundled source file.
- Retain public-seam tests with the script and run them on every environment the skill claims to support.
- When a script is a harness enhancement rather than a declared requirement, provide and test a portable manual fallback for the core behavior.

## Exceptional Maintainer Specifications

The [Agent Skills specification](https://agentskills.io/specification#directory-structure) permits additional package files but assigns no portable meaning to `SPEC.md`. Skill Composer therefore treats it as an exceptional convention, reached through an explicit conditional pointer rather than assumed harness behavior. The default package has no `SPEC.md`.

Add `SPEC.md` only when every condition holds:

1. An explicit user requirement, repository rule, or authoritative product contract supplies at least one current requirement and the reason it must survive.
2. The requirement is stable across plausible implementation and harness changes.
3. It constrains modification or review, while ordinary skill execution does not need it.
4. A future rewrite could appear locally correct while silently violating it, and a separate maintenance contract materially reduces that risk.

Put principles, decision rules, routing, and completion criteria needed during normal execution in `SKILL.md`. Put branch-only lookup material in a referenced file and past changes in `CHANGELOG.md`. Skill importance, size, or complexity does not satisfy the admission test, and the absence of `SPEC.md` is the expected result for most skills.

A qualifying `SPEC.md` stays short and current-state. For every retained requirement, name the invariant, its enduring reason or concrete failure mode, and any validity boundary. Keep workflow steps and release narration in their runtime and history owners. In `SKILL.md`, add a pointer that loads the file before modifying or reviewing that skill itself; packaging the file alone does not make an agent read it.

A skill whose principles define every run, or whose routing rules are the workflow,
keeps those requirements in `SKILL.md` and does not qualify.

## Portable Core and Harness Enhancements

The portable-core decision is owned by [Portability](SKILL.md#portability). When Step 1
identifies a host hook, dynamic context source, subagent configuration, extra
frontmatter field, UI metadata, permission convenience, or another harness enhancement,
use this branch-only checklist. For every enhancement:

- name the harness and surface that support it;
- state what it improves;
- provide a portable fallback that preserves the core result; and
- test that the fallback works without the enhancement.

The fallback may be less convenient or less automated, but it must preserve the core
result. Do not store essential state only in a hook, rely on dynamic injection as the
sole source of required input, or make a host-only subagent the only executor unless
Step 1 explicitly records the package as host-specific.

## Workflow Patterns

Select a pattern only when it clarifies a real branch. Keep the resulting ordered
process and its local completion criteria in `SKILL.md`; this table is lookup material,
not a second workflow owner.

| Pattern | Select when the use case requires | Preserve explicitly |
|---|---|---|
| Sequential orchestration | Strict ordered dependencies | Inputs passed forward, per-step validation, and failure recovery |
| Multi-service coordination | One result spans several tools or MCP services | Service boundaries, data handoff, and the owner of partial failure |
| Iterative refinement | A measurable quality gate may require repeated work | Quality criterion, bounded loop, and stopping condition |
| Context-aware selection | The same outcome needs different tools by observable context | Decision inputs, one selected path, and fallback |
| Domain-specific intelligence | Domain rules decide whether or how an action may proceed | Rule source, decision boundary, audit output, and escalation path |

### Problem-First vs Tool-First

Think of it like Home Depot. You might walk in with a problem — "I need to fix a kitchen cabinet" — and an employee points you to the right tools. Or you might pick out a new drill and ask how to use it for your specific job.

Skills work the same way:

- **Problem-first**: "I need to set up a project workspace" — Your skill orchestrates the right MCP calls in the right sequence. Users describe outcomes; the skill handles the tools.
- **Tool-first**: "I have Notion MCP connected" — Your skill teaches the agent the optimal workflows and best practices. Users have access; the skill provides expertise.

Most skills lean one direction. Knowing which framing fits your use case helps you choose the right pattern below.

| Approach | User starts with | Skill provides | Best patterns |
|----------|-----------------|----------------|---------------|
| Problem-first | A goal or outcome | Tool orchestration, sequencing | Sequential Orchestration, Multi-MCP Coordination |
| Tool-first | An MCP or tool | Best practices, domain knowledge | Domain-Specific Intelligence, Context-Aware Selection |

## Skill Review Checklist

The ordered procedure and mutation boundary live in [Reviewing an Existing
Skill](SKILL.md#reviewing-an-existing-skill). During Review Step 5, use this branch-only
ledger to prove coverage without replaying the procedure. Record `Rule or branch |
Evidence | Result | Follow-up`; valid results are `pass`, `finding`, `not applicable`,
and `unknown`.

| Coverage area | Account for |
|---|---|
| Contract and scope | Request, repository rules, sources of truth, allowed mutations, targets and surfaces, invocation and distribution, real branches, portable core, host enhancements and fallbacks, and any qualifying `SPEC.md` authority and rationale |
| Package and trust | Every packaged file and local link; scripts, dependencies, binaries, generated or external content; network, credentials, dynamic downloads, broad access, provenance, integrity, and instruction-injection boundaries |
| Agent contract | Each branch's description pointer or explicit invocation path, ordered steps, reference reads, local completion criteria, terminology, failure behavior, progressive disclosure, duplicated or stale content, and current primary evidence for target claims |
| Validation and behavior | Portable and target validators, fresh activation and functional cases, realistic trigger boundaries, safe side-effect handling, portable fallback, each host enhancement, isolation, coexistence, and every claimed model and surface |
| Findings and release | Severity and file evidence, impact, smallest fix, objective completion criterion, facts versus inference and unknowns, affected reruns, semantic residue, and the applicable changelog evidence gate |

Never turn an uninspected file, unavailable validator, unsafe live side effect, or unrun
behavior case into a pass. Absence of `SPEC.md` or release artifacts is not a finding
when their admission conditions do not apply.

## Testing Methodology

There is no portable built-in evaluation runner. Run scenarios manually in the target host or build a repeatable harness. Start output-quality iteration with 2-3 cases tied to observed baseline gaps. For focused description tuning, aim for about 20 balanced trigger/non-trigger queries, run each multiple times (three is a reasonable start), and reserve fresh validation queries to detect overfitting. For enterprise release, require 3-5 representative queries covering trigger, non-trigger, and ambiguous cases. Expand every suite for real branches and risks, and test every deployed model.

### 1. Baseline and Expected Behavior

Run representative tasks without the skill first. Record the exact failure or missing context, then define observable expected behavior for the same tasks with the skill. Use fresh sessions so earlier skill content or conversation state does not contaminate results.

### 2. Triggering Tests

For model-invoked skills, test whether the host loads the skill at the right boundary. Negative cases must be realistic near-misses, not unrelated topics that test nothing.

```
Should trigger:
- "Initialize a ProjectHub workspace for Q4 planning"

Realistic near-miss:
- "Summarize the existing ProjectHub workspace" (when the skill only creates workspaces)

Ambiguous boundary:
- "Help me organize Q4 in ProjectHub"
```

State the expected activation or clarification behavior before running each case. Include paraphrases for every real branch.

### 3. Functional Tests

Goal: Correct outputs produced.

```
Test: Create project with 5 tasks
Given: Project name "Q4 Planning", 5 task descriptions
When: Skill executes workflow
Then:
- Project created
- 5 tasks with correct properties
- All tasks linked to project
- No API errors
```

### 4. Isolation and Coexistence

Run the skill alone, then alongside the skills most likely to overlap. Verify the new skill does not steal unrelated triggers, suppress another skill, or depend on another installed skill unless that dependency is explicit. For a cross-agent skill, disable host enhancements and verify the portable fallback preserves the core result.

### 5. Performance Comparison

Goal: Skill improves over baseline.

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 15 | 2 clarifying questions |
| Failed API calls | 3 requiring retry | 0 |
| Tokens consumed | 12,000 | 6,000 |

Use your success criteria measurements to populate this table only after correctness
passes. Manual and scripted approaches are both valid; verify any target-specific
authoring or evaluation helper before relying on it.

### Iteration Signals

**Undertriggering** (skill doesn't load when it should):
- Users manually enabling it
- Support questions about when to use it
- Fix: Identify the missing usage branch and add or sharpen one discriminating pointer using observed user language

**Overtriggering** (skill loads for unrelated queries):
- Users disabling it
- Confusion about purpose
- Fix: Narrow the positive context pointer and test the nearest competing branch; use an explicit prohibition only when a positive boundary cannot express the rule

#### Execution Issues

Symptoms: inconsistent results, API call failures, user corrections needed.
- Workflows produce different outputs for the same input
- MCP tool calls fail intermittently
- Users need to manually correct or retry

Fix: Improve instructions with more explicit steps, add error handling for common failure modes, and include retry logic or fallback approaches for unreliable operations.

## Troubleshooting

### Package or Validation Failure

1. Confirm the package contains `SKILL.md` at its expected root with exact casing.
2. Check YAML delimiters, indentation, value types, and the portable name constraints.
3. Use [Harness Research](HARNESS-RESEARCH.md) to interpret the named surface's current
   diagnostic and validator behavior.

### Skill Doesn't Trigger

Quick checks:
- Is description too generic? ("Helps with projects" won't work)
- Does it include trigger phrases users would actually say?
- Does it mention relevant file types?

Run an actual activation case in a fresh session. A model repeating the description only proves that it can read the text.

### Skill Triggers Too Often

1. Be more specific: `"PDF legal documents for contract review"` not `"documents"`
2. Give each real branch one discriminating context pointer and remove synonym lists that add no distinction
3. Test the nearest competing skill or same-domain near-miss, then refine the positive boundary

### Instructions Not Followed

1. Reproduce the failure in a fresh session and identify the first skipped or misread branch.
2. Replace ambiguity such as "validate things properly" with an ordered action and observable completion criterion.
3. Co-locate the rule with the step it governs; move only lookup material into a reference with an explicit read condition.
4. Remove competing options, duplicate rules, and no-op encouragement that cannot change the decision path.

### Large Context Issues

Symptoms: Slow responses, degraded quality.

Solutions:
1. Use **500 lines** or **5,000 tokens** as investigation heuristics, not universal acceptance limits. Move branch-only lookup material to focused references only when behavior and information ownership remain intact.
2. Measure recall on the actual target as skills are added; use the surface's currently documented cap instead of a generic count.
3. Ensure progressive disclosure is working and reference reads have explicit conditions.

### Skill Packs

If you have many related capabilities, consider grouping them into a **skill pack** — a single skill that bundles related functions together. This can reduce the number of simultaneously enabled skills and help the host select the right capability.

Consolidate only when coexistence evaluations show trigger conflicts or recall degradation and the combined skill preserves equal behavior. Shared domain or an arbitrary skill count alone is not enough.

### MCP Connection Issues

1. Use [Harness Research](HARNESS-RESEARCH.md) to identify the named host's current connector or status diagnostic.
2. Check authentication (API keys valid, proper scopes)
3. Test MCP independently by asking the agent to call it without the skill
4. Verify tool names match MCP server documentation (case-sensitive)

## Distribution

Treat each harness and product surface as a separate compatibility surface. Before
choosing a package layout or writing installation guidance, resolve these decisions
through [Harness Research](HARNESS-RESEARCH.md):

| Decision | Establish |
|---|---|
| Scope | Repository or project, personal, workspace or organization, and the owner of each installation |
| Delivery | Folder, archive, plugin or marketplace, API or SDK, and the exact artifact each surface consumes |
| Discovery and invocation | Current location or enablement path, selection mode, and any session reload requirement |
| Update lifecycle | Who publishes updates, whether recipients receive them, and which version identifier is authoritative |
| Validation | Portable and target validators, clean-install procedure, and representative behavior cases |

Record exact current paths, commands, UI steps, and host behavior in the task evidence
and in a target-specific release artifact only when its users need them. A folder on
disk or a validator pass does not prove that an active session discovered the skill;
test the exact built artifact independently on every claimed surface.

### Repository and Standalone Distribution

- Use a repository-level README for a collection and a skill-local README for an
  independently distributed skill's human-facing installation or compatibility notes.
- Keep runtime instructions in `SKILL.md`; do not duplicate them in a README.
- Keep independently distributed release artifacts, dependencies, and the Skill
  Composer changelog inside the skill folder.
- Produce only the delivery artifacts the verified target consumes.
- Link from MCP documentation when the skill enhances that MCP.

### Positioning Your Skill

How you describe your skill determines whether users understand its value and actually try it. When writing about your skill — in your README, documentation, or marketing — keep these principles in mind.

**Focus on outcomes, not features:**

Good: *"The ProjectHub skill enables teams to set up complete project workspaces in seconds — including pages, databases, and templates — instead of spending 30 minutes on manual setup."*

Bad: *"The ProjectHub skill is a folder containing YAML frontmatter and Markdown instructions that calls our MCP server tools."*

**Highlight the MCP + skills story:**

*"Our MCP server gives the agent access to your project system. Our skills teach the agent your team's planning workflow. Together, they provide consistent tool-assisted project management."*

### Document in Your MCP Repo

If you maintain an MCP server, link to your skills from the MCP documentation:

- Link to skills from MCP documentation
- Explain the value of using both together
- Provide a quick-start guide that covers MCP setup and skill installation

## Portable Changelog Format

Use a skill-local `CHANGELOG.md` when a skill has releases of its own or may be distributed without its source repository. Git history is not a sufficient release record: one commit may modify several skills, and an installed or copied skill may have no Git metadata.

Keep the changelog outside `SKILL.md` so historical narration does not consume runtime context. Package it with the skill, update it in the same change as released behavior, and record only changes that matter to a user, integrator, or downstream maintainer. Omit it for unpublished, single-use skills until there is a real release history to preserve.

### Evidence gate

Evidence outranks the desire to fill every field. Write a changelog claim only when it is directly supported by at least one traceable source:

- the user's explicit explanation in the current conversation or a retrievable earlier conversation;
- a requirement or specification;
- observed diff or code;
- test or log output; or
- an existing release record, limited to what that record actually says.

A historical conversation can establish why the user chose a separate file, boundary, or workflow even when the current request only says to implement it. Preserve that explicit reason. Do not promote an agent's plausible interpretation of the conversation into the user's rationale, and do not use the changelog entry being written as evidence for itself.

De-identification is transformation, not invention. Rename sensitive details while preserving the evidenced actors, states, sequence, and consequence. Use a minimal code, config, payload, or diff excerpt when one was observed. A reconstruction may express an explicitly described code pattern, but it must not introduce behavior or causality that the source did not establish. When only the reason is known, use concrete prose instead of manufacturing code.

If the evidence does not establish a `Why`, preserve the supported facts, report what evidence is missing, and do not claim the new entry is complete. An `Example` is optional: omit it when it would not materially improve understanding or when the evidence cannot support it. When importing legacy entries that lack enough evidence, keep their recorded facts and identify them as legacy history rather than backfilling a plausible story.

Once the evidence gate passes, include for every complete new logical change inside a release:

- **Changed** (required): the behavior, rule, contract, or compatibility surface that changed.
- **Why** (required): the failure mode, missing invariant, or distribution constraint that made the change necessary.
- **Example** (optional): include the causal pre-change pattern and its consequence only when it makes the decision materially easier to understand than `Changed` and `Why` alone. Prefer the smallest reconstructed code, config, payload, or diff snippet that makes the missing relationship obvious; use concrete prose when code would add no clarity. Show before and after only when the contrast helps explain the decision.
- **Migration** (optional): include only when a user or downstream integrator must act.

Use this inclusion test: remove the proposed `Example` and reread `Changed` plus `Why`. If the causal pattern, consequence, and reason for the decision remain equally clear, omit the example.

During review, run this test against every retained `Example`, including examples outside the current diff. Existing text is not grandfathered: remove any example that no longer adds material understanding.

When included, write the heading as `Example` and de-identify its contents. Replace project, customer, ticket, repository, path, symbol, route, event, and real payload names with neutral ones. Preserve structural roles such as caller, owner, gate, optimizer, or compatibility boundary because they carry the rationale. Reconstruct the smallest faithful example instead of copying proprietary code verbatim. If a changelog contains examples, state in its preamble that they are de-identified, evidence-backed reconstructions.

An example documents what caused the change; it is not a usage demo or a mandatory restatement of the new behavior.

````markdown
# Changelog

Examples, when included, are de-identified, evidence-backed reconstructions of the patterns that motivated each change.

## [2.0.0] - 2025-11-15

### Preserve decision-relevant facts

- **Changed:** Callers now pass every distinction the owning surface may need.
- **Why:** Selecting one value early made valid states indistinguishable and prevented the owner from deciding correctly.
- **Example:**

  ```ts
  declare const candidates: Candidate[] | undefined;
  const choice = candidates?.[0] ?? null;
  owner.decide(choice);
  ```

  This reduces one or many candidates to one value and collapses both an empty result and an unavailable result to `null`.
- **Migration:** Pass the complete candidate result to the owner.
````

Semantic versioning: Major (breaking), Minor (features, backward compatible), Patch (bug fixes).

## Resources and Community

If you're building your first skill, start with the portable rules in this package. Use [Harness Research](HARNESS-RESEARCH.md) to locate fresh target guidance only when a target-specific branch requires it.

### Current Documentation

Use the trust anchors and source-selection procedure in [Harness
Research](HARNESS-RESEARCH.md). This reference deliberately does not cache current
target instructions or remembered vendor URLs.

### Background

- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — the original architecture discussion and later open-standard update

### Public Skills Repository

GitHub: [anthropics/skills](https://github.com/anthropics/skills) — Contains Anthropic-created skills you can browse and customize. Use these as reference implementations when building your own.

### Auxiliary Skill-Authoring Helpers

A harness may inject `skill-creator` or an analogous helper. Use a helper for capabilities tied to that harness, such as scaffolding, schema validation, or isolated evaluation. Treat its general authoring advice as advisory and apply the [Authoring Authority](SKILL.md#authoring-authority) rule before accepting it.

In particular, do not let a helper's generic packaging preference erase an explicit portable-release requirement. Verify which statements are real target-platform constraints; keep the rest subordinate to Skill Composer's design policy.

### Getting Support

**For technical questions:**
- Community forums at the [Claude Developers Discord](https://discord.gg/claudedev) — general questions, best practices, sharing skills

**For bug reports:**
- GitHub Issues: [anthropics/skills/issues](https://github.com/anthropics/skills/issues)
- Include: skill name, error message, steps to reproduce
