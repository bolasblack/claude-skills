#!/usr/bin/env python3
"""Tests for validate-agds.py AGD reference validation."""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


def load_module(name: str, path: Path):
    """Load a Python module from an arbitrary file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validate_agds = load_module("validate_agds", SCRIPT_DIR / "validate-agds.py")


class TestValidateAgds(unittest.TestCase):
    """Verify AGD reference validation includes related references."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.project_dir = Path(self.temp_dir.name)
        self.agents_dir = self.project_dir / ".agents"
        self.decisions_dir = self.agents_dir / "decisions"
        self.scripts_dir = self.agents_dir / "scripts"
        self.decisions_dir.mkdir(parents=True)
        self.scripts_dir.mkdir(parents=True)
        (self.agents_dir / "config.json").write_text(json.dumps({"tags": []}))

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_agd(self, filename: str, frontmatter: str) -> None:
        content = f"---\n{frontmatter}\n---\n\n## Context\nTest context.\n"
        (self.decisions_dir / filename).write_text(content)

    def test_related_reference_must_exist(self):
        self.write_agd(
            "AGD-001_related.md",
            """title: \"Related\"
description: \"References a missing decision\"
related: AGD-999""",
        )

        errors = validate_agds.validate_all_decisions(self.project_dir)

        self.assertIn(
            "AGD-001_related.md: related references non-existent AGD-999",
            errors,
        )

    def test_auto_managed_reverse_references_are_not_validated(self):
        self.write_agd(
            "AGD-001_original.md",
            """title: \"Original\"
description: \"Original decision\"
updated_by: definitely-not-an-agd
obsoleted_by: AGD-999""",
        )

        errors = validate_agds.validate_all_decisions(self.project_dir)

        self.assertEqual(errors, [])

    def test_post_validate_agds_scripts_run_after_validation(self):
        hook_dir = self.agents_dir / "hooks"
        hook_dir.mkdir()
        hook_script = hook_dir / "local-post-validate.py"
        marker_file = self.agents_dir / "post-validate-marker.txt"
        hook_script.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "from pathlib import Path\n"
            "project_dir = Path(sys.argv[1])\n"
            f"Path({str(marker_file)!r}).write_text(str(project_dir))\n"
        )
        hook_script.chmod(0o755)
        (self.agents_dir / "config.json").write_text(json.dumps({
            "tags": [],
            "postValidateAgdsScripts": ["hooks/local-post-validate.py"],
        }))

        validate_agds.run_post_validate_scripts(self.project_dir)

        self.assertEqual(marker_file.read_text(), str(self.project_dir))


if __name__ == "__main__":
    unittest.main(verbosity=2)
