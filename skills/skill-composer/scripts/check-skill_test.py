#!/usr/bin/env python3
"""Black-box tests for check-skill.py."""

from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


sys.dont_write_bytecode = True
SCRIPT = Path(__file__).with_name("check-skill.py")
FRONTMATTER = '---\nname: demo\ndescription: "Use when testing the checker."\n---\n'


def run(skill_dir):
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(skill_dir)],
        capture_output=True,
        text=True,
        check=False,
    )


class CheckSkillTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skill = self.root / "demo"
        self.skill.mkdir()

    def write(self, relative, text):
        path = self.skill / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(textwrap.dedent(text), encoding="utf-8")
        return path

    def write_skill(self, body="# Demo\n", frontmatter=FRONTMATTER):
        return self.write("SKILL.md", frontmatter + body)

    def assert_passes(self):
        result = run(self.skill)
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("OK demo", result.stdout)
        return result

    def assert_fails(self, rule, detail):
        result = run(self.skill)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        lines = [line for line in result.stdout.splitlines() if line.startswith("FAIL ")]
        matching = [line for line in lines if line.startswith(f"FAIL {rule}:")]
        self.assertTrue(matching, result.stdout)
        self.assertTrue(any(detail in line for line in matching), result.stdout)
        return result

    def test_a_minimal_valid_skill_passes(self):
        self.write_skill()
        self.assert_passes()

    def test_entry_point_byte_cap_is_inclusive(self):
        skill = self.write_skill()
        padding = 15000 - len(skill.read_bytes())
        self.write_skill("# Demo\n" + "x" * padding)
        self.assertEqual(15000, len(skill.read_bytes()))
        self.assert_passes()

        self.write_skill("# Demo\n" + "x" * (padding + 1))
        self.assert_fails("entry-point-size", "15001 bytes")

    def test_entry_point_size_counts_utf8_bytes(self):
        skill = self.write_skill()
        characters = (15000 - len(skill.read_bytes())) // 3 + 1
        self.write_skill("# Demo\n" + "字" * characters)
        self.assert_fails("entry-point-size", "bytes")

    def test_missing_entry_point_is_a_failure(self):
        self.write("README.md", "# Demo\n")
        self.assert_fails("entry-point", "SKILL.md")

    def test_frontmatter_must_open_the_file(self):
        self.write_skill(frontmatter="")
        self.assert_fails("frontmatter", "must start with ---")

    def test_name_must_match_the_directory(self):
        self.write_skill(frontmatter='---\nname: other\ndescription: "x"\n---\n')
        self.assert_fails("frontmatter", "does not match directory 'demo'")

    def test_name_must_be_lowercase_hyphenated(self):
        bad = self.root / "Bad_Name"
        bad.mkdir()
        bad.joinpath("SKILL.md").write_text(
            '---\nname: Bad_Name\ndescription: "x"\n---\n', encoding="utf-8"
        )
        result = run(bad)
        self.assertEqual(1, result.returncode, result.stdout)
        self.assertIn("FAIL frontmatter: name 'Bad_Name'", result.stdout)

    def test_description_is_required(self):
        self.write_skill(frontmatter="---\nname: demo\n---\n")
        self.assert_fails("frontmatter", "description is missing")

    def test_folded_and_plain_multiline_descriptions_are_accepted(self):
        self.write_skill(
            frontmatter=(
                "---\nname: demo\ndescription: >\n  Use when folding\n"
                "  a long description.\nmetadata:\n  internal: true\n---\n"
            )
        )
        self.assert_passes()
        self.write_skill(
            frontmatter="---\nname: demo\ndescription: Use when a plain\n  value wraps.\n---\n"
        )
        self.assert_passes()

    def test_description_over_1024_characters_fails(self):
        self.write_skill(frontmatter=f"---\nname: demo\ndescription: {'d' * 1025}\n---\n")
        self.assert_fails("frontmatter", "1025 characters")

    def test_broken_and_escaping_local_links_fail(self):
        self.write_skill("Read [missing](references/missing.md).\n")
        self.assert_fails("local-links", "references/missing.md")

        self.root.joinpath("outside.md").write_text("# Out\n", encoding="utf-8")
        self.write_skill("Read [out](../outside.md).\n")
        self.assert_fails("local-links", "outside the skill")

    def test_links_to_missing_anchors_fail(self):
        self.write_skill("See [later](#later).\n")
        self.assert_fails("local-links", "#later")

    def test_urls_and_code_are_not_links(self):
        self.write_skill(
            """\
            # Demo

            See [docs](https://example.com/a.md#b) and `[x](missing.md)`.

            ```markdown
            [example](references/not-here.md#section)
            ```
            """
        )
        self.assert_passes()

    def test_reference_pointers_target_whole_files(self):
        self.write("references/guide.md", "# Guide\n\n## Part\n")
        self.write_skill("Read [guide](references/guide.md#part) in full.\n")
        result = self.assert_fails("whole-file-pointers", "references/guide.md#part")
        self.assertIn("or split the reference", result.stdout)

    def test_anchors_into_skill_md_and_the_same_file_are_allowed(self):
        self.write("references/guide.md", "Back to [the router](../SKILL.md#route).\n")
        self.write_skill(
            "# Demo\n\n## Route\n\nRead [guide](references/guide.md). See [route](#route).\n"
        )
        self.assert_passes()

    def test_links_to_another_skill_entry_point_fail(self):
        other = self.root / "other"
        other.mkdir()
        other.joinpath("SKILL.md").write_text(
            '---\nname: other\ndescription: "x"\n---\n', encoding="utf-8"
        )
        self.write_skill("Follow [other](../other/SKILL.md).\n")
        result = self.assert_fails("cross-skill-links", "../other/SKILL.md")
        self.assertIn("invoke", result.stdout)

    def test_urls_to_another_skill_entry_point_fail(self):
        self.write_skill(
            "Follow [other](https://github.com/o/r/blob/main/skills/other/SKILL.md#x).\n"
        )
        result = self.assert_fails("cross-skill-links", "skills/other/SKILL.md")
        self.assertIn("invoke", result.stdout)

    def test_references_must_be_reachable_from_the_entry_point(self):
        self.write("references/guide.md", "# Guide\n\nThen read [deep](deep.md).\n")
        self.write("references/deep.md", "# Deep\n")
        self.write("references/orphan.md", "# Orphan\n")
        self.write("README.md", "See [orphan](references/orphan.md).\n")
        self.write_skill("Read [guide](references/guide.md) in full.\n")
        result = self.assert_fails("reachable-references", "references/orphan.md")
        self.assertNotIn("deep.md", result.stdout)
        self.assertNotIn("README.md", result.stdout)

        self.write_skill(
            "Read [guide](references/guide.md) and [orphan](references/orphan.md).\n"
        )
        self.assert_passes()

    def test_code_span_file_paths_and_directory_links_reach_references(self):
        self.write("references/guide.md", "Then read `references/deep.md`.\n")
        self.write("references/deep.md", "# Deep\n")
        self.write("references/example/README.md", "# Example\n")
        self.write("references/example/part.md", "# Part\n")
        self.write("references/loose.md", "# Loose\n")
        self.write_skill(
            "Read `references/guide.md` in full. Copy [the example](references/example/).\n"
            "Lookup material lives in `references/`.\n"
        )
        result = self.assert_fails("reachable-references", "references/loose.md")
        for reached in ("guide.md", "deep.md", "example/"):
            self.assertNotIn(reached, result.stdout)

    def test_cross_skill_urls_in_files_the_agent_never_reads_pass(self):
        self.write(
            "README.md",
            "Adapted from [upstream](https://github.com/o/r/blob/main/skills/demo/SKILL.md).\n",
        )
        self.write_skill()
        self.assert_passes()

        self.write_skill("See [the README](README.md).\n")
        self.assert_fails("cross-skill-links", "README.md -> https://github.com/o/r")

    def test_a_relative_cross_skill_link_in_an_unread_file_still_escapes_the_skill(self):
        self.write("README.md", "See [other](../other/SKILL.md).\n")
        self.write_skill()
        result = self.assert_fails("local-links", "README.md -> ../other/SKILL.md: outside")
        self.assertNotIn("cross-skill-links", result.stdout)

    def test_a_maintainer_spec_needs_a_pointer_from_the_entry_point(self):
        self.write("SPEC.md", "# Spec\n")
        self.write_skill()
        self.assert_fails("spec-pointer", "SPEC.md")

        self.write_skill("When modifying this skill, read [SPEC.md](SPEC.md) in full.\n")
        self.assert_passes()

    def test_nested_entry_points_fail(self):
        self.write_skill()
        self.write("evals/fixtures/sample/SKILL.md", FRONTMATTER)
        self.assert_fails("nested-entry-points", "evals/fixtures/sample/SKILL.md")

    def test_every_finding_is_reported_in_one_run(self):
        self.write_skill(
            "x" * 15000 + "\n[missing](nope.md)\n",
            frontmatter="---\nname: other\ndescription: x\n---\n",
        )
        result = run(self.skill)
        self.assertEqual(1, result.returncode)
        for rule in ("entry-point-size", "frontmatter", "local-links"):
            self.assertIn(f"FAIL {rule}:", result.stdout)
        self.assertIn("FAIL demo: 3 findings", result.stdout)

    def test_a_missing_directory_is_a_usage_error(self):
        result = run(self.root / "absent")
        self.assertEqual(2, result.returncode)
        self.assertIn("not a directory", result.stderr)


if __name__ == "__main__":
    unittest.main()
