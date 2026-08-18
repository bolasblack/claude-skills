#!/usr/bin/env python3
"""Fixture with a deliberate write that contradicts the read-only contract."""

import json
from pathlib import Path
import sys


target = Path(sys.argv[1])
Path("audit.json").write_text(
    json.dumps({"target": str(target.resolve())}) + "\n",
    encoding="utf-8",
)
