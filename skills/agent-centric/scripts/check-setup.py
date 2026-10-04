#!/usr/bin/env python3
"""Check Agent Centric setup without modifying the project or running its scripts.

Managed by: agent-centric skill
DO NOT MODIFY THIS FILE - it will be automatically updated from the skill directory.
To disable auto-update, add this filename to disableAutoUpdateScripts in config.json.

Usage: python3 check-setup.py <project_dir>
Exit codes: 0 = ready, 1 = missing or invalid setup, 2 = invalid arguments.
"""

import argparse
import json
import os
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_dir", help="Target project root (checked as-is)")
    args = parser.parse_args()
    if not args.project_dir:
        parser.error("project_dir must not be empty")

    agents_dir = Path(args.project_dir) / ".agents"
    problems = []
    config_path = agents_dir / "config.json"
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
        if not isinstance(config, dict) or not isinstance(config.get("tags"), list):
            problems.append(f"{config_path}: expected an object with a tags array")
        elif not all(isinstance(tag, str) for tag in config["tags"]):
            problems.append(f"{config_path}: tags must contain only strings")
    except (OSError, ValueError) as error:
        problems.append(f"{config_path}: {error}")

    for name in ("decisions", "scripts"):
        path = agents_dir / name
        if not path.is_dir():
            problems.append(f"{path}: missing directory")

    for name in ("validate-agds.py", "generate-index.py", "utils.py", "simple_yaml.py"):
        path = agents_dir / "scripts" / name
        if not path.is_file() or not os.access(path, os.R_OK):
            problems.append(f"{path}: missing or unreadable script")
        elif name in ("validate-agds.py", "generate-index.py") and not os.access(path, os.X_OK):
            problems.append(f"{path}: script is not executable")

    if problems:
        print("agent-centric setup is missing or incomplete; stop using this skill.", file=sys.stderr)
        for problem in problems:
            print(f"  - {problem}", file=sys.stderr)
        return 1

    print("agent-centric setup is ready.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
