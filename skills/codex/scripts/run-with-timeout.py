#!/usr/bin/env python3
"""Portable `timeout` replacement: run-with-timeout.py SECONDS CMD [ARG...]

Works identically on GNU, macOS, and BSD with no extra installs (python3 is
already a dependency of this skill). Runs CMD in its own process group,
passing stdin/stdout/stderr straight through. On expiry sends SIGTERM to the
group, escalates to SIGKILL after 10s, and exits 124 (GNU timeout's code).
Otherwise exits with CMD's own code; 127 if CMD is not found.
"""
import os
import signal
import subprocess
import sys


def main():
    if len(sys.argv) < 3:
        print("usage: run-with-timeout.py SECONDS CMD [ARG...]", file=sys.stderr)
        return 2
    try:
        seconds = float(sys.argv[1])
    except ValueError:
        print(f"run-with-timeout: bad SECONDS value: {sys.argv[1]!r}", file=sys.stderr)
        return 2
    try:
        proc = subprocess.Popen(sys.argv[2:], start_new_session=True)
    except FileNotFoundError:
        print(f"run-with-timeout: command not found: {sys.argv[2]}", file=sys.stderr)
        return 127
    try:
        rc = proc.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        for sig, grace in ((signal.SIGTERM, 10), (signal.SIGKILL, None)):
            try:
                os.killpg(proc.pid, sig)
            except ProcessLookupError:
                break
            try:
                proc.wait(timeout=grace)
                break
            except subprocess.TimeoutExpired:
                continue
        return 124
    return 128 - rc if rc < 0 else rc


if __name__ == "__main__":
    sys.exit(main())
