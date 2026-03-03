---
name: skill-composer
description: "Create and improve Claude Code Skills following official best practices. Use when creating a skill, improving skill descriptions, fixing skill activation issues, or structuring skill directories."
---

# Skill Composer

Create well-structured, discoverable skills that Claude can activate automatically. Based on Anthropic's official guide and community best practices.

## Skills & MCP

**MCP provides the professional kitchen:** access to tools, ingredients, and equipment.
**Skills provide the recipes:** step-by-step instructions on how to create something valuable.

Together, they enable users to accomplish complex tasks without figuring out every step themselves.

| MCP (Connectivity) | Skills (Knowledge) |
|---|---|
| Connects Claude to your service (Notion, Asana, Linear, etc.) | Teaches Claude how to use your service effectively |
| Provides real-time data access and tool invocation | Captures workflows and best practices |
| What Claude *can* do | How Claude *should* do it |

**Why this matters for MCP users:**

Without skills, users connect your MCP but don't know what to do next — support tickets pile up, each conversation starts from scratch, and inconsistent results get blamed on your connector. With skills, pre-built workflows activate automatically, tool usage is consistent and reliable, and best practices are embedded in every interaction.

> *Building standalone skills without MCP? Skip to Planning and Design — you can always return here later.*

## Core Design Principles

### Progressive Disclosure

Skills use a three-level system to minimize token usage:

1. **YAML frontmatter** (always loaded): Appears in Claude's system prompt. Provides just enough for Claude to decide when to activate the skill.
2. **SKILL.md body** (loaded when relevant): Full instructions, loaded when Claude determines the skill matches the current task.
3. **Linked files** (loaded on demand): References, scripts, assets - loaded only as needed during execution.

### Composability

Claude can load multiple skills simultaneously. Skills should work well alongside others, never assume they're the only capability available.

### Portability

Skills work across Claude.ai, Claude Code, and API. Create once, use everywhere - provided the environment supports any dependencies the skill requires.

## Planning Before Building

### Start with Use Cases

Ask yourself first:
- What does a user want to accomplish?
- What multi-step workflows does this require?
- Which tools are needed (built-in or MCP)?
- What domain knowledge or best practices should be embedded?

Identify 2-3 concrete use cases before writing anything.

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
- **Workflow Automation**: `skill-creator` skill — "Interactive guide for creating new skills. Walks the user through use case definition, frontmatter generation, instruction writing, and validation."
- **MCP Enhancement**: `sentry-code-review` skill (from Sentry) — "Automatically analyzes and fixes detected bugs in GitHub Pull Requests using Sentry's error monitoring data via their MCP server."

### Define Success Criteria

**Quantitative** (aspirational targets):
- Skill triggers on **90%** of relevant queries
- Completes workflow in expected tool calls
- **0 failed API calls** per workflow

**Qualitative:**
- Users don't need to prompt about next steps
- Workflows complete without user correction
- Consistent results across sessions

**How to measure:**
- *Trigger rate*: Run 10-20 test queries that should trigger your skill. Track how many load automatically vs. require explicit invocation.
- *Workflow efficiency*: Compare the same task with and without the skill enabled. Count tool calls and total tokens consumed.
- *API reliability*: Monitor MCP server logs during test runs. Track retry rates and error codes.
- *Consistency*: Run the same request 3-5 times. Compare outputs for structural consistency and quality.
- *User experience*: During testing, note how often you need to redirect or clarify. Ask beta users for feedback.

## Creating a Skill

### Step 1: Choose Scope

**Project/Local Skills**: `.claude/skills/` (Recommended)
- Team-shared via git, project-specific, committed to repository

**Global Skills**: `~/.claude/skills/` or shared location
- Cross-project workflows, system-wide capabilities

```bash
mkdir -p .claude/skills/skill-name
```

### Step 2: Create File Structure

```
your-skill-name/
├── SKILL.md          # Required - main instructions
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
- Do NOT include `README.md` inside the skill folder (all documentation goes in SKILL.md or references/)
  - **Exception**: A repo-level README.md IS appropriate when distributing via GitHub for human users — just not inside the skill folder itself.
- All files MUST be inside the skill folder - never reference external files

### Step 3: Write YAML Frontmatter

The frontmatter is how Claude decides whether to load your skill. Get this right.

```yaml
---
name: "skill-name"
description: "What it does. Use when [trigger conditions]."
---
```

**Required fields**:

| Field | Constraints |
|-------|-------------|
| `name` | kebab-case, no spaces/capitals/underscores, max 64 chars, must match folder name |
| `description` | Max 1024 chars, MUST include what AND when, no XML tags (`<` `>`) |

**Optional fields**:

| Field | Purpose | Example |
|-------|---------|---------|
| `allowed-tools` | Restrict tool access | `Read, Grep, Glob` or `"Bash(python:*) WebFetch"` |
| `license` | Open source license | `MIT`, `Apache-2.0` |
| `compatibility` | Environment requirements (1-500 chars) | `"Requires Claude Code with bash access"` |
| `metadata` | Custom key-value pairs | `author`, `version`, `mcp-server`, `tags` |

**Security restrictions**: No XML angle brackets in frontmatter. Names with "claude" or "anthropic" prefix are reserved.

### Step 4: Write the Description

The description is the single most important field - it determines activation.

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

**Include**: specific file extensions, action verbs users say, domain terminology, "Use when..." clause.

**To reduce over-triggering**, add negative triggers:
```yaml
description: "Advanced data analysis for CSV files. Use for statistical modeling,
  regression, clustering. Do NOT use for simple data exploration."
```

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

### Troubleshooting
Error: [Common error]
Cause: [Why]
Solution: [Fix]
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

## Examples

### Example 1: [Common scenario]
**User says:** "Set up a new marketing campaign"
**Actions:**
1. Fetch existing campaigns via MCP
2. Create new campaign with provided parameters
**Result:** Campaign created with confirmation link

### Troubleshooting

**Error:** [Common error message]
**Cause:** [Why it happens]
**Solution:** [How to fix]
```

**Best practices**:
- Be specific and actionable (not "validate things properly" but list exact checks)
- Use `## Important` or `## Critical` headers for key points
- Reference bundled resources: `Before writing queries, consult references/api-patterns.md`
- Keep SKILL.md under **5,000 words** - move details to `references/`

**Advanced technique**: For critical validations, bundle a script that performs checks programmatically rather than relying on language instructions. Code is deterministic; language interpretation isn't.

### Step 6: Consider Tool Restrictions

```yaml
allowed-tools: Read, Grep, Glob          # Read-only analysis
allowed-tools: Read, WebFetch, WebSearch  # Research only
allowed-tools: "Bash(python:*) WebFetch"  # Scoped bash + web
```

See [REFERENCE.md](REFERENCE.md#tool-restrictions) for all tools and patterns.

### Step 7: Add Version History

```markdown
## Version History
- v1.0.0 (2025-11-03): Initial version
```

Use semantic versioning: Major (breaking), Minor (features), Patch (fixes).

### Step 8: Test Activation

Three areas to test:

**Triggering**: Does it activate on relevant queries? NOT activate on unrelated ones?
```
Should trigger:    "Help me set up a new ProjectHub workspace"
Should NOT trigger: "What's the weather in San Francisco?"
```

**Functional**: Does it produce correct outputs? API calls succeed? Edge cases handled?

**Execution issues**: Inconsistent results, API call failures, user corrections needed? Improve instructions and add error handling.

**Performance**: Compare with and without skill - fewer messages, fewer tokens, fewer failures?

> **Pro Tip:** Iterate on a single task before expanding. The most effective skill creators iterate on a single challenging task until Claude succeeds, then extract the winning approach into a skill. This leverages in-context learning and provides faster signal than broad testing.

**Debug approach**: Ask Claude "When would you use the [skill name] skill?" - it will quote the description back. Adjust based on what's missing.

For Claude Code: `claude --debug` to see activation logs.

**Testing approaches:** Skills can be tested manually (Claude.ai — fast iteration), with scripted automation (Claude Code — repeatable validation), or programmatically (Skills API — systematic evaluation suites). Choose based on your audience size and quality requirements. See [REFERENCE.md](REFERENCE.md#testing-and-iteration) for details.

**Checklist accelerator:** Use `skill-creator` to generate your first draft, then run through the Quick Checklist below to validate completeness.

### Using skill-creator

The `skill-creator` skill — built into Claude.ai and available for Claude Code — can help you build and iterate on skills. If you have an MCP server and know your top 2-3 workflows, you can build and test a functional skill in a single sitting.

**Creating skills:**
- Generate skills from natural language descriptions
- Produce properly formatted SKILL.md with frontmatter
- Suggest trigger phrases and structure

**Reviewing skills:**
- Flag common issues (vague descriptions, missing triggers, structural problems)
- Identify potential over/under-triggering risks
- Suggest test cases based on the skill's stated purpose

**Iterative improvement:**
- After encountering edge cases or failures, bring those examples back to skill-creator
- Example: "Use the issues & solution identified in this chat to improve how the skill handles [specific edge case]"

To use: `"Use the skill-creator skill to help me build a skill for [your use case]"`

> *Note: skill-creator helps you design and refine skills but does not execute automated test suites or produce quantitative evaluation results.*

### Problem-First vs Tool-First

Think of it like Home Depot. You might walk in with a problem — "I need to fix a kitchen cabinet" — and an employee points you to the right tools. Or you might pick out a new drill and ask how to use it for your specific job.

- **Problem-first:** "I need to set up a project workspace" — Your skill orchestrates the right MCP calls in the right sequence. Users describe outcomes; the skill handles the tools.
- **Tool-first:** "I have Notion MCP connected" — Your skill teaches Claude the optimal workflows and best practices. Users have tool access; the skill provides expertise.

Most skills lean one direction. Knowing which framing fits your use case helps you choose the right workflow pattern below.

## Workflow Patterns

Five proven patterns for structuring skill instructions. See [REFERENCE.md](REFERENCE.md#workflow-patterns) for full examples.

| Pattern | Use When |
|---------|----------|
| **Sequential Orchestration** | Multi-step processes in specific order |
| **Multi-MCP Coordination** | Workflows spanning multiple services |
| **Iterative Refinement** | Output quality improves with iteration |
| **Context-Aware Selection** | Same outcome, different tools by context |
| **Domain-Specific Intelligence** | Specialized knowledge beyond tool access |

## Skills vs Slash Commands

| Aspect | Skills | Slash Commands |
|--------|--------|----------------|
| **Invocation** | Automatic (model-invoked) | Manual (user types /command) |
| **Complexity** | Complex multi-step capabilities | Simple prompts |
| **Files** | Directory with SKILL.md + supporting files | Single markdown file |
| **Discovery** | Based on description matching | Explicit user command |

**Choose Skills** when Claude should activate based on context, or when complex workflows with multiple files/scripts are needed.

**Choose Slash Commands** when the user wants explicit invocation control, or for simple repeated prompts.

## Real-World Examples

Seven annotated examples in [examples/](examples/) demonstrating different patterns:

| Example | Lines | Pattern | Source |
|---------|-------|---------|--------|
| [TDD](examples/tdd.md) | ~365 | Discipline enforcement | obra/superpowers |
| [Systematic Debugging](examples/systematic-debugging.md) | ~296 | Four-phase methodology | obra/superpowers |
| [Web App Testing](examples/webapp-testing.md) | ~96 | Helper scripts | anthropics/skills |
| [MCP Builder](examples/mcp-builder.md) | ~329 | Comprehensive framework | anthropics/skills |
| [XLSX](examples/xlsx.md) | ~289 | Production standards | anthropics/skills |
| [DOCX](examples/docx.md) | ~197 | Decision tree + externals | anthropics/skills |
| [Git Worktrees](examples/git-worktrees.md) | ~214 | Safety workflow | obra/superpowers |

See [REFERENCE.md](REFERENCE.md#pattern-selection-guide) for when to use each pattern.

## Quick Checklist

Before building:
- [ ] Identified 2-3 concrete use cases
- [ ] Planned folder structure
- [ ] Tools identified (built-in or MCP)
- [ ] Reviewed this guide and example skills
- [ ] Considered skill-creator for initial draft

During development:
- [ ] `SKILL.md` exists (exact spelling)
- [ ] YAML frontmatter has `---` delimiters
- [ ] `name`: kebab-case, no spaces/capitals
- [ ] `description`: includes WHAT and WHEN
- [ ] No XML tags (`<` `>`) in frontmatter
- [ ] Instructions are clear and actionable
- [ ] Error handling included
- [ ] Examples provided (User says / Actions / Result)
- [ ] References clearly linked
- [ ] Version history present

Before upload:
- [ ] Tested triggering on obvious tasks (10-20 queries)
- [ ] Tested triggering on paraphrased requests
- [ ] Verified doesn't trigger on unrelated topics
- [ ] Functional tests pass
- [ ] Tool integration works (if applicable)
- [ ] Compressed as .zip file (for Claude.ai upload)
- [ ] Version number set in metadata

After upload:
- [ ] Monitor for under/over-triggering
- [ ] Collect user feedback
- [ ] Iterate on description and instructions based on results
- [ ] Update version in metadata after changes

## Version History

- v3.1.0 (2026-03-03): Aligned with Anthropic's Complete Guide to Building Skills PDF
- v3.0.0 (2026-03-02): Rewritten based on Anthropic's Complete Guide to Building Skills, merged with existing community patterns and examples
- v2.0.0 (2025-11-15): Renamed from write-skills, restructured documentation
- v1.0.0 (2025-11-03): Initial version
