# Grok — Second Opinion (xAI Grok)

Get an independent second opinion from xAI's Grok via the `grok` CLI — a different AI system reviewing with fresh eyes and no stake in the plan.

## Modes

- **Review** (`/grok review [focus]`) — independent diff review against the base branch with a `[P1]`/`[P2]` pass/fail gate
- **Challenge** (`/grok challenge [focus]`) — adversarial pass that hunts for edge cases, race conditions, security holes, and failure modes
- **Consult** (`/grok <question>`) — ask Grok anything, with session continuity for follow-ups

Every call runs Grok read-only — `--permission-mode plan` plus `--disallowed-tools` for the file-write tools, since plan mode alone does not block them — presents its output verbatim, and closes with a one-line actionable recommendation. When Claude reviewed the same changes, a cross-model comparison is appended.

## Requirements

- Grok CLI installed and authenticated via `grok login`
- `python3` for the bundled stream parser
- `git` for Review and Challenge modes

## Files

- `SKILL.md` - Main skill definition and workflow
- `scripts/parse-stream.py` - Streams `--output-format streaming-messages-json` output (thinking traces, tool calls, token totals, failure events)
- `scripts/run-with-timeout.py` - Portable `timeout` replacement (GNU/macOS/BSD, exit 124, no coreutils needed)
- `scripts/*_test.py` - Self-checks: `python3 <name>_test.py`

## Acknowledgments

Design modeled on the `/codex` skill from [gstack](https://github.com/garrytan/gstack) by Garry Tan; built standalone against grok CLI 0.2.118.
