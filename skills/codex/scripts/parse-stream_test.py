#!/usr/bin/env python3
"""Self-check for parse-stream.py. Run: python3 parse-stream_test.py"""
import json
import os
import subprocess
import sys

PARSER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parse-stream.py")


def run(events):
    stream = "".join(json.dumps(e) + "\n" for e in events)
    p = subprocess.run(
        [sys.executable, PARSER], input=stream, capture_output=True, text=True
    )
    return p.returncode, p.stdout, p.stderr


def test_failure_events_surface():
    rc, out, err = run(
        [
            {"type": "thread.started", "thread_id": "abc"},
            {"type": "error", "message": "stream disconnected before completion"},
            {"type": "turn.failed", "error": {"message": "usage limit reached"}},
            {"type": "turn.failed", "error": "plain string err"},
        ]
    )
    assert "[codex error] stream disconnected before completion" in out, out
    assert "[codex error] usage limit reached" in out, out
    assert "[codex error] plain string err" in out, out
    assert rc != 0, f"expected non-zero exit, got {rc}"
    assert "mid-stream disconnect" not in err, err


def test_clean_turn_still_parses():
    rc, out, err = run(
        [
            {"type": "thread.started", "thread_id": "abc"},
            {"type": "item.completed", "item": {"type": "reasoning", "text": "deep thought"}},
            {"type": "item.completed", "item": {"type": "agent_message", "text": "hi"}},
            {
                "type": "item.completed",
                "item": {"type": "command_execution", "command": "git diff"},
            },
            {"type": "turn.completed", "usage": {"input_tokens": 3, "output_tokens": 4}},
        ]
    )
    assert out.splitlines() == [
        "SESSION_ID:abc",
        "[codex thinking] deep thought",
        "",
        "hi",
        "[codex ran] git diff",
        "",
        "tokens used: 7",
    ], out
    assert rc == 0, rc
    assert err == "", err


def test_truncated_stream_still_warns():
    rc, out, err = run([{"type": "thread.started", "thread_id": "abc"}])
    assert "mid-stream disconnect" in err, err
    assert rc == 0, rc


def test_junk_and_null_fields_are_skipped():
    stream = "\n".join(
        [
            "not json",
            "[1,2]",
            "null",
            json.dumps({"type": "item.completed", "item": None}),
            json.dumps({"type": "turn.completed", "usage": None}),
        ]
    )
    p = subprocess.run(
        [sys.executable, PARSER], input=stream, capture_output=True, text=True
    )
    assert p.returncode == 0, (p.returncode, p.stdout, p.stderr)
    assert p.stdout == "", p.stdout
    assert "mid-stream disconnect" not in p.stderr, p.stderr


def test_hostile_stream_is_sanitized():
    rc, out, err = run(
        [
            {"type": "thread.started", "thread_id": 'x"; rm -rf ~'},
            {
                "type": "item.completed",
                "item": {"type": "agent_message", "text": "A\x1b[2JB\u202e\u200b\ufeff\x85C"},
            },
            {"type": "turn.completed", "usage": {"input_tokens": 1, "output_tokens": 1}},
        ]
    )
    assert "SESSION_ID:" not in out, out
    for bad in ("\x1b", "\u202e", "\u200b", "\ufeff", "\x85"):
        assert bad not in out, repr(out)
    assert rc == 0, rc


if __name__ == "__main__":
    test_failure_events_surface()
    test_clean_turn_still_parses()
    test_truncated_stream_still_warns()
    test_junk_and_null_fields_are_skipped()
    test_hostile_stream_is_sanitized()
    print("ok")
