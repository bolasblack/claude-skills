# 01. Extension API Cheatsheet

This reference summarizes high-value extension APIs for `@mariozechner/pi-coding-agent`.

## Core extension shape

```ts
import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";

export default function (pi: ExtensionAPI) {
  // register tools/commands/hooks
}
```

## Most-used hooks

- `session_start` / `session_shutdown`
- `session_before_switch`
- `session_before_fork`
- `session_before_compact` / `session_compact`
- `session_before_tree` / `session_tree`
- `resources_discover`
- `input` (pre-skill/prompt expansion)
- `before_agent_start` / `agent_start` / `agent_end`
- `turn_start` / `turn_end`
- `message_start` / `message_update` / `message_end`
- `context` (modify outbound context messages)
- `before_provider_request` (inspect/patch/replace provider payload)
- `tool_call` (can block, can mutate `event.input`)
- `tool_execution_start` / `tool_execution_update` / `tool_execution_end`
- `tool_result` (can patch, supports `ctx.signal`)
- `user_bash`
- `model_select`

### Removed events (v0.65.0)

- ~~`session_switch`~~ — Use `session_start` with `event.reason === "resume"` and `event.previousSessionFile`.
- ~~`session_fork`~~ — Use `session_start` with `event.reason === "fork"` and `event.previousSessionFile`.
- ~~`session_directory`~~ — Removed entirely.

## ExtensionContext highlights

- `ctx.hasUI` and `ctx.ui` (dialogs, status, widgets, editor, theme control)
- `ctx.sessionManager` (entries, branches, labels)
- `ctx.modelRegistry` / `ctx.model` (current model, model lookup)
- `ctx.modelRegistry.getApiKeyAndHeaders(model)` (replaces removed `getApiKey()`)
- `ctx.signal` (agent abort signal for nested async work)
- `ctx.getContextUsage()` and `ctx.getSystemPrompt()`
- `ctx.compact()` for manual compaction
- `ctx.shutdown()` for graceful exit
- `ctx.isIdle()` / `ctx.abort()` / `ctx.hasPendingMessages()`

Command handlers also receive `ExtensionCommandContext` with:
- `ctx.waitForIdle()`
- `ctx.reload()` (same as `/reload`)
- `ctx.newSession()`, `ctx.fork()`, `ctx.navigateTree()`, `ctx.switchSession()`

## Tool registration

### pi.registerTool()

Register tools with strict schema (`Type.Object`) and clear descriptions.

Requirements:
- Truncate large outputs.
- Throw for tool failures (do not silently return fake success).
- Normalize path inputs if your tool accepts `@path` style references.
- Provide `promptSnippet` for a one-line entry in `Available tools` system prompt section.
  Omitting `promptSnippet` leaves the tool out of that section entirely.
- Use `promptGuidelines` to add bullets to the `Guidelines` section when tool is active.

### defineTool() helper

Use `defineTool()` for standalone tool definitions with full TypeScript parameter type inference:

```ts
import { defineTool } from "@mariozechner/pi-coding-agent";
import { Type } from "@sinclair/typebox";

const myTool = defineTool({
  name: "my_tool",
  label: "My Tool",
  description: "What this tool does",
  promptSnippet: "Short summary for system prompt",
  parameters: Type.Object({
    text: Type.String({ description: "Input text" }),
  }),
  async execute(_toolCallId, params) {
    // params.text is correctly typed as string
    return { content: [{ type: "text", text: params.text }], details: {} };
  },
});

pi.registerTool(myTool);
```

### prepareArguments hook

Optional hook that runs before schema validation. Use it to normalize old session arguments:

```ts
pi.registerTool({
  // ...
  prepareArguments(args) {
    const input = args as { oldField?: string; newField?: string };
    if (input.oldField && !input.newField) {
      return { ...input, newField: input.oldField };
    }
    return args;
  },
});
```

## File mutation queue

Custom tools that mutate files must use `withFileMutationQueue()` to avoid race conditions
with built-in `edit` and `write` during parallel tool execution:

```ts
import { withFileMutationQueue } from "@mariozechner/pi-coding-agent";
import { resolve } from "node:path";

async execute(_toolCallId, params, _signal, _onUpdate, ctx) {
  const absolutePath = resolve(ctx.cwd, params.path);
  return withFileMutationQueue(absolutePath, async () => {
    // read-modify-write inside the queue
    return { content: [{ type: "text", text: "Done" }], details: {} };
  });
}
```

## Tool overrides

Extensions can override built-in tools (`read`, `bash`, `edit`, `write`, `grep`, `find`, `ls`) by registering a tool with the same name.

Key rules:
- Match the built-in tool result shape (`content`, `details`, `isError` types).
- If you do not provide custom renderers, the built-in renderer is reused per slot.
- `promptSnippet` and `promptGuidelines` are NOT inherited; define explicitly on the override.
- Use `--no-tools` to run with only extension tools.

## Output truncation

Use truncation helpers from `@mariozechner/pi-coding-agent`:
- `truncateHead`, `truncateTail`, `truncateLine`
- `DEFAULT_MAX_BYTES` (50KB) and `DEFAULT_MAX_LINES` (2000)

Always inform the model when output is truncated and where the full output is stored.

## Command registration

Use `pi.registerCommand("name", { ... })` for slash commands.

Guidance:
- Keep command handlers idempotent.
- Guard UI calls with `ctx.hasUI` when behavior must work in non-interactive modes.
- If multiple extensions register the same command name, pi assigns numeric suffixes (e.g., `/review:1`, `/review:2`).
- Use `getArgumentCompletions` for Tab auto-completion of command arguments.

```ts
pi.registerCommand("deploy", {
  description: "Deploy to an environment",
  getArgumentCompletions: (prefix: string) => {
    const envs = ["dev", "staging", "prod"];
    return envs.filter(e => e.startsWith(prefix)).map(e => ({ value: e, label: e }));
  },
  handler: async (args, ctx) => { /* ... */ },
});
```

## Shortcuts and flags

- `pi.registerShortcut("ctrl+shift+p", { ... })` for keyboard shortcuts.
- `pi.registerFlag("name", { type: "boolean" | "string" | "number", default })` for CLI flags.
- Use `keyHint(keybindingId, description)` to show configured shortcuts in renderers.
- Use `keyText(keybindingId)` for raw key text.
- Use `rawKeyHint(key, description)` for non-configurable keys.
- Keybinding ids are namespaced: `app.*` (coding-agent) and `tui.*` (shared TUI).

## Message injection: sendMessage vs sendUserMessage

- `pi.sendMessage()` injects a custom message (e.g., status or metadata) with optional delivery modes: `steer`, `followUp`, `nextTurn`.
- `pi.sendUserMessage()` injects a *user* message and always triggers a turn. When the agent is streaming, you must pass `deliverAs` (`steer` or `followUp`).
- Use `sendMessage` for extension metadata; use `sendUserMessage` when you want the agent to treat it as user input.

## Dynamic provider registration

Use `pi.registerProvider()` and `pi.unregisterProvider()` for custom/proxy providers.

Calls during extension factory are queued and applied on runner init.
Calls after that take effect immediately without `/reload`.

Use cases:
- Team proxy endpoint
- OAuth custom provider
- Non-default headers/auth behavior
- Non-standard streaming APIs (`streamSimple`)

See `references/06-provider-integrations.md` for OAuth and streaming details.

## UI customization surface

`ctx.ui` supports:
- dialogs: `select`, `confirm`, `input`, `editor` (all support `timeout` and `signal` options)
- display: `notify`, `setStatus`, `setWidget`, `setFooter`, `setHeader`, `setTitle`
- working: `setWorkingMessage` (shown during streaming)
- editor control: `setEditorText`, `getEditorText`, `pasteToEditor`, `setEditorComponent`
- tool display: `getToolsExpanded()`, `setToolsExpanded()`
- theme: `getAllThemes()`, `getTheme()`, `setTheme()`
- thinking: `setHiddenThinkingLabel()` (customize collapsed thinking label)
- custom components: `ctx.ui.custom()` with optional overlay mode

Mode caveat:
- Interactive: full UI
- RPC: mediated via extension UI protocol
- JSON/Print: UI methods are no-op or limited

## Source provenance

All resources, commands, tools, skills, and prompt templates carry `sourceInfo`:

```ts
{
  path: string;
  source: string;       // "builtin", "sdk", or extension metadata
  scope: "user" | "project" | "temporary";
  origin: "package" | "top-level";
  baseDir?: string;
}
```

Use `sourceInfo` for provenance. Do not use legacy `extensionPath` or `source` fields (removed in v0.62.0).

## Subagent model policy for agent files

When defining subagents in markdown (`~/.pi/agent/agents/*.md` or `.pi/agents/*.md`):

1. Treat `model` as optional.
2. Prefer omitting `model` for portable setups.
3. If you set `model`, verify availability first: `pi --list-models`
4. Add a fallback note: "If this model is unavailable, use any equivalent reasoning-capable model."
