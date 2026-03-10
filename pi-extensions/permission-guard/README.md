# Permission Guard Extension — Behavioral Spec

## Scope
- Governs tool permissions for: `bash`, `read`, `write`, `edit`.
- Default policy is deny-by-confirmation for risky access, with persisted allow rules.
- Emergency bypass: set `PI_PERMISSION_GUARD_BYPASS=1` (also accepts `true`/`yes`) to skip all permission checks.

## Policy Rules
1. `bash`
   - Always requires approval unless matched by an allow rule.
   - Exception: commands explicitly documented in skill markdown command blocks are auto-allowed.
   - Matching is strict (normalized exact command), not prefix-based.

2. File tools (`read`/`write`/`edit`)
   - Paths inside current project root (`ctx.cwd`) are allowed by default.
   - Paths outside project root require approval unless matched by an allow rule.

3. Skill paths
   - Skill approvals are represented as:
     - `Skill($user/<skill-name>)`
     - `Skill($project/<skill-name>)`
   - `Skill(...)` grants read access to files under that skill directory.
   - Writes/edits to skill files still require separate explicit approval.

## Decision Surfaces
- Permission can be decided from either interactive dialog or system notification actions.
- Both surfaces race in parallel when applicable.
- First valid decision wins; the other surface is canceled/closed.
- Clicking notification content focuses the Pi terminal pane, but does not by itself approve/deny.

## Integration Contract (with `system-notify` extension)
- This extension declares intent (title/message/actions) and consumes decisions.
- Notification implementation details are delegated to `system-notify`.
- Event channels:
  1. `system-notify:action-prompt-request`
     - payload: `{ requestId, title, message, actions, closeLabel?, timeoutSeconds? }`
     - default behavior: `timeoutSeconds` is omitted (no timeout)
  2. `system-notify:action-prompt-result`
     - payload: `{ requestId, action?, activationType? }`
  3. `system-notify:action-prompt-cancel`
     - payload: `{ requestId }`
- `requestId` correlates request/result/cancel and must be unique per permission prompt.

## Visibility Gate for Notifications
- If Pi pane is already visible/active, no notification surface is required.
- “Visible” means:
  - active terminal pane in active terminal tab/window
  - and when running under tmux, active window + active pane (non-hidden by zoom/focus state)

## Persisted Rules
- Project-level file: `<project>/.pi/permission-guard.json`
- User-level file: `~/.pi/agent/permission-guard.json`
- Schema: `{ "allowedRules": string[] }`
- Effective rule set is the union of project + user rules.

## Rule Grammar (glob-aware)
- `Bash(<glob>)`
- `FileRead(<glob>)`
- `FileWrite(<glob>)`
- `FileEdit(<glob>)`
- `Skill($user/<name>)`
- `Skill($project/<name>)`

## User Choices
- Allow
- Allow always (project level)
- Allow always (user level)
- Deny
- Deny with note
