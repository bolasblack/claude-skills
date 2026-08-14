---
name: skill-composer
description: "Primary authority for creating, updating, reviewing, and packaging agent skills. Use for any skill-authoring task, including cross-agent portability, host-only enhancement boundaries, activation or description fixes, portable changelogs, and conflicts with harness-injected helpers such as skill-creator; compose those helpers under this skill rather than letting them replace its rules."
---

# Skill Composer

Create well-structured, discoverable agent skills. Based on the current Agent Skills specification, target-platform documentation, and community best practices.

When modifying or reviewing Skill Composer itself, read [SPEC.md](SPEC.md) first. It holds the rare maintainer-only requirements that must constrain future rewrites; ordinary skill-authoring tasks do not need it.

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

For a stronger agent-facing writing pass, optionally compose this skill with Matt Pocock's [writing-for-agents](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents). Skill Composer owns skill scope, mechanics, packaging, and validation; `writing-for-agents` sharpens context pointers, completion criteria, information hierarchy, and pruning. Keep the composition optional so the resulting skill does not depend on a sibling skill being installed.

### Portability

Default to two layers:

1. **Portable core:** the goal, inputs, outputs, decision rules, ordered workflow, failure behavior, and completion criteria work across compatible agents.
2. **Harness enhancements:** hooks, dynamic context, subagent configuration, UI metadata, permission conveniences, and similar host-only features may improve ergonomics or enforcement but do not become the sole way to complete the core workflow.

Name each enhancement's host and provide a portable fallback. A skill may depend on a host-only feature only when its description and compatibility contract explicitly make the skill host-specific; do not claim cross-agent portability for that package.

## Planning Before Building

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

### Define Success Criteria and Evaluations

Build evaluations before extensive instructions:

1. Run representative tasks without the skill and record the specific gap.
2. Start with 2-3 scenarios that exercise those observed gaps; expand only when real branches or risks require it.
3. Define expected behavior and a checkable completion criterion for each scenario.
4. Write the minimum instructions needed to improve the baseline.
5. Run the same scenarios with the skill and iterate from evidence.

For a model-invoked skill, cover intended triggers, realistic near-misses, and ambiguous boundary cases. For every skill, measure task correctness, instruction following, tool or API failures, user correction, and any output contract that matters. Compare efficiency only after correctness; fewer tokens or tool calls are not improvements when behavior regresses.

## Creating a Skill

### Step 1: Choose Target and Scope

Name the target harness, surface, invocation mode, and distribution form before choosing a path or frontmatter. Define the portable core first, then add verified target-only enhancements with fallbacks. If the skill is intentionally single-harness, state that contract explicitly instead.

For Claude Code filesystem skills:

- **Project**: `.claude/skills/` for repository-scoped skills; commit the folder to share it with the team.
- **Personal**: `~/.claude/skills/` for cross-project skills owned by one user.

```bash
mkdir -p .claude/skills/skill-name
```

See [Distribution](REFERENCE.md#distribution) for authoritative target-specific installation and packaging detail.

### Step 2: Create File Structure

```
your-skill-name/
├── SKILL.md          # Required - main instructions
├── CHANGELOG.md      # For independently versioned or distributed skills
├── scripts/          # Optional - executable code
│   ├── process.py
│   └── validate.sh
├── references/       # Optional - documentation loaded as needed
│   ├── api-guide.md
│   └── examples.md
└── assets/           # Optional - templates, fonts, icons
    └── template.md
```

**Critical rules**:
- File MUST be exactly `SKILL.md` (case-sensitive, no variations)
- Folder name: kebab-case only (`my-skill`, not `My_Skill`)
- Keep runtime instructions in `SKILL.md` or linked references; do not add a README that duplicates them.
- A human-facing `README.md` and a release-facing `CHANGELOG.md` are appropriate when the skill is independently distributed. Keep portable release artifacts inside the skill folder so they travel without the source repository.
- Keep packaged dependencies inside the skill folder. Use external references only when the target harness supports them and the distribution does not need to be self-contained.

`SPEC.md` is intentionally absent from the default structure. Add it only when an explicit, stable requirement must constrain future modifications or rewrites but is not needed during ordinary skill execution. Put runtime principles and workflows in `SKILL.md`, branch-only lookup material in references, and release history in `CHANGELOG.md`. In the rare qualifying case, keep `SPEC.md` short, state each current requirement and why it must survive, and add a conditional pointer from `SKILL.md` for modifying or reviewing that skill itself. Apply the complete [Exceptional Maintainer Specifications](REFERENCE.md#exceptional-maintainer-specifications) admission test; importance, length, or complexity alone does not qualify a skill.

See [Directory Structure Patterns](REFERENCE.md#directory-structure-patterns) for the authoritative structure and script requirements.

### Step 3: Write YAML Frontmatter

Use the portable Agent Skills fields unless the named target requires or supports an extension. For a model-invoked skill, the description is also its discovery pointer.

```yaml
---
name: "skill-name"
description: "What it does. Use when [trigger conditions]."
---
```

**Portable required fields**:

| Field | Constraints |
|-------|-------------|
| `name` | 1-64 lowercase letters, digits, or hyphens; no leading, trailing, or consecutive hyphens; must match folder name |
| `description` | 1-1024 chars; describe what the skill does and when it applies |

**Optional fields**:

| Field | Purpose | Example |
|-------|---------|---------|
| `allowed-tools` | Experimental, target-dependent tool pre-approval | `Read Grep Glob` |
| `license` | License name or bundled license file reference | `MIT`, `Apache-2.0`, `LICENSE.txt` |
| `compatibility` | Environment requirements (1-500 chars) | `"Requires Claude Code with bash access"` |
| `metadata` | Optional string-to-string extension map | `author`, `version`, `mcp-server` |

Run both the portable validator and the target-platform validator. On Anthropic upload surfaces, `name` must not contain the reserved words `claude` or `anthropic`, and `name` and `description` must not contain XML tags; do not promote those surface rules into universal constraints for every harness.

See [YAML Frontmatter Specification](REFERENCE.md#yaml-frontmatter-specification) for the authoritative portable schema and target qualifications.

### Step 4: Write the Description

First choose whether the skill is model-invoked, user-invoked, or both. For model invocation, the description is the primary activation pointer. For a user-only skill, it is a concise human-facing summary and need not pretend to be an automatic trigger list. See [Invocation Modes](REFERENCE.md#invocation-modes) for target-specific controls.

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

### Step 5: Write Instructions

Clear, explicit, step-by-step. Put critical instructions at the top.

```markdown
## Instructions

### Step 1: Gather Context
Run `git diff --staged` to see changes.

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

### Step 2: [Second Major Step]
[...]

**Done when:** [observable completion criterion]
```

**Best practices**:
- Be specific and actionable (not "validate things properly" but list exact checks)
- Give every step a checkable, exhaustive completion criterion
- Put a rule next to the step it governs; use references for lookup material, not split process state
- Reference bundled resources with explicit read conditions: `Before writing queries, consult references/api-patterns.md`
- Keep `SKILL.md` below **5,000 tokens** and under **500 lines**; see [Large Context Issues](REFERENCE.md#large-context-issues) and move needed detail to one-level-deep references
- Include troubleshooting and examples only when an evidenced branch needs them

**Advanced technique**: For critical validations, bundle a script that performs checks programmatically rather than relying on language instructions. Code is deterministic; language interpretation isn't.

### Step 6: Consider Tool Pre-Approval

```yaml
allowed-tools: Read Grep Glob
allowed-tools: "Bash(git:*) Read"
```

`allowed-tools` is experimental in the portable spec and varies by host. In Claude Code it pre-approves listed tools for the invocation turn; it does not remove unlisted tools. Use the host's permission or deny mechanism when actual restriction is required. See [Tool Pre-Approval](REFERENCE.md#tool-pre-approval).

### Step 7: Record Portable Release History

Under Skill Composer's release policy, a skill that is independently versioned or distributed keeps its release history in a skill-local `CHANGELOG.md`, not in `SKILL.md` and not only in Git history. A commit can contain changes to several skills, while a standalone distribution may contain no `.git` directory.

Update the changelog in the same change that alters released behavior. Use semantic versioning, keep one entry per skill release, and avoid duplicating the history in runtime instructions.

Before writing any changelog claim, apply the mandatory [Evidence gate](REFERENCE.md#evidence-gate). It governs explicit reasons from current or retrievable earlier user conversations, other accepted sources, de-identification, and missing-evidence handling. Do not treat a new entry as complete until its change and rationale pass that gate; any optional example must pass it too.

For every complete new logical change, record what changed and why the change became necessary. Add an `Example` only when it materially clarifies the causal pre-change pattern or consequence beyond `Changed` and `Why`; omit it when removing it leaves understanding unchanged. When useful, prefer a minimal de-identified code, config, payload, or diff excerpt; translate an explicitly described code pattern into a faithful reconstruction only when that adds clarity. When an example is useful but code is not, use concrete prose. Never invent missing rationale for legacy history.

When reviewing an existing changelog, re-run the inclusion test for every retained `Example`, not only examples added by the current diff, and remove it when `Changed` plus `Why` remain equally clear without it. The changelog review passes only when every complete new entry has evidence-backed change and rationale and every retained example adds material understanding. Preserve legacy claims under the Evidence gate's legacy rule; do not invent missing history to make them fit the new format.

See [Portable Changelog Format](REFERENCE.md#portable-changelog-format) for the full format and inclusion test. An unpublished, single-use skill does not need an empty changelog.

### Step 8: Run Evaluations

Run the scenarios defined before authoring and add cases for every branch introduced while writing:

- **Triggering** (model-invoked only): intended queries, paraphrases, realistic near-misses, and ambiguous boundaries.
- **Functional**: correct output, edge cases, side effects, tool or API behavior, and completion criteria.
- **Isolation and coexistence**: the skill alone, then alongside likely overlapping skills.
- **Baseline comparison**: repeat the same task without the skill when the claimed value is an improvement over default behavior.

Do not treat an obviously unrelated negative query, a schema validator, or asking the model to recite the description as evidence of correct activation. There is no portable built-in evaluation runner; use the target harness manually or build repeatable automation. Keep suite sizes purpose-specific: start output-quality iteration with 2-3 cases; for focused description tuning, aim for about 20 balanced trigger/non-trigger queries and repeat each multiple times; for enterprise release, require 3-5 representative queries covering trigger, non-trigger, and ambiguity. Expand by real branches and risk, and test every model and surface you intend to support.

For Claude Code, `claude --debug` can provide diagnostic logs; it is not a substitute for behavior evidence. See [Testing Methodology](REFERENCE.md#testing-methodology).

## Reviewing an Existing Skill

Review is a distinct, default-read-only branch. Do not create files, rewrite content, or publish changes unless the user authorizes modification. Do not review only the current diff when the request concerns the skill itself.

### Review Step 1: Lock the Contract

Record the review scope, repository rules, target harness and surface, invocation mode, distribution form, and allowed mutations. If the package presents `SPEC.md` as a maintainer contract, verify the authority, requirement, and current rationale of every entry rather than treating the filename as proof. Reconstruct the intended jobs, usage branches, outputs, side effects, and completion criteria from requirements and observed usage; mark missing evidence as unknown rather than trusting the current text.

**Done when:** every claimed branch and target constraint has a source or is explicitly unknown.

### Review Step 2: Inventory the Whole Package

Read and classify every packaged file, resolve every local link, and inspect scripts, assets, dependencies, external inputs, and release artifacts. Before executing untrusted content, assess network access, credential handling, broad filesystem or tool use, dynamic downloads, and instruction-injection surfaces.

**Done when:** every file and trust boundary is accounted for, with uninspected or binary content reported as unknown.

### Review Step 3: Audit the Agent Contract

Map each usage branch to its invocation control, description pointer, ordered steps, reference reads, and checkable completion criteria. Audit progressive disclosure, co-location, consistent terminology, and the portable-core/harness-enhancement boundary. Confirm every host-only enhancement has a fallback, unless the skill explicitly declares that host as a requirement. Where `SPEC.md` is a maintainer contract, apply its exceptional admission test, verify that its pointer fires only when modifying or reviewing that skill itself, and report any runtime rule or history duplicated into it. Report duplicated rules, environment caches, time-sensitive claims, stale sediment, no-op instructions, and examples that add no material understanding; remove them only in the authorized fixing step.

**Done when:** every branch, step, and reference pointer has an evidence-backed pass, finding, or not-applicable disposition.

### Review Step 4: Validate Real Behavior

Run the portable schema validator plus the named target's validator; neither replaces behavior testing. Execute representative activation and functional scenarios, then test isolation and coexistence where the harness supports them. Run bundled scripts in a safe environment and verify their outputs and failure paths. Record every test not run and why.

**Done when:** each supported branch has behavior evidence and every validation gap remains visible.

### Review Step 5: Report, Then Fix if Authorized

For each finding, provide severity, file and line evidence, impact, the smallest adequate fix, and an objective completion criterion. Separate confirmed facts, inferences, and unknowns. If changes are authorized, apply them, rerun affected gates, and update the skill-local changelog under its Evidence gate when the release policy applies.

**Done when:** every review rule is accounted for and no unknown or unrun check is presented as a pass. Use the full [Skill Review Checklist](REFERENCE.md#skill-review-checklist) as the coverage ledger.

## Workflow Patterns

Five proven patterns for structuring skill instructions. See [REFERENCE.md](REFERENCE.md#workflow-patterns) for full examples.

| Pattern | Use When |
|---------|----------|
| **Sequential Orchestration** | Multi-step processes in specific order |
| **Multi-MCP Coordination** | Workflows spanning multiple services |
| **Iterative Refinement** | Output quality improves with iteration |
| **Context-Aware Selection** | Same outcome, different tools by context |
| **Domain-Specific Intelligence** | Specialized knowledge beyond tool access |

## Real-World Examples

Use the annotated [Skill Examples](REFERENCE.md#skill-examples) only when a concrete pattern helps the current branch. They are historical pattern snapshots, not current platform contracts, and examples are not mandatory content for a new skill.

## Quick Checklist

Before building:
- [ ] Identified every real usage branch and its concrete use case
- [ ] Named target harness, surface, invocation mode, and distribution form
- [ ] Defined a portable core and fallbacks for host-only enhancements, or explicitly declared a single-harness contract
- [ ] Planned folder structure
- [ ] Tools identified (built-in or MCP)
- [ ] Classified any harness-injected authoring helpers as subordinate adapters
- [ ] Defined baseline evaluations and completion criteria

During development:
- [ ] `SKILL.md` exists (exact spelling)
- [ ] YAML frontmatter has `---` delimiters
- [ ] Portable and target-specific validators pass, or unavailable gates are reported
- [ ] Model-invoked description covers each real branch
- [ ] Instructions are clear and actionable
- [ ] Each step has a checkable completion criterion
- [ ] Needed error handling and examples add information; inapplicable sections are omitted
- [ ] References have explicit read conditions and resolve one level deep
- [ ] Any maintainer `SPEC.md` passes the exceptional admission test and has a pointer for modifying or reviewing that skill itself
- [ ] Independently released skill has an updated, packaged `CHANGELOG.md` whose complete new entries contain evidence-backed change and rationale and whose retained examples all pass the removal test

Before release or installation:
- [ ] Tested intended triggers, paraphrases, realistic near-misses, and ambiguity when model invocation applies
- [ ] Functional tests pass
- [ ] Isolation and coexistence tests pass where supported
- [ ] Portable fallback preserves core behavior without host-only enhancements, when portability is claimed
- [ ] Tool integration works (if applicable)
- [ ] Security and trust review matches the distribution risk
- [ ] Target-specific package, metadata, and version requirements pass

After release:
- [ ] Monitor for under/over-triggering
- [ ] Collect user feedback
- [ ] Iterate on description and instructions based on results
- [ ] Update the target's release mechanism and skill-local changelog when behavior changes
