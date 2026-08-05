#!/usr/bin/env python3
"""Stream-parse `codex exec --json` JSONL from stdin.

Prints, as they arrive: SESSION_ID:<id> (from thread.started), [codex thinking]
reasoning traces, agent messages, [codex ran] command lines, and total token
usage. Failure events print [codex error] and exit non-zero. Warns on stderr if
the stream ended without a turn.completed event.
"""
import json
import re
import sys

_CTRL = re.compile(
    "[\x00-\x08\x0b-\x1f\x7f-\x9f"
    "\u200b-\u200f\u202a-\u202e\u2060-\u2064\ufeff]"
)


def clean(s):
    """Strip control and invisible characters (ANSI escapes, C1, zero-width, bidi overrides) from untrusted text."""
    return _CTRL.sub("", str(s))


turns = 0
failed = False
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        continue
    if not isinstance(obj, dict):
        continue
    t = obj.get("type", "")
    if t == "thread.started":
        tid = obj.get("thread_id", "")
        if tid and re.fullmatch(r"[A-Za-z0-9._-]{1,128}", str(tid)):
            print(f"SESSION_ID:{tid}", flush=True)
    elif t == "item.completed":
        item = obj.get("item") or {}
        itype = item.get("type", "")
        text = item.get("text", "")
        if itype == "reasoning" and text:
            print(f"[codex thinking] {clean(text)}\n", flush=True)
        elif itype == "agent_message" and text:
            print(clean(text), flush=True)
        elif itype == "command_execution":
            cmd = item.get("command", "")
            if cmd:
                print(f"[codex ran] {clean(cmd)}", flush=True)
    elif t in ("error", "turn.failed"):
        failed = True
        err = obj.get("error")
        msg = obj.get("message") or (err.get("message") if isinstance(err, dict) else err)
        print(f"[codex error] {clean(msg or line)}", flush=True)
    elif t == "turn.completed":
        turns += 1
        usage = obj.get("usage") or {}
        tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        if tokens:
            print(f"\ntokens used: {tokens}", flush=True)

if failed:
    sys.exit(1)
if turns == 0:
    print(
        "[codex warning] no turn.completed event received — possible mid-stream disconnect",
        file=sys.stderr,
    )
