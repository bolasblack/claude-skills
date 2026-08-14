# Skill Composer Reference

Technical specifications, review gates, workflow patterns, and target-specific notes for Agent Skills.

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
- [Invocation Modes](#invocation-modes)
- [Portable Changelog Format](#portable-changelog-format)
- [Skill Examples](#skill-examples)
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
compatibility: "Requires Claude Code with bash access"
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

The portable specification and target harnesses may enforce different schemas. Validate both when packaging for a named surface. For Anthropic upload surfaces, `name` must not contain the reserved words `claude` or `anthropic`, and `name` and `description` must not contain XML tags. Claude Code accepts additional frontmatter fields that fail on claude.ai and API upload paths, so label those fields as Claude Code-only.

## Tool Pre-Approval

In the portable specification, `allowed-tools` is experimental and contains a space-separated set of pre-approved tools. Support and syntax vary between agent implementations.

In Claude Code, the field pre-approves listed tools for the turn in which the skill is invoked. It does not restrict or remove unlisted tools. Use Claude Code permission or deny rules for actual restrictions. The field does not apply to Agent SDK skills; configure SDK tool approval in the SDK options instead.

### Claude Code Pre-Approval Examples

**Read-only analysis** (code review, security audits):
```yaml
allowed-tools: Read Grep Glob
```

**Research only** (information gathering, docs lookup):
```yaml
allowed-tools: Read WebFetch WebSearch Grep Glob
```

**Pre-approved file operations**:
```yaml
allowed-tools: Read Write
```

**Scoped bash with web** (specific interpreters only):
```yaml
allowed-tools: "Bash(python:*) Bash(npm:*) WebFetch"
```

Omitting `allowed-tools` does not define a portable permission policy; the host's normal permissions still apply.

## Directory Structure Patterns

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

- Keep scripts self-contained or document every dependency and supported environment.
- Include helpful error messages, validate inputs, and handle expected edge cases.
- Use portable forward-slash paths in instructions and code unless the target is explicitly platform-specific.
- Add executable permissions and a shebang when the script is meant to run directly; neither is required for every bundled source file.
- Test scripts on every environment the skill claims to support.

## Exceptional Maintainer Specifications

The [Agent Skills specification](https://agentskills.io/specification#directory-structure) permits additional package files but assigns no portable meaning to `SPEC.md`. Skill Composer therefore treats it as an exceptional convention, reached through an explicit conditional pointer rather than assumed harness behavior. The default package has no `SPEC.md`.

Add `SPEC.md` only when every condition holds:

1. An explicit user requirement, repository rule, or authoritative product contract supplies at least one current requirement and the reason it must survive.
2. The requirement is stable across plausible implementation and harness changes.
3. It constrains modification or review, while ordinary skill execution does not need it.
4. A future rewrite could appear locally correct while silently violating it, and a separate maintenance contract materially reduces that risk.

Put principles, decision rules, routing, and completion criteria needed during normal execution in `SKILL.md`. Put branch-only lookup material in a referenced file and past changes in `CHANGELOG.md`. Skill importance, size, or complexity does not satisfy the admission test, and the absence of `SPEC.md` is the expected result for most skills.

A qualifying `SPEC.md` stays short and current-state. For every retained requirement, name the invariant, its enduring reason or concrete failure mode, and any validity boundary. Keep workflow steps and release narration in their runtime and history owners. In `SKILL.md`, add a pointer that loads the file before modifying or reviewing that skill itself; packaging the file alone does not make an agent read it.

Skill Composer itself qualifies because its output-level portability, context-footprint, and maintenance-context requirements must constrain future rewrites while ordinary authoring runs do not need its self-maintenance contract. A skill whose principles define every run, or whose routing rules are the workflow, keeps those requirements in `SKILL.md` and does not qualify.

## Portable Core and Harness Enhancements

Cross-agent skills have two layers:

1. **Portable core:** goal, inputs, outputs, decisions, ordered steps, failure behavior, and completion criteria that compatible agents can execute without host-only features.
2. **Harness enhancements:** optional integrations such as Claude Code hooks, dynamic context, subagent configuration, extra frontmatter, UI metadata, or permission pre-approval.

For every enhancement:

- name the harness and surface that support it;
- state what it improves;
- provide a portable fallback that preserves the core result; and
- test that the fallback works without the enhancement.

The fallback may be less convenient or less automated, but it must preserve the core contract. Do not store essential state only in a hook, rely on dynamic injection as the sole source of required input, or make a host-only subagent the only executor of a portable workflow.

An intentionally host-specific skill is the exception. State the host requirement in its description and compatibility documentation, then review it against that host rather than claiming cross-agent support.

## Workflow Patterns

### Pattern 1: Sequential Orchestration

**Use when**: Multi-step processes in a specific order.

```markdown
## Workflow: Onboard New Customer

### Step 1: Create Account
Call tool: `create_customer`
Parameters: name, email, company

### Step 2: Setup Payment
Call tool: `setup_payment_method`
Wait for: payment method verification

### Step 3: Create Subscription
Call tool: `create_subscription`
Parameters: plan_id, customer_id (from Step 1)

### Step 4: Send Welcome Email
Call tool: `send_email`
Template: welcome_email_template
```

**Key techniques**: Explicit step ordering, dependencies between steps, validation at each stage, rollback instructions for failures.

### Pattern 2: Multi-MCP Coordination

**Use when**: Workflows spanning multiple services.

```markdown
### Phase 1: Design Export (Figma MCP)
1. Export design assets
2. Generate specifications
3. Create asset manifest

### Phase 2: Asset Storage (Drive MCP)
1. Create project folder
2. Upload all assets
3. Generate shareable links

### Phase 3: Task Creation (Linear MCP)
1. Create development tasks
2. Attach asset links
3. Assign to team

### Phase 4: Notification (Slack MCP)
1. Post handoff summary to #engineering
2. Include asset links and task references
```

**Key techniques**: Clear phase separation, data passing between MCPs, validation before next phase, centralized error handling.

### Pattern 3: Iterative Refinement

**Use when**: Output quality improves with iteration.

```markdown
### Initial Draft
1. Fetch data via MCP
2. Generate first draft
3. Save to temporary file

### Quality Check
1. Run validation: `scripts/check_report.py`
2. Identify issues (missing sections, formatting, data errors)

### Refinement Loop
1. Address each issue
2. Regenerate affected sections
3. Re-validate
4. Repeat until quality threshold met

### Finalization
1. Apply final formatting
2. Generate summary
3. Save final version
```

**Key techniques**: Explicit quality criteria, iterative improvement, validation scripts, know when to stop iterating.

### Pattern 4: Context-Aware Selection

**Use when**: Same outcome, different tools depending on context.

```markdown
### Decision Tree
1. Check file type and size
2. Determine best approach:
   - Large files (>10MB): Use cloud storage
   - Collaborative docs: Use Notion/Docs
   - Code files: Use GitHub
   - Temporary files: Use local storage

### Execute Based on Decision
- Call appropriate tool
- Apply service-specific metadata
- Generate access link

### Provide Context to User
Explain why that approach was chosen
```

**Key techniques**: Clear decision criteria, fallback options, transparency about choices.

### Pattern 5: Domain-Specific Intelligence

**Use when**: Skill adds specialized knowledge beyond tool access.

```markdown
### Before Processing (Compliance Check)
1. Fetch transaction details
2. Apply compliance rules:
   - Check sanctions lists
   - Verify jurisdiction
   - Assess risk level
3. Document compliance decision

### Processing
IF compliance passed:
- Process transaction
- Apply fraud checks
ELSE:
- Flag for review
- Create compliance case

### Audit Trail
- Log all checks
- Record decisions
- Generate audit report
```

**Key techniques**: Domain expertise embedded in logic, compliance before action, comprehensive documentation.

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

## Historical Pattern Snapshot Guide

The observations below describe the bundled historical snapshots. They are non-authoritative pattern prompts, not current platform policy. Re-check any selected technique against the current task, the portable core, and target documentation; omit it when it does not add behavior.

### From Real-World Examples

#### Discipline Enforcement (like TDD example)
**Use when**: Need to enforce strict methodology.
**Techniques**: Iron Laws (unbreakable rules), rationalization tables (pre-empt excuses), verification checklists, red flags for self-monitoring.

#### Four-Phase Methodology (like Systematic Debugging)
**Use when**: Complex process with clear stages.
**Techniques**: Phase gates, stopping rules (three-fix rule), sub-skill integration, meta-cognitive monitoring.

#### Helper Scripts (like Web App Testing)
**Use when**: Complex setup better handled by code.
**Techniques**: Black box philosophy (don't pollute context), `--help` first (self-documenting), decision trees, compact helper-led instructions.

#### Comprehensive Framework (like MCP Builder)
**Use when**: Building complex systems with multiple phases.
**Techniques**: Quoted design principles, WebFetch for external docs, progressive reference loading, evaluation framework.

#### Production Standards (like XLSX)
**Use when**: Domain-specific quality requirements.
**Techniques**: Zero-tolerance policies, industry conventions (color coding), automated validation scripts, verification checklists.

#### Decision Tree + Externals (like DOCX)
**Use when**: Multiple workflows based on use case.
**Techniques**: Decision tree upfront, external documentation (MANDATORY reads), batching strategy (3-10 items), minimal edits principle.

#### Safety Workflow (like Git Worktrees)
**Use when**: Automation with safety requirements.
**Techniques**: Priority order (existing > config > ask), safety verification (.gitignore), auto-detection, baseline verification.

### Patterns Observed Across the Snapshots

1. **Clear structure**: Well-defined sections
2. **Explicit principles**: Core principles stated upfront
3. **Examples where needed**: Code, commands, or workflows only when they clarify output or a decision
4. **Tables for mappings**: Comparisons or checklists when relationships are otherwise hard to scan
5. **Safety boundaries**: Positive target behavior plus prohibitions only for unavoidable guardrails
6. **Integration guidance**: How skills relate to each other

### Key Insights

**From Community (obra/superpowers)**:
- Rationalization pre-emption (TDD)
- Stopping rules (Systematic Debugging)
- Safety verification (Git Worktrees)
- Sub-skill integration
- Human partner signals

**From Official (anthropics/skills)**:
- Compact helper-led design (Web App Testing)
- Black box philosophy (helper scripts)
- WebFetch integration (MCP Builder)
- Zero-tolerance policies (XLSX)
- MANDATORY reads (DOCX)
- Progressive reference loading

### Anti-Patterns

Common failure modes:
- Vague descriptions
- Multiple unrelated capabilities
- Ambiguous instructions
- Skip verification steps
- Missing a skill-local changelog for an independently released skill
- Assume context without checking
- Skip safety verification
- Pollute context with large files

## Skill Review Checklist

Review the complete installed or packaged skill, not only the current diff. Default to read-only unless the user authorizes changes. Use a coverage ledger with `Rule or branch | Evidence | Result | Follow-up`; valid results are `pass`, `finding`, `not applicable`, and `unknown`. Never turn an unknown or unrun check into a pass.

### 1. Contract and Scope

- Record the user request, repository rules, allowed mutations, and sources of truth.
- Name every target agent or harness, surface, invocation mode, and distribution form.
- Reconstruct the intended jobs, real usage branches, inputs, outputs, side effects, failure behavior, and completion criteria.
- Distinguish confirmed requirements from inference and unknown history.
- Identify the portable core and each harness enhancement; require a fallback unless the skill explicitly declares a single-harness contract.
- If `SPEC.md` is presented as a maintainer contract, verify its authority, every requirement and rationale, all four [admission conditions](#exceptional-maintainer-specifications), and its pointer for modifying or reviewing that skill itself. Its absence is not a finding by itself.

### 2. Package and Trust Inventory

- Classify every file as runtime instruction, maintainer contract, reference, script, asset, metadata, or release artifact.
- Resolve every local link and verify referenced files are packaged. Avoid reference chains deeper than one level from `SKILL.md`.
- Inspect scripts and dependencies before running them. Check inputs, failure paths, network access, credential handling, dynamic downloads, broad filesystem access, tool grants, and instruction-injection surfaces.
- For enterprise or externally sourced packages, review every bundled file, sandbox-test executable content, verify provenance and package integrity, and use a reviewer independent of the author.
- Record binary, generated, external, or otherwise uninspected content as unknown.

### 3. Agent Contract

- For model invocation, map one discriminating description pointer to every real branch and test realistic near-neighbor boundaries.
- For user-only invocation, verify discoverability and explicit control without demanding automatic-trigger phrasing.
- Map every branch to ordered steps, reference reads, and checkable, exhaustive completion criteria.
- Verify progressive disclosure and co-location: process steps stay together; lookup material has explicit read conditions.
- Prune duplicated rules, unsupported environment assumptions, time-sensitive claims, stale sediment, no-op instructions, needless options, and examples whose removal does not reduce understanding.
- Check terminology, error handling where operations can fail, and target-specific claims against current primary documentation.

### 4. Validation and Behavior

- Run `skills-ref validate ./path/to/skill` for portable frontmatter and naming when available, plus the named target's validator. Record each validator's scope; neither schema validation nor naming checks are a behavior review.
- Run each supported branch in a fresh context with its expected behavior and observable completion criteria.
- For model-invoked skills, cover intended triggers, paraphrases, realistic near-misses, and ambiguous cases.
- Test the portable fallback without host enhancements. Test each declared enhancement on its named host.
- Test in isolation and alongside likely overlapping skills; include every model and surface claimed by the release.
- Run bundled scripts safely and verify successful output, invalid input, dependency failure, and side-effect boundaries.

### 5. Findings and Release

- Report each finding with severity, file and line evidence, impact, the smallest adequate fix, and an objective completion criterion.
- Separate facts, inferences, and unknowns. Report tests not run and why.
- If changes are authorized, rerun every affected gate and check the whole package again for semantic residue.
- Apply the [Evidence gate](#evidence-gate) to a skill-local changelog when Skill Composer or repository release policy requires one. Do not fail an otherwise valid unpublished skill merely for lacking release artifacts that do not apply.

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

Use your success criteria measurements to populate this table only after correctness passes. Manual and scripted approaches are both valid, but the Skills API does not supply a built-in evaluation runner; automation must come from a target-specific authoring helper or a user-built harness.

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

### Skill Won't Upload

Error: "Could not find SKILL.md in uploaded folder"
- Rename to exactly `SKILL.md` (case-sensitive)
- Verify: `ls -la` should show `SKILL.md`

Error: "Invalid frontmatter"
- Check `---` delimiters (opening on line 1, closing before content)
- Use spaces not tabs for indentation
- Quote strings with special characters

Error: "Invalid skill name"
- Use kebab-case: `my-cool-skill` not `My Cool Skill`

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
1. Keep `SKILL.md` under **500 lines** and below the recommended **5,000 tokens**; move needed lookup material to focused references.
2. Measure recall on the actual target as skills are added; use the surface's documented cap instead of a generic count.
3. Ensure progressive disclosure is working and reference reads have explicit conditions.

### Skill Packs

If you have many related capabilities, consider grouping them into a **skill pack** — a single skill that bundles related functions together. This can reduce the number of simultaneously enabled skills and help the host select the right capability.

Consolidate only when coexistence evaluations show trigger conflicts or recall degradation and the combined skill preserves equal behavior. Shared domain or an arbitrary skill count alone is not enough.

### MCP Connection Issues

1. Use the named host's connector or status diagnostic. For Claude Code, run `/mcp`; for Claude.ai, open **Customize > Connectors**
2. Check authentication (API keys valid, proper scopes)
3. Test MCP independently by asking the agent to call it without the skill
4. Verify tool names match MCP server documentation (case-sensitive)

### Debug Mode (Claude Code)

```bash
claude --debug
```

Use debug output for YAML parse errors and skill-listing diagnostics. For trigger tests, record whether the host actually loaded or invoked the skill; debug output alone is not behavior evidence.

## Distribution

Treat each target as a separate compatibility surface. Do not assume that a skill propagates between surfaces: some Claude surfaces provide automatic or opt-in sync, while independently authored local installs and Skills API versions remain separately managed. Verify current sync behavior, then package, validate, release, and test every claimed target independently.

### Claude.ai

1. Package the skill folder as a ZIP file.
2. Open **Customize > Skills**.
3. Select **+**, then **Create skill > Upload a skill**.
4. Upload the ZIP and run the claude.ai evaluation cases.

Organization owners manage skill availability and provisioning in **Organization settings > Skills** when their plan supports it. Recipients of a shared claude.ai skill receive later owner updates automatically; do not generalize that behavior to local installs, provisioned archives, or API versions.

### Claude Code Filesystem Skills

- Project skills: `.claude/skills/<skill-name>/SKILL.md`
- Personal skills: `~/.claude/skills/<skill-name>/SKILL.md`

Claude Code also accepts additional frontmatter and runtime features. Keep those enhancements outside the portable core or declare the skill Claude Code-only.

### Claude Code Plugin Structure

```
my-plugin/
├── .claude-plugin/
│   └── plugin.json
├── commands/
├── agents/
└── skills/
    └── my-skill/
        └── SKILL.md
```

Skills in `skills/` are discovered automatically; no per-skill `plugin.json` entry is needed. Plugin skills are invoked with a namespaced form such as `/plugin-name:skill-name`.

### Repository and Standalone Distribution

1. Use a repository-level README for a collection and a skill-local README when an independently distributed skill needs human-facing installation or compatibility notes.
2. Do not duplicate runtime instructions from `SKILL.md` in either README.
3. Keep independently distributed release artifacts, dependencies, and the Skill Composer changelog inside the skill folder.
4. Provide a ZIP only for a target that consumes one, such as claude.ai upload.
5. Link from MCP documentation when the skill enhances that MCP.

The `anthropics/skills` repository on GitHub contains Anthropic-created skills you can browse and customize. See also the MCP documentation cross-reference guidance in [Document in Your MCP Repo](#document-in-your-mcp-repo) below.

### Installation Guide Template

Include a guide like this in your repo README:

```markdown
## Installing the [Your Service] skill

1. Download the skill:
   - Clone repo: `git clone https://github.com/yourcompany/skills`
   - Or download ZIP from Releases

2. Install on the supported target:
   - Claude.ai: open Customize > Skills and upload the ZIP
   - Claude Code project: copy the folder into `.claude/skills/`
   - Other agents: follow the verified target-specific path

3. Enable the skill:
   - Toggle on the [Your Service] skill
   - Ensure your MCP server is connected

4. Test:
   - Ask the target agent: "Set up a new project in [Your Service]"
```

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

### Skills API

The Skills API manages workspace-scoped skill uploads and generated versions. Add an uploaded skill to a Messages API request through `container.skills`. Messages API use of skills requires the code execution tool beta. Do not substitute an optional `metadata.version` value for the API's version identifier or for the skill-local release record.

For implementation details, use the current Skills API guide and API reference rather than copying endpoint behavior into a long-lived skill.

### Agent SDK

Agent SDK skills are filesystem artifacts discovered from configured setting sources; the SDK does not register them through the Skills API. Configure the available skills and tool approval in SDK options. The `allowed-tools` frontmatter field does not control SDK permissions.

## Invocation Modes

Invocation and content structure are independent choices:

- **Model-invoked:** the host selects the skill from its description.
- **User-invoked:** the user selects the skill explicitly to control timing or side effects.
- **Both:** the default on hosts that safely support both paths.

Claude Code has merged custom commands into skills. Use `disable-model-invocation: true` for a user-only Claude Code skill and `user-invocable: false` for a model-only one. Existing `.claude/commands/*.md` files remain a compatibility form, not a separate authoring model. Other agents may expose different controls; keep invocation policy in a target adapter rather than the portable core.

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

## Skill Examples

Seven annotated historical pattern snapshots live in [examples/](examples/). Use them for structural ideas only; current specifications and target documentation override any embedded platform detail.

| Example | Pattern | Source | Key Feature |
|---------|---------|--------|-------------|
| [TDD](examples/tdd.md) | Discipline enforcement | obra/superpowers | Rationalization tables |
| [Systematic Debugging](examples/systematic-debugging.md) | Four-phase methodology | obra/superpowers | Three-fix rule |
| [Web App Testing](examples/webapp-testing.md) | Helper scripts | anthropics/skills | Black box philosophy |
| [MCP Builder](examples/mcp-builder.md) | Comprehensive framework | anthropics/skills | WebFetch integration |
| [XLSX](examples/xlsx.md) | Production standards | anthropics/skills | Zero formula errors |
| [DOCX](examples/docx.md) | Decision tree + externals | anthropics/skills | MANDATORY file reads |
| [Git Worktrees](examples/git-worktrees.md) | Safety workflow | obra/superpowers | `.gitignore` verification |

**By use case category:**
- **Document & Asset Creation**: XLSX, DOCX — producing formatted documents and assets with domain-specific quality standards
- **Workflow Automation**: TDD, Systematic Debugging, MCP Builder — enforcing step-by-step processes and consistent methodology
- **MCP Enhancement**: Web App Testing, Git Worktrees — enhancing tool access with best practices and safety workflows

## Resources and Community

If you're building your first skill, start with the Best Practices Guide, then reference the API docs as needed.

### Official Documentation

- [Agent Skills Specification](https://agentskills.io/specification) — portable structure, fields, references, and validation
- [Skill Authoring Best Practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — current authoring and evaluation guidance
- [Enterprise Skill Review](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/enterprise) — security, coexistence, lifecycle, and production review
- [Claude Code Skills](https://code.claude.com/docs/en/slash-commands) — Claude Code-specific invocation and enhancement fields
- [Use Skills in Claude](https://support.claude.com/en/articles/12512180-use-skills-in-claude) — current claude.ai installation and sharing paths
- [Skills API Guide](https://platform.claude.com/docs/en/build-with-claude/skills-guide) — API upload, versions, and Messages API use
- [Agent SDK Skills](https://code.claude.com/docs/en/agent-sdk/skills) — filesystem discovery and SDK-specific tool controls
- [MCP Documentation](https://modelcontextprotocol.io) — Model Context Protocol specification and guides

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
