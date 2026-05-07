#!/usr/bin/env python3
"""Tests for generate-index.py relationship indexing and reverse references."""

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from simple_yaml import parse_frontmatter


def load_module(name: str, path: Path):
    """Load a Python module from an arbitrary file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


generate_index = load_module("generate_index", SCRIPT_DIR / "generate-index.py")


class TestGenerateIndex(unittest.TestCase):
    """Verify relationship indexing and reverse-reference sync."""

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
        content = (
            f"---\n{frontmatter}\n---\n\n"
            "## Context\n"
            "Test context.\n\n"
            "## Decision\n"
            "Test decision.\n\n"
            "## Consequences\n"
            "Test consequences.\n"
        )
        (self.decisions_dir / filename).write_text(content)

    def test_generate_indexes_include_related_relationships(self):
        self.write_agd(
            "AGD-001_original.md",
            """title: \"Original\"
description: \"Original decision\"""",
        )
        self.write_agd(
            "AGD-002_update.md",
            """title: \"Update\"
description: \"Updates original\"
updates: AGD-001""",
        )
        self.write_agd(
            "AGD-003_obsolete.md",
            """title: \"Obsolete\"
description: \"Obsoletes original\"
obsoletes: AGD-001""",
        )
        self.write_agd(
            "AGD-004_related.md",
            """title: \"Related\"
description: \"Related to original\"
related: AGD-001""",
        )

        generate_index.generate_indexes(self.project_dir)

        relations_index = (self.agents_dir / "INDEX-AGD-RELATIONS.md").read_text()
        self.assertIn("decisions/AGD-002_update.md -(u)-> decisions/AGD-001_original.md", relations_index)
        self.assertIn("decisions/AGD-003_obsolete.md -(o)-> decisions/AGD-001_original.md", relations_index)
        self.assertIn("decisions/AGD-004_related.md -(r)-> decisions/AGD-001_original.md", relations_index)

    def test_related_does_not_create_reverse_frontmatter(self):
        self.write_agd(
            "AGD-001_original.md",
            """title: \"Original\"
description: \"Original decision\"""",
        )
        self.write_agd(
            "AGD-002_update.md",
            """title: \"Update\"
description: \"Updates original\"
updates: AGD-001""",
        )
        self.write_agd(
            "AGD-003_related.md",
            """title: \"Related\"
description: \"Related to original\"
related: AGD-001""",
        )

        generate_index.generate_indexes(self.project_dir)

        original_content = (self.decisions_dir / "AGD-001_original.md").read_text()
        frontmatter, _ = parse_frontmatter(original_content)

        self.assertEqual(frontmatter.get("updated_by"), "AGD-002")
        self.assertNotIn("related", frontmatter)

    def test_managed_reverse_references_are_pruned_to_computed_values(self):
        self.write_agd(
            "AGD-001_original.md",
            """title: \"Original\"
description: \"Original decision\"
updated_by: AGD-999
obsoleted_by: AGD-998""",
        )
        self.write_agd(
            "AGD-002_update.md",
            """title: \"Update\"
description: \"Updates original\"
updates: AGD-001""",
        )

        generate_index.generate_indexes(self.project_dir)

        original_content = (self.decisions_dir / "AGD-001_original.md").read_text()
        frontmatter, _ = parse_frontmatter(original_content)

        self.assertEqual(frontmatter.get("updated_by"), "AGD-002")
        self.assertNotIn("obsoleted_by", frontmatter)

    def test_managed_reverse_references_are_removed_when_no_longer_present(self):
        self.write_agd(
            "AGD-001_original.md",
            """title: \"Original\"
description: \"Original decision\"
updated_by: AGD-002
obsoleted_by: AGD-003""",
        )

        generate_index.generate_indexes(self.project_dir)

        original_content = (self.decisions_dir / "AGD-001_original.md").read_text()
        frontmatter, _ = parse_frontmatter(original_content)

        self.assertNotIn("updated_by", frontmatter)
        self.assertNotIn("obsoleted_by", frontmatter)

    def test_post_generate_index_scripts_run_after_indexes_are_written(self):
        hook_dir = self.agents_dir / "hooks"
        hook_dir.mkdir()
        hook_script = hook_dir / "local-post-generate.py"
        marker_file = self.agents_dir / "post-generate-marker.txt"
        hook_script.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "from pathlib import Path\n"
            "project_dir = Path(sys.argv[1])\n"
            "index_exists = (project_dir / '.agents' / 'INDEX-TAGS.md').exists()\n"
            f"Path({str(marker_file)!r}).write_text(str(index_exists))\n"
        )
        hook_script.chmod(0o755)
        (self.agents_dir / "config.json").write_text(json.dumps({
            "tags": [],
            "postGenerateIndexScripts": ["hooks/local-post-generate.py"],
        }))

        generate_index.generate_indexes(self.project_dir)

        self.assertEqual(marker_file.read_text(), "True")


if __name__ == "__main__":
    unittest.main(verbosity=2)
