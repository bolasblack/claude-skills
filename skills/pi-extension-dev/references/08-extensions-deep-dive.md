# Extensions Deep Dive (Local Reference)

This reference summarizes the pi extension docs and the examples catalog so the skill stays portable.

## Extension locations and loading

- Auto-discovery paths for hot-reloadable extensions:
  - Global: `~/.pi/agent/extensions/*.ts` or `~/.pi/agent/extensions/*/index.ts`
  - Project: `.pi/extensions/*.ts` or `.pi/extensions/*/index.ts`
- Use `pi -e ./path.ts` for quick tests only. For `/reload`, place extensions in auto-discovery locations.
- Settings can add extra paths via `extensions` (see `10-settings-reference.md`).

## Core capabilities

- Register tools with `pi.registerTool()` or `defineTool()` (LLM-callable, typed parameters).
- Register slash commands with `pi.registerCommand()` (supports `getArgumentCompletions`).
- Subscribe to lifecycle/events with `pi.on()` (session, agent, tool, input, model, resources, etc.).
- Customize UI with `ctx.ui.*` (dialogs, widgets, status, custom components, overlays).
- Override built-in tools by registering a tool with the same name.
- Persist state with `pi.appendEntry()` and reconstruct via session entries.
- Inject messages with `pi.sendMessage()` / `pi.sendUserMessage()`.
- Manage tools with `pi.getActiveTools()` / `pi.getAllTools()` / `pi.setActiveTools()`.
- Manage sessions with `pi.setSessionName()` / `pi.getSessionName()` / `pi.setLabel()`.
- Access commands with `pi.getCommands()`.

## Extension structure and imports

- Extensions are TypeScript modules loaded via `jiti` (no build step required).
- Common imports:
  - `@mariozechner/pi-coding-agent` for types/API (`ExtensionAPI`, `defineTool`, `isToolCallEventType`, `withFileMutationQueue`, `keyHint`, etc.)
  - `@sinclair/typebox` for schemas
  - `@mariozechner/pi-tui` for custom UI
  - `@mariozechner/pi-ai` for `StringEnum`
- Node built-ins and local `node_modules` work when a `package.json` is present.

## Events snapshot

- **Resources**: `resources_discover` (contribute skill/prompt/theme paths, fires after `session_start`).
- **Session**: `session_start` (reason: `"startup" | "reload" | "new" | "resume" | "fork"`, includes `previousSessionFile` for new/resume/fork), `session_shutdown`, `session_before_compact`, `session_compact`, `session_before_fork`, `session_before_switch`, `session_before_tree`, `session_tree`.
- **Agent**: `before_agent_start` (can inject message, modify system prompt), `agent_start`, `agent_end`, `turn_start`, `turn_end`.
- **Message**: `message_start`, `message_update`, `message_end`.
- **Tool**: `tool_call` (can block, can mutate `event.input`), `tool_execution_start|update|end`, `tool_result` (can patch results, supports `ctx.signal`), `user_bash`.
- **Input**: `input` (transform, handle, or continue), `context` (message filtering), `before_provider_request` (inspect/replace payload), `model_select`.

### Removed events (v0.65.0)

- ~~`session_switch`~~ — replaced by `session_start { reason: "resume" }`
- ~~`session_fork`~~ — replaced by `session_start { reason: "fork" }`
- ~~`session_directory`~~ — removed entirely

## Tool best practices

- Always truncate tool output. Built-in limits: 50KB or 2000 lines.
- Use `truncateHead`, `truncateTail`, `DEFAULT_MAX_BYTES`, and `DEFAULT_MAX_LINES` from `@mariozechner/pi-coding-agent`.
- Throw errors from `execute()` to mark `isError: true`.
- Use `StringEnum` for string options (Google compatibility).
- For overrides, match built-in result shapes exactly (details types).
- Provide `promptSnippet` so the tool appears in the `Available tools` system prompt section.
- Use `promptGuidelines` for tool-specific `Guidelines` section bullets.
- Use `withFileMutationQueue()` for file-mutating tools (prevents race conditions in parallel execution).
- Use `prepareArguments` for backward compatibility with old session schemas.

## Mode behavior

- `ctx.hasUI` is `false` in print/json; check before using dialogs/UI.
- `ctx.hasUI` is `true` in interactive and RPC modes.
- RPC mode supports UI via protocol; interactive has full TUI.

## Keybinding hints (avoid hardcoding)

- Use `keyHint(keybindingId, description)` to show configured shortcuts.
- Use `keyText(keybindingId)` for raw key text.
- Keybinding ids are namespaced: `app.*` (coding-agent) and `tui.*` (TUI).
- Custom editors and `ctx.ui.custom()` components receive `keybindings: KeybindingsManager`.
- Avoid hardcoded key checks in renderers; use keybinding utilities.

## Custom rendering

Tools can provide `renderCall` and `renderResult`. Both receive a `context` object:

```ts
context.args          // current tool call arguments
context.state         // shared row-local state across renderCall and renderResult
context.lastComponent // previously returned component for reuse
context.invalidate()  // request rerender
context.toolCallId, context.cwd, context.executionStarted
context.argsComplete, context.isPartial, context.expanded
context.showImages, context.isError
```

Best practices:
- Use `Text` with padding `(0, 0)`. The Box handles padding.
- Handle `isPartial` for streaming progress.
- Support `expanded` for detail on demand.
- Read `context.args` in `renderResult` instead of copying args into `context.state`.
- Reuse `context.lastComponent` when the same component instance can be updated in place.

## Examples catalog (from examples/extensions)

High-value examples to copy patterns from:

- **Safety gates**: `permission-gate.ts`, `protected-paths.ts`, `confirm-destructive.ts`
- **Custom tools**: `todo.ts`, `question.ts`, `dynamic-tools.ts`, `truncated-tool.ts`, `tool-override.ts`
- **Commands/UI**: `preset.ts`, `plan-mode/`, `tools.ts`, `handoff.ts`, `send-user-message.ts`, `reload-runtime.ts`, `shutdown-command.ts`
- **Rendering/UI**: `built-in-tool-renderer.ts`, `minimal-mode.ts`, `status-line.ts`, `widget-placement.ts`, `modal-editor.ts`, `overlay-qa-tests.ts`, `timed-confirm.ts`
- **Providers**: `custom-provider-anthropic/`, `custom-provider-gitlab-duo/`
- **Remote**: `ssh.ts`, `interactive-shell.ts`, `sandbox/`
- **Sessions**: `session-name.ts`, `bookmark.ts`, `git-checkpoint.ts`, `auto-commit-on-exit.ts`
- **Messages**: `message-renderer.ts`, `event-bus.ts`, `file-trigger.ts`
- **Games**: `snake.ts`, `space-invaders.ts`, `doom-overlay/`

Use these as references for reliable event wiring, UI calls, and tool patterns.
