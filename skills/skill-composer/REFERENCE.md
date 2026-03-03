# Skill Composer Reference

Technical specifications, workflow patterns, and example analysis for Claude Code Skills.

## Skills and MCP Relationship

Think of it like a professional kitchen. **MCP provides the kitchen** — access to tools, ingredients, and equipment (connecting Claude to services like Notion, Asana, Linear, etc.). **Skills provide the recipes** — step-by-step instructions on how to create something valuable.

Together, they enable users to accomplish complex tasks without needing to figure out every step themselves.

| MCP (Connectivity) | Skills (Knowledge) |
|--------------------|--------------------|
| Connects Claude to your service | Teaches Claude how to use your service effectively |
| Provides real-time data access and tool invocation | Captures workflows and best practices |
| What Claude can do | How Claude should do it |

**Without skills:** Users connect your MCP but don't know what to do next. Support tickets asking "how do I do X with your integration." Each conversation starts from scratch. Inconsistent results because users prompt differently each time.

**With skills:** Pre-built workflows activate automatically when needed. Consistent, reliable tool usage. Best practices embedded in every interaction. Lower learning curve for your integration.

Skills position your MCP as a complete solution — not just connectivity, but knowledge.

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
| `name` | string | kebab-case only. Max 64 chars. No spaces, underscores, or capitals. Must match folder name. |
| `description` | string | Max 1024 chars. MUST include what AND when. No XML tags (`<` `>`). |

### Optional Fields

```yaml
---
name: "skill-name"
description: "Description here"
allowed-tools: Read, Grep, Glob
license: MIT
compatibility: "Requires Claude Code with bash access"
metadata:
  author: Company Name
  version: 1.0.0
  mcp-server: server-name
  category: productivity
  tags: [project-management, automation]
  documentation: https://example.com/docs
  support: support@example.com
---
```

| Field | Type | Purpose |
|-------|------|---------|
| `allowed-tools` | string | Restricts which tools Claude can use when skill is active |
| `license` | string | Open source license (MIT, Apache-2.0, etc.) |
| `compatibility` | string | Environment requirements, 1-500 chars |
| `metadata` | object | Custom key-value pairs (author, version, mcp-server, etc.) |

### Security Restrictions

**Forbidden in frontmatter**:
- XML angle brackets (`<` `>`) - frontmatter appears in system prompt, could inject instructions
- Names prefixed with "claude" or "anthropic" (reserved)
- Code execution in YAML (safe YAML parsing enforced)

## Tool Restrictions

When using `allowed-tools`, specify any combination of:

- **Read** - Read files from filesystem
- **Write** - Write new files
- **Edit** - Edit existing files
- **Bash** - Execute shell commands (supports scoping: `Bash(python:*)`)
- **Grep** - Search file contents with patterns
- **Glob** - Find files by pattern matching
- **WebFetch** - Fetch content from URLs
- **WebSearch** - Search the web
- **Task** - Launch specialized sub-agents
- **TodoWrite** - Manage task lists
- **Skill** - Load other skills
- **SlashCommand** - Execute slash commands
- **AskUserQuestion** - Prompt user for input

### Common Restriction Patterns

**Read-only analysis** (code review, security audits):
```yaml
allowed-tools: Read, Grep, Glob
```

**Research only** (information gathering, docs lookup):
```yaml
allowed-tools: Read, WebFetch, WebSearch, Grep, Glob
```

**Safe file operations** (generation, no destructive edits):
```yaml
allowed-tools: Read, Write, Bash
```

**Scoped bash with web** (specific interpreters only):
```yaml
allowed-tools: "Bash(python:*) Bash(npm:*) WebFetch"
```

**Full access** (default - omit `allowed-tools` field):
```yaml
# No allowed-tools field = all tools available
```

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

Scripts for programmatic validation and utilities. Remember `chmod +x` and shebang lines.

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

- Execute permissions: `chmod +x scripts/*.sh`
- Shebang lines: `#!/usr/bin/env python3` or `#!/usr/bin/env bash`
- Forward slashes only (Unix-style paths)
- Document dependencies in skill description

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
- **Tool-first**: "I have Notion MCP connected" — Your skill teaches Claude the optimal workflows and best practices. Users have access; the skill provides expertise.

Most skills lean one direction. Knowing which framing fits your use case helps you choose the right pattern below.

| Approach | User starts with | Skill provides | Best patterns |
|----------|-----------------|----------------|---------------|
| Problem-first | A goal or outcome | Tool orchestration, sequencing | Sequential Orchestration, Multi-MCP Coordination |
| Tool-first | An MCP or tool | Best practices, domain knowledge | Domain-Specific Intelligence, Context-Aware Selection |

## Pattern Selection Guide

### From Real-World Examples

#### Discipline Enforcement (like TDD example)
**Use when**: Need to enforce strict methodology.
**Techniques**: Iron Laws (unbreakable rules), rationalization tables (pre-empt excuses), verification checklists, red flags for self-monitoring.

#### Four-Phase Methodology (like Systematic Debugging)
**Use when**: Complex process with clear stages.
**Techniques**: Phase gates, stopping rules (three-fix rule), sub-skill integration, meta-cognitive monitoring.

#### Helper Scripts (like Web App Testing)
**Use when**: Complex setup better handled by code.
**Techniques**: Black box philosophy (don't pollute context), `--help` first (self-documenting), decision trees, extreme conciseness (~96 lines).

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

### Common Patterns Across All Examples

1. **Clear structure**: Well-defined sections
2. **Explicit principles**: Core principles stated upfront
3. **Concrete examples**: Code snippets, commands, workflows
4. **Tables for reference**: Quick reference, comparisons, checklists
5. **Red flags/warnings**: What NOT to do
6. **Integration guidance**: How skills relate to each other

### Key Insights

**From Community (obra/superpowers)**:
- Rationalization pre-emption (TDD)
- Stopping rules (Systematic Debugging)
- Safety verification (Git Worktrees)
- Sub-skill integration
- Human partner signals

**From Official (anthropics/skills)**:
- Extreme conciseness (Web App Testing: 96 lines)
- Black box philosophy (helper scripts)
- WebFetch integration (MCP Builder)
- Zero-tolerance policies (XLSX)
- MANDATORY reads (DOCX)
- Progressive reference loading

### Anti-Patterns

What good skills DON'T do:
- Vague descriptions
- Multiple unrelated capabilities
- Ambiguous instructions
- Skip verification steps
- Missing version history
- Assume context without checking
- Skip safety verification
- Pollute context with large files

**Tip: Code > language for validation.** For critical validations, consider bundling a script that performs checks programmatically rather than relying on language instructions alone. Code is deterministic; language interpretation isn't. See the Office skills (XLSX, DOCX) for examples of this pattern.

## Testing Methodology

### 1. Triggering Tests

Goal: Skill loads at the right times.

```
Should trigger:
- "Help me set up a new ProjectHub workspace"
- "I need to create a project in ProjectHub"
- "Initialize a ProjectHub project for Q4 planning"

Should NOT trigger:
- "What's the weather in San Francisco?"
- "Help me write Python code"
- "Create a spreadsheet" (unless skill handles that)
```

### 2. Functional Tests

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

### 3. Performance Comparison

Goal: Skill improves over baseline.

| Metric | Without Skill | With Skill |
|--------|--------------|------------|
| Back-and-forth messages | 15 | 2 clarifying questions |
| Failed API calls | 3 requiring retry | 0 |
| Tokens consumed | 12,000 | 6,000 |

Use your success criteria measurements to populate this table. Three testing approaches based on audience size: **Manual testing in Claude.ai** for fast iteration with no setup, **Scripted testing in Claude Code** for repeatable validation across changes, and **Programmatic testing via Skills API** for systematic evaluation at scale. Choose the approach that matches your quality requirements and deployment scope.

### Iteration Signals

**Undertriggering** (skill doesn't load when it should):
- Users manually enabling it
- Support questions about when to use it
- Fix: Add more detail, keywords, and technical terms to description

**Overtriggering** (skill loads for unrelated queries):
- Users disabling it
- Confusion about purpose
- Fix: Add negative triggers, be more specific, clarify scope

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

Debug: Ask Claude "When would you use the [skill name] skill?" - adjust based on what's missing.

### Skill Triggers Too Often

1. Add negative triggers: `"Do NOT use for simple data exploration"`
2. Be more specific: `"PDF legal documents for contract review"` not `"documents"`
3. Clarify scope: `"Use specifically for online payment workflows, not for general financial queries"`

### Instructions Not Followed

1. **Too verbose** - Use bullet points, numbered lists, move details to references/
2. **Instructions buried** - Put critical instructions at the top, use `## Critical` headers
3. **Ambiguous language** - Replace "validate things properly" with explicit checklists
4. **Model laziness** - When Claude rushes through tasks or skips validation steps, add explicit encouragement:

   ```
   ## Performance Notes
   - Take your time to do this thoroughly
   - Quality is more important than speed
   - Do not skip validation steps
   ```

   Note: Adding this to user prompts is more effective than placing it in SKILL.md. Consider instructing users to include performance notes in their initial prompt for best results.

### Large Context Issues

Symptoms: Slow responses, degraded quality.

Solutions:
1. Keep SKILL.md under **5,000 words** - move details to references/
2. Evaluate if more than 20-50 skills are enabled simultaneously
3. Ensure progressive disclosure is working (not loading everything upfront)

### Skill Packs

If you have many related capabilities, consider grouping them into a **skill pack** — a single skill that bundles related functions together. This reduces the number of simultaneously enabled skills and helps Claude select the right capability without scanning dozens of descriptions.

Use skill packs when:
- You have 3+ skills that share the same MCP server or domain
- Users typically need several related capabilities in one session
- Description overlap causes triggering conflicts between related skills

### MCP Connection Issues

1. Verify MCP server is connected (Settings > Extensions)
2. Check authentication (API keys valid, proper scopes)
3. Test MCP independently (ask Claude to call MCP directly without skill)
4. Verify tool names match MCP server documentation (case-sensitive)

### Debug Mode (Claude Code)

```bash
claude --debug
```

Look for YAML parsing errors, file loading messages, and skill activation logs.

## Distribution

### Claude.ai Upload Path

How individual users get skills:

1. Download the skill folder
2. Zip the folder (if needed)
3. Upload to Claude.ai via Settings > Capabilities > Skills
4. Or place in Claude Code skills directory

### When to Use API vs Claude.ai

| Use Case | Best Surface |
|----------|-------------|
| End users interacting with skills directly | Claude.ai / Claude Code |
| Manual testing and iteration during development | Claude.ai / Claude Code |
| Individual, ad-hoc workflows | Claude.ai / Claude Code |
| Applications using skills programmatically | API |
| Production deployments at scale | API |
| Automated pipelines and agent systems | API |

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

Skills in `skills/` are discovered automatically - no plugin.json entries needed.

### GitHub

1. Host skill in public repo with clear README (at repo level, not inside skill folder)
2. Add installation instructions and example usage with screenshots
3. Link from MCP documentation if applicable
4. Compress as `.zip` for users who want to upload directly to Claude.ai

The `anthropics/skills` repository on GitHub contains Anthropic-created skills you can browse and customize. See also the MCP documentation cross-reference guidance in [Document in Your MCP Repo](#document-in-your-mcp-repo) below.

### Installation Guide Template

Include a guide like this in your repo README:

```markdown
## Installing the [Your Service] skill

1. Download the skill:
   - Clone repo: `git clone https://github.com/yourcompany/skills`
   - Or download ZIP from Releases

2. Install in Claude:
   - Open Claude.ai > Settings > skills
   - Click "Upload skill"
   - Select the skill folder (zipped)

3. Enable the skill:
   - Toggle on the [Your Service] skill
   - Ensure your MCP server is connected

4. Test:
   - Ask Claude: "Set up a new project in [Your Service]"
```

### Positioning Your Skill

How you describe your skill determines whether users understand its value and actually try it. When writing about your skill — in your README, documentation, or marketing — keep these principles in mind.

**Focus on outcomes, not features:**

Good: *"The ProjectHub skill enables teams to set up complete project workspaces in seconds — including pages, databases, and templates — instead of spending 30 minutes on manual setup."*

Bad: *"The ProjectHub skill is a folder containing YAML frontmatter and Markdown instructions that calls our MCP server tools."*

**Highlight the MCP + skills story:**

*"Our MCP server gives Claude access to your Linear projects. Our skills teach Claude your team's sprint planning workflow. Together, they enable AI-powered project management."*

### Document in Your MCP Repo

If you maintain an MCP server, link to your skills from the MCP documentation:

- Link to skills from MCP documentation
- Explain the value of using both together
- Provide a quick-start guide that covers MCP setup and skill installation

### Organization Deployment

Shipped December 18, 2025. Admins can deploy skills workspace-wide through the Claude Console:

- **Workspace-wide deploy**: Push skills to all users in the organization at once
- **Automatic updates**: Changes propagate without users needing to re-download
- **Centralized management**: Control which skills are active across your organization

#### Version Control through Claude Console

Version control and management through the Claude Console lets admins track skill versions, roll back changes, and manage deployment across teams.

#### Open Standard Philosophy

Skills are designed as an open, portable standard. A skill built for Claude.ai works identically in Claude Code and the API. This cross-platform portability means you're not locked into a single surface — build once, deploy anywhere. The `compatibility` field in frontmatter captures environment requirements, enabling ecosystem collaboration where skills can declare what they need and run wherever those requirements are met.

### API Usage

For programmatic use cases — such as building applications, agents, or automated workflows that leverage skills — the API provides direct control over skill management and execution.

Key capabilities:

- `/v1/skills` endpoint for listing and managing skills
- Add skills to Messages API requests via the `container.skills` parameter
- Version control and management through the Claude Console
- Works with the Claude Agent SDK for building custom agents

Skills in the API require the Code Execution Tool beta, which provides the secure sandbox environment skills need to run.

For implementation details, see:

- Skills API Quickstart
- Create Custom Skills
- Skills in the Agent SDK

## Skills vs Slash Commands

| Aspect | Skills | Slash Commands |
|--------|--------|----------------|
| **Invocation** | Automatic (model-invoked) | Manual (user types /command) |
| **Complexity** | Complex capabilities with structure | Simple prompts |
| **Files** | Directory with SKILL.md + supporting files | Single markdown file |
| **Discovery** | Based on description matching | Explicit user command |
| **Use case** | Claude should discover automatically | User wants explicit control |

**Choose Skills when**: Context-based activation needed, complex workflows, multiple files/scripts, team standardization.

**Choose Slash Commands when**: Explicit invocation control, simple single-file prompt, repeated identical instructions.

## Version History Format

```markdown
## Version History
- v2.0.0 (2025-11-15): Breaking change - new API format
- v1.1.0 (2025-11-10): Added feature X
- v1.0.1 (2025-11-05): Fixed bug Y
- v1.0.0 (2025-11-03): Initial version
```

Semantic versioning: Major (breaking), Minor (features, backward compatible), Patch (bug fixes).

## Skill Examples

Seven real-world examples in [examples/](examples/):

| Example | Lines | Pattern | Source | Key Feature |
|---------|-------|---------|--------|-------------|
| [TDD](examples/tdd.md) | ~365 | Discipline enforcement | obra/superpowers | Rationalization tables |
| [Systematic Debugging](examples/systematic-debugging.md) | ~296 | Four-phase methodology | obra/superpowers | Three-fix rule |
| [Web App Testing](examples/webapp-testing.md) | ~96 | Helper scripts | anthropics/skills | Black box philosophy |
| [MCP Builder](examples/mcp-builder.md) | ~329 | Comprehensive framework | anthropics/skills | WebFetch integration |
| [XLSX](examples/xlsx.md) | ~289 | Production standards | anthropics/skills | Zero formula errors |
| [DOCX](examples/docx.md) | ~197 | Decision tree + externals | anthropics/skills | MANDATORY file reads |
| [Git Worktrees](examples/git-worktrees.md) | ~214 | Safety workflow | obra/superpowers | .gitignore verification |

**By use case category:**
- **Document & Asset Creation**: XLSX, DOCX — producing formatted documents and assets with domain-specific quality standards
- **Workflow Automation**: TDD, Systematic Debugging, MCP Builder — enforcing step-by-step processes and consistent methodology
- **MCP Enhancement**: Web App Testing, Git Worktrees — enhancing tool access with best practices and safety workflows

## Resources & Community

If you're building your first skill, start with the Best Practices Guide, then reference the API docs as needed.

### Official Documentation

- [Best Practices Guide](https://docs.anthropic.com/en/docs/build-with-claude/agent-skills/best-practices) — comprehensive guide to building effective skills
- [Skills Documentation](https://docs.anthropic.com/en/docs/build-with-claude/agent-skills) — core concepts and configuration
- [API Reference](https://docs.anthropic.com/en/api) — endpoints and parameters for programmatic usage
- [MCP Documentation](https://modelcontextprotocol.io) — Model Context Protocol specification and guides

### Blog Posts

- [Introducing Agent Skills](https://www.anthropic.com/news/agent-skills) — launch announcement and overview
- [Engineering Blog: Equipping Agents for the Real World](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world) — technical deep-dive on agent architecture
- [Skills Explained](https://www.anthropic.com/news/skills-explained) — conceptual overview of what skills are and why they matter
- [How to Create Skills for Claude](https://www.anthropic.com/news/how-to-create-skills-for-claude) — step-by-step creation tutorial
- [Building Skills for Claude Code](https://www.anthropic.com/news/building-skills-for-claude-code) — Claude Code-specific skill development
- [Improving Frontend Design through Skills](https://www.anthropic.com/news/improving-frontend-design-through-skills) — case study on design-focused skills

### Public Skills Repository

GitHub: [anthropics/skills](https://github.com/anthropics/skills) — Contains Anthropic-created skills you can browse and customize. Use these as reference implementations when building your own.

### skill-creator Tool

Built into Claude.ai and available for Claude Code:

- Generate skills from descriptions: "Help me build a skill using skill-creator"
- Review existing skills: "Review this skill and suggest improvements"
- Validates structure, frontmatter, and best practices
- Use it to generate your first draft, then iterate manually

### Getting Support

**For technical questions:**
- Community forums at the [Claude Developers Discord](https://discord.gg/claudedev) — general questions, best practices, sharing skills

**For bug reports:**
- GitHub Issues: [anthropics/skills/issues](https://github.com/anthropics/skills/issues)
- Include: skill name, error message, steps to reproduce

## Version History

- v3.1.0 (2026-03-03): Aligned with Anthropic's Complete Guide to Building Skills PDF
- v3.0.0 (2026-03-03): Initial reference document
