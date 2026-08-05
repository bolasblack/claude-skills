# Codex — Second Opinion (OpenAI Codex)

Get an independent second opinion from OpenAI Codex via the `codex` CLI — a different AI system reviewing with fresh eyes and no stake in the plan.

## Modes

- **Review** (`/codex review [focus]`) — independent diff review against the base branch with a `[P1]`/`[P2]` pass/fail gate
- **Challenge** (`/codex challenge [focus]`) — adversarial pass that hunts for edge cases, race conditions, security holes, and failure modes
- **Consult** (`/codex <question>`) — ask Codex anything, with session continuity for follow-ups

Every call runs Codex read-only, presents its output verbatim, and closes with a one-line actionable recommendation. When Claude reviewed the same changes, a cross-model comparison is appended. Defaults to `gpt-5.6-sol` at `ultra` reasoning effort; naming a model or effort overrides it.

## Requirements

- OpenAI Codex CLI (`npm install -g @openai/codex`), authenticated via `codex login` or `OPENAI_API_KEY`/`CODEX_API_KEY`
- `python3` for the bundled JSONL stream parser
- `git` for Review and Challenge modes

## Files

- `SKILL.md` - Main skill definition and workflow
- `scripts/parse-stream.py` - Streams `codex exec --json` output (thinking traces, tool calls, session id, token totals, failure events)
- `scripts/run-with-timeout.py` - Portable `timeout` replacement (GNU/macOS/BSD, exit 124, no coreutils needed)
- `scripts/*_test.py` - Self-checks: `python3 <name>_test.py`

## Acknowledgments

Ported from the `/codex` skill in [gstack](https://github.com/garrytan/gstack) by Garry Tan, rebuilt standalone (no gstack runtime required) and re-grounded against codex-cli 0.146.0.
