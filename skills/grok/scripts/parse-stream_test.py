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


def test_clean_turn_parses():
    rc, out, err = run(
        [
            {"type": "system", "subtype": "init", "session_id": "abc", "model": "grok-4.5"},
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "thinking", "thinking": "deep thought", "signature": "x"},
                        {
                            "type": "tool_use",
                            "id": "call-1",
                            "name": "run_terminal_command",
                            "input": {"command": "git log --oneline -1"},
                        },
                    ],
                    "usage": {"input_tokens": 1, "output_tokens": 2},
                },
            },
            {
                "type": "user",
                "message": {
                    "role": "user",
                    "content": [
                        {"type": "tool_result", "tool_use_id": "call-1", "content": "…", "is_error": False}
                    ],
                },
            },
            {
                "type": "assistant",
                "message": {
                    "role": "assistant",
                    "content": [{"type": "text", "text": "hi"}],
                    "usage": {"input_tokens": 1, "output_tokens": 2},
                },
            },
            {
                "type": "result",
                "subtype": "success",
                "is_error": False,
                "result": "hi",
                "usage": {"input_tokens": 3, "output_tokens": 4},
            },
        ]
    )
    assert out.splitlines() == [
        "[grok thinking] deep thought",
        "",
        "[grok ran] git log --oneline -1",
        "hi",
        "",
        "tokens used: 7",
    ], out
    assert rc == 0, rc
    assert err == "", err


def test_error_result_surfaces():
    rc, out, err = run(
        [
            {"type": "system", "subtype": "init", "session_id": "abc"},
            {"type": "result", "subtype": "error_during_execution", "is_error": True, "result": "boom"},
        ]
    )
    assert "[grok error] boom" in out, out
    assert rc != 0, f"expected non-zero exit, got {rc}"
    assert "mid-stream disconnect" not in err, err


def test_truncated_stream_still_warns():
    rc, out, err = run([{"type": "system", "subtype": "init", "session_id": "abc"}])
    assert "mid-stream disconnect" in err, err
    assert rc == 0, rc


def test_junk_and_null_fields_are_skipped():
    stream = "\n".join(
        [
            "not json",
            "[1,2]",
            "null",
            json.dumps({"type": "assistant", "message": None}),
            json.dumps({"type": "assistant", "message": {"content": None}}),
            json.dumps({"type": "result", "subtype": "success", "is_error": False, "usage": None}),
        ]
    )
    p = subprocess.run(
        [sys.executable, PARSER], input=stream, capture_output=True, text=True
    )
    assert p.returncode == 0, (p.returncode, p.stdout, p.stderr)
    assert p.stdout == "", p.stdout
    assert "mid-stream disconnect" not in p.stderr, p.stderr


def test_output_is_sanitized():
    rc, out, err = run(
        [
            {
                "type": "assistant",
                "message": {"role": "assistant", "content": [{"type": "text", "text": "A\x1b[2JB\u202e\u200b\ufeff\x85C"}]},
            },
            {"type": "result", "subtype": "success", "is_error": False, "usage": {"input_tokens": 1, "output_tokens": 1}},
        ]
    )
    for bad in ("\x1b", "\u202e", "\u200b", "\ufeff", "\x85"):
        assert bad not in out, repr(out)
    assert rc == 0, rc


if __name__ == "__main__":
    test_clean_turn_parses()
    test_error_result_surfaces()
    test_truncated_stream_still_warns()
    test_junk_and_null_fields_are_skipped()
    test_output_is_sanitized()
    print("ok")
