# 04. Testing and Debugging

## Validation checklist

1. Extension loads successfully.
2. Registered command appears and executes.
3. Tool can be called by model.
4. `tool_call` guard blocks dangerous actions.
5. Large output truncation works.
6. Behavior is acceptable in interactive/print/json/rpc modes.
7. File-mutating tools use `withFileMutationQueue()`.
8. `promptSnippet` is set so tool appears in system prompt `Available tools` section.

## Mode behavior sanity checks

- Interactive: verify dialogs, widgets, custom UI, and keybindings.
- Print (`-p`) and JSON (`--mode json`): ensure UI calls are guarded by `ctx.hasUI` and no crashes occur.
- RPC (`--mode rpc`): confirm UI dialogs work through the extension UI protocol and that non-dialog UI calls are safe no-ops.

## Practical smoke tests

- Start with direct extension path:

```bash
pi --no-extensions -e ./.pi/extensions/my-ext.ts
```

- Move to discovered location and run `/reload`.

## Common failures

- Missing API key/provider auth for selected model.
- Hardcoded model in agent frontmatter not available in current environment.
- UI method usage in non-interactive mode without guard.
- Command/tool naming collisions across multiple extensions (resolved via numeric suffixes since v0.62.0).
- Using removed `getApiKey()` instead of `getApiKeyAndHeaders()`.
- Using removed events (`session_switch`, `session_fork`, `session_directory`).
- Missing `promptSnippet` causing tool to not appear in system prompt.
- File mutations without `withFileMutationQueue()` causing race conditions.

## Subagent-specific checks

- Verify agent discovery (`~/.pi/agent/agents` and/or `.pi/agents`).
- Keep `model` optional where portability matters.
- If `model` is explicit, verify with `pi --list-models`.

## Debugging playbook

- Start with a minimal run: `pi --no-extensions -e ./path/to/ext.ts`.
- Toggle built-ins to isolate: `--no-tools`, `--no-skills`, `--no-prompt-templates`, `--no-themes`.
- Reproduce in `--mode json` and `--mode rpc` to validate non-UI behavior.
- Use `before_provider_request` to log payloads when debugging provider serialization.
- Add temporary `ctx.ui.notify` or `console.log` for event ordering, then remove.
- Check startup diagnostics for structured `info`/`warning`/`error` messages.

## Diagnostics to collect

- exact extension path loaded
- selected model/provider
- mode (`interactive`, `print`, `json`, `rpc`)
- reproduction command
- full error text
- `sourceInfo` on resources/tools/commands for provenance
