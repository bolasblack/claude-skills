# System Notify Extension — Behavioral Spec

## Scope
- Provides system-level notifications for Pi events.
- Implements notification-backed action prompts used by `permission-guard`.

## Responsibilities
1. Passive notifications
   - Notify when agent work completes.
   - Notify when a permission prompt is raised.

2. Action prompts
   - Render actionable notification prompts with provided actions.
   - Return selected action back to caller via event bus.
   - Support cancellation of in-flight prompts.

3. Focus behavior
   - Clicking notification content should focus the Pi terminal pane.
   - Clicking the first action button ("显示" / "Focus terminal") should focus the Pi terminal pane.
   - Clicking any other action button should NOT focus/switch pane.
   - Focus attempts terminal activation first, then pane/window selection.

4. Visibility gate
   - If Pi pane is already visible, passive notifications may be skipped.

## Integration Contract (with `permission-guard`)

### Request event
- Channel: `system-notify:action-prompt-request`
- Payload:
```ts
{
  requestId: string;
  title: string;
  message: string;
  actions: string[];
  closeLabel?: string;
  timeoutSeconds?: number; // optional; if omitted, no timeout is applied
}
```

### Result event
- Channel: `system-notify:action-prompt-result`
- Payload:
```ts
{
  requestId: string;
  action?: string;
  activationType?: string;
}
```

### Cancel event
- Channel: `system-notify:action-prompt-cancel`
- Payload:
```ts
{ requestId: string }
```

## Correlation semantics
- `requestId` uniquely identifies one prompt lifecycle.
- Exactly one result should be emitted per request (unless cancelled before any user action).
- Cancel should close/remove active prompt UI when possible.

## Platform behavior
- macOS implementation lives in `macos-wez.ts`.
- Non-supported platforms use no-op behavior by default (no crashes, no hard failures).
- Debug logging is disabled by default. Set `PI_SYSTEM_NOTIFY_DEBUG=1` to enable logs at `~/.pi/agent/system-notify.log`.

## Files
- `index.ts`: event bus wiring + extension entrypoint
- `macos-wez.ts`: macOS notification/focus implementation
- `vendor/`: local notification runtime assets
