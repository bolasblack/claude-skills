# Workflow Patterns

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
