# js-code-simplifier

> **Sunset:** this agent is no longer installable from this repository and will be removed in the future. It is an unmodified import of the `code-simplifier` agent from Anthropic's official plugin repository; it presents one upstream project's code style (prefer the `function` keyword, explicit return types, and so on) as if it were the current project's standards, and it tells itself to run proactively without being asked. Use the simplify command built into your agent runner (Claude Code's `/simplify`) instead, or the upstream [`code-simplifier`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier) plugin if you want the original.

Simplifies and refines code for clarity, consistency, and maintainability while preserving all functionality.

## Description

An expert code simplification agent that enhances code clarity, consistency, and maintainability while preserving exact functionality. Focuses on recently modified code unless instructed otherwise.

Key capabilities:
- Preserves functionality while improving code structure
- Applies project-specific coding standards from CLAUDE.md
- Reduces unnecessary complexity and nesting
- Eliminates redundant code and abstractions
- Prioritizes clarity over brevity

## Acknowledgments

Imported from [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official/blob/main/plugins/code-simplifier/agents/code-simplifier.md).
