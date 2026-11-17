# Portability

## Portable Core and Harness Enhancements

The portable-core decision is owned by [Portability](../SKILL.md#portability). When Step 1
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

## Skills and MCP Relationship

MCP supplies connectivity and callable tools; skills supply reusable instructions, workflow, and domain judgment. Either can stand alone, and a skill may coordinate built-in tools, MCP tools, or no tools at all.

| MCP (Connectivity) | Skills (Knowledge) |
|--------------------|--------------------|
| Connects an agent to a service | Teaches an agent how to use capabilities effectively |
| Provides real-time data access and tool invocation | Captures workflows and best practices |
| What an agent can do | How an agent should do it |

Model-invoked skills may load automatically from context; user-invoked skills run only when selected. Do not describe automatic activation as a property of every skill.
