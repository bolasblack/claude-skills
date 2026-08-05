#!/usr/bin/env python3
"""Self-check for run-with-timeout.py. Run: python3 run-with-timeout_test.py"""
import os
import subprocess
import sys
import time

WRAPPER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "run-with-timeout.py"
)


def run(*args, **kw):
    return subprocess.run([sys.executable, WRAPPER, *args], capture_output=True, text=True, **kw)


def test_passes_through_exit_code():
    p = run("5", "sh", "-c", "exit 7")
    assert p.returncode == 7, p.returncode


def test_passes_through_stdout():
    p = run("5", "echo", "hi")
    assert p.stdout == "hi\n", repr(p.stdout)
    assert p.returncode == 0, p.returncode


def test_timeout_exits_124_promptly():
    start = time.monotonic()
    p = run("1", "sleep", "30")
    elapsed = time.monotonic() - start
    assert p.returncode == 124, (p.returncode, p.stderr)
    assert elapsed < 10, f"took {elapsed:.1f}s — child not killed promptly"


def test_missing_command_exits_127():
    p = run("5", "definitely-not-a-real-command-xyz")
    assert p.returncode == 127, (p.returncode, p.stderr)


if __name__ == "__main__":
    test_passes_through_exit_code()
    test_passes_through_stdout()
    test_timeout_exits_124_promptly()
    test_missing_command_exits_127()
    print("ok")
