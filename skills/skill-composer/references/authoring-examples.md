# Authoring Examples

## Use Case Examples

Lookup material for [Planning Before Creating or Updating](../SKILL.md#planning-before-creating-or-updating).

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

### Description Examples

Examples for [Step 4](../SKILL.md#step-4-write-the-description), following `[What it does] + [When to use it] + [Key capabilities]`:

```yaml
# Good - specific with trigger phrases
description: "Analyzes Figma design files and generates developer handoff
  documentation. Use when user uploads .fig files, asks for 'design specs',
  'component documentation', or 'design-to-code handoff'."

# Bad - no triggers
description: "Helps with projects"
```

## Instruction Template

A copy-and-adapt starting shape for [Step 5](../SKILL.md#step-5-write-instructions). Every step keeps its own **Done when:** criterion.

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
