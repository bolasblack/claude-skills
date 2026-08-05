#!/usr/bin/env python3
"""Stream-parse `grok --output-format streaming-messages-json` NDJSON from stdin.

Prints, as they arrive: [grok thinking] reasoning traces, assistant message
text, [grok ran] tool-call lines, and total token usage from the final result
event. A failed result prints [grok error] and exits non-zero. Warns on stderr
if the stream ended without a result event.
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


done = False
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
    if t == "assistant":
        for block in (obj.get("message") or {}).get("content") or []:
            btype = block.get("type", "")
            if btype == "thinking" and block.get("thinking"):
                print(f"[grok thinking] {clean(block['thinking'])}\n", flush=True)
            elif btype == "text" and block.get("text"):
                print(clean(block["text"]), flush=True)
            elif btype == "tool_use":
                cmd = (block.get("input") or {}).get("command") or block.get("name", "")
                if cmd:
                    print(f"[grok ran] {clean(cmd)}", flush=True)
    elif t == "result":
        done = True
        if obj.get("is_error") or obj.get("subtype") != "success":
            failed = True
            print(f"[grok error] {clean(obj.get('result') or obj.get('subtype') or line)}", flush=True)
        usage = obj.get("usage") or {}
        tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        if tokens:
            print(f"\ntokens used: {tokens}", flush=True)

if failed:
    sys.exit(1)
if not done:
    print(
        "[grok warning] no result event received — possible mid-stream disconnect",
        file=sys.stderr,
    )
