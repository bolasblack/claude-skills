#!/usr/bin/env python3
"""Package-contract tests for Skill Composer."""

import json
from pathlib import Path
import re
import unittest
from urllib.parse import unquote


PACKAGE = Path(__file__).parent


def markdown_anchors(text):
    """Return GitHub-style heading anchors for the Markdown used in this package."""
    anchors = set()
    duplicates = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*$", text, flags=re.MULTILINE):
        heading = re.sub(r"`([^`]*)`", r"\1", heading)
        heading = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", heading)
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        duplicate = duplicates.get(slug, 0)
        duplicates[slug] = duplicate + 1
        anchors.add(slug if duplicate == 0 else f"{slug}-{duplicate}")
    return anchors


class SkillComposerPackageTest(unittest.TestCase):
    def test_skill_frontmatter_is_portable_and_matches_its_directory(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(skill.startswith("---\n"))
        frontmatter = skill.split("---\n", 2)[1]
        fields = {}
        for line in frontmatter.splitlines():
            match = re.fullmatch(r"([a-z][a-z0-9-]*):\s*(.+)", line)
            self.assertIsNotNone(match, f"unsupported frontmatter line: {line}")
            key, raw_value = match.groups()
            fields[key] = json.loads(raw_value) if raw_value.startswith('"') else raw_value

        self.assertEqual({"name", "description", "license"}, set(fields))
        self.assertEqual(PACKAGE.name, fields["name"])
        self.assertRegex(fields["name"], r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
        self.assertLessEqual(len(fields["name"]), 64)
        self.assertGreaterEqual(len(fields["description"]), 1)
        self.assertLessEqual(len(fields["description"]), 1024)
        self.assertEqual("LICENSE.md", fields["license"])
        self.assertEqual(
            "# License\n\nPersonal use.\n",
            PACKAGE.joinpath(fields["license"]).read_text(encoding="utf-8"),
        )

    def test_research_and_automation_contracts_are_reachable(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        spec = PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8")
        readme = PACKAGE.joinpath("README.md").read_text(encoding="utf-8")
        research = PACKAGE.joinpath("HARNESS-RESEARCH.md")

        self.assertIn("environment-native automation", skill.lower())
        self.assertIn("environment-native automation", spec.lower())
        self.assertIn("[HARNESS-RESEARCH.md](HARNESS-RESEARCH.md)", skill)
        self.assertIn("[HARNESS-RESEARCH.md](HARNESS-RESEARCH.md)", readme)
        self.assertTrue(research.is_file())
        self.assertIn(
            "[scripts/fetch-harness-docs.py](scripts/fetch-harness-docs.py)",
            research.read_text(encoding="utf-8"),
        )
        research_text = research.read_text(encoding="utf-8")
        self.assertIn("--proxy", research_text)
        self.assertIn("--ca-file", research_text)
        self.assertIn("transport-trust selection", research_text)
        self.assertIn("residual output may remain", research_text)
        self.assertIn("reviewed identity preamble", research_text)
        self.assertRegex(
            research_text, r"retrieval-phase wall-clock\s+deadline"
        )
        self.assertNotIn("command wall-clock", research_text)
        self.assertIn("TLS certificate verification failures are `trust`", research_text)
        self.assertIn("write-failure cleanup check", readme)

    def test_spec_invariants_own_their_reasons_without_a_second_ledger(self):
        spec = PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8")
        reference = PACKAGE.joinpath("REFERENCE.md").read_text(encoding="utf-8")
        sections = re.findall(
            r"^## ([^\n]+)\n(.*?)(?=^## |\Z)",
            spec,
            flags=re.MULTILINE | re.DOTALL,
        )

        self.assertGreater(len(sections), 0)
        for heading, body in sections:
            self.assertIn("**Why:**", body, heading)
        self.assertNotIn("### Skill Composer Admission Ledger", reference)

    def test_every_instruction_step_has_a_local_completion_criterion(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        fenced_blocks = re.findall(
            r"^```[^\n]*\n(.*?)^```$",
            skill,
            flags=re.MULTILINE | re.DOTALL,
        )
        runtime = re.sub(
            r"^```[^\n]*\n.*?^```$",
            "",
            skill,
            flags=re.MULTILINE | re.DOTALL,
        )
        runtime_steps = re.findall(
            r"^### ((?:(?:Review|Release) )?Step \d+:[^\n]+)\n"
            r"(.*?)(?=^#{2,3} |\Z)",
            runtime,
            flags=re.MULTILINE | re.DOTALL,
        )
        example_steps = []
        for block in fenced_blocks:
            example_steps.extend(
                re.findall(
                    r"^### (Step \d+:[^\n]+)\n(.*?)(?=^#{2,3} |\Z)",
                    block,
                    flags=re.MULTILINE | re.DOTALL,
                )
            )

        self.assertGreaterEqual(len(runtime_steps), 18)
        self.assertGreaterEqual(len(example_steps), 4)
        for heading, body in runtime_steps + example_steps:
            self.assertIn("**Done when:**", body, heading)

    def test_contract_lock_steps_finish_with_every_declared_input(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        research = PACKAGE.joinpath("HARNESS-RESEARCH.md").read_text(
            encoding="utf-8"
        )

        checks = {
            "Review Step 1: Lock the Contract": (
                skill,
                (
                    "review scope",
                    "repository rules",
                    "allowed mutations",
                    "target harness and surface",
                    "invocation policy",
                    "distribution form",
                    "reconstructed job",
                    "branch",
                    "output",
                    "side effect",
                    "completion criterion",
                ),
            ),
            "Release Step 1: Lock the Release Contract": (
                skill,
                (
                    "exact skill",
                    "proposed version",
                    "target harnesses and surfaces",
                    "invocation policies",
                    "distribution forms",
                    "artifact files",
                    "claimed gate",
                ),
            ),
            "Step 1: Lock the Question": (
                research,
                (
                    "target harness and surface",
                    "invocation and distribution mode",
                    "version",
                    "claim or question",
                    "portable disposition",
                ),
            ),
        }
        for heading, (document, expected) in checks.items():
            section = document.split(f"### {heading}\n", 1)[1].split(
                "\n### ", 1
            )[0]
            done = section.split("**Done when:**", 1)[1].lower()
            for phrase in expected:
                self.assertIn(phrase, done, heading)

    def test_lookup_rules_have_one_owner(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        reference = PACKAGE.joinpath("REFERENCE.md").read_text(encoding="utf-8")

        for duplicate in (
            "**Portable required fields**",
            "your-skill-name/",
            "## Quick Checklist",
            "### Pattern 1: Sequential Orchestration",
        ):
            self.assertNotIn(duplicate, skill)
        self.assertNotIn("### Pattern 1: Sequential Orchestration", reference)
        self.assertNotIn("**Portable core:**", reference)
        self.assertIn("## YAML Frontmatter Specification", reference)
        self.assertIn("## Directory Structure Patterns", reference)
        self.assertIn("## Workflow Patterns", reference)
        self.assertIn("exactly `SKILL.md`", reference)
        self.assertIn("parent directory", reference)

    def test_invocation_and_evaluation_boundaries_are_decision_complete(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        reference = PACKAGE.joinpath("REFERENCE.md").read_text(encoding="utf-8")
        for phrase in (
            "context load",
            "cognitive load",
            "not a third",
            "explicit user authorization",
            "disposable fixture",
        ):
            self.assertIn(phrase, skill.lower())
        self.assertNotIn("## Invocation Modes", reference)

    def test_unreleased_history_records_net_changes_only(self):
        changelog = PACKAGE.joinpath("CHANGELOG.md").read_text(encoding="utf-8")

        self.assertIn("## [Unreleased]", changelog)
        for residue in (
            "### Make transport trust explicit",
            "### State publication cleanup limits honestly",
            "harness-document",
            "Replace `HTTPS_PROXY`",
            "Remove links to `examples/*.md`",
        ):
            self.assertNotIn(residue, changelog)

    def test_local_markdown_links_and_anchors_resolve(self):
        failures = []
        for document in PACKAGE.rglob("*.md"):
            text = document.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", text):
                path, separator, fragment = target.partition("#")
                if not path or "://" in path or path.startswith("mailto:"):
                    target_document = document if not path else None
                else:
                    target_document = document.parent.joinpath(path).resolve()
                if target_document is None:
                    continue
                try:
                    target_document.relative_to(PACKAGE.resolve())
                except ValueError:
                    failures.append(
                        f"{document.relative_to(PACKAGE)} -> {target} "
                        "(outside package)"
                    )
                    continue
                if not target_document.exists():
                    failures.append(f"{document.relative_to(PACKAGE)} -> {target}")
                    continue
                if separator and target_document.suffix.lower() == ".md":
                    anchors = markdown_anchors(
                        target_document.read_text(encoding="utf-8")
                    )
                    if unquote(fragment).lower() not in anchors:
                        failures.append(
                            f"{document.relative_to(PACKAGE)} -> {target} "
                            "(missing anchor)"
                        )

        self.assertEqual([], failures)

    def test_all_declared_authoring_workflows_have_runtime_routes(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        frontmatter = skill.split("---\n", 2)[1].lower()
        router = skill.split("## Choose the Workflow\n", 1)[1].split(
            "\n## Planning Before Creating or Updating", 1
        )[0]

        expected_routes = {
            "Create": "#creating-or-updating-a-skill",
            "Update": "#planning-before-creating-or-updating",
            "Review": "#reviewing-an-existing-skill",
            "Package or release": "#packaging-and-releasing-a-skill",
        }
        for operation in ("creating", "updating", "reviewing", "packaging"):
            self.assertIn(operation, frontmatter)
        for label, anchor in expected_routes.items():
            route = re.search(
                rf"^- \*\*{re.escape(label)}:\*\* (.+)$",
                router,
                flags=re.MULTILINE,
            )
            self.assertIsNotNone(route, f"missing {label} workflow route")
            self.assertIn(anchor, route.group(1))
        self.assertIn("## Packaging and Releasing a Skill", skill)
        self.assertIn("clean instance", skill)
        self.assertIn("portable fallback", skill)
        self.assertIn("isolation", skill)
        self.assertIn("coexistence", skill)

    def test_dynamic_harness_facts_have_one_research_owner(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        reference = PACKAGE.joinpath("REFERENCE.md").read_text(encoding="utf-8")
        research = PACKAGE.joinpath("HARNESS-RESEARCH.md").read_text(encoding="utf-8")
        distribution = reference.split("## Distribution\n", 1)[1].split(
            "\n## Portable Changelog Format", 1
        )[0]

        self.assertIn("[HARNESS-RESEARCH.md](HARNESS-RESEARCH.md)", skill)
        self.assertIn("[HARNESS-RESEARCH.md](HARNESS-RESEARCH.md)", reference)
        for decision in (
            "Scope",
            "Delivery",
            "Discovery and invocation",
            "Update lifecycle",
            "Validation",
        ):
            self.assertIn(decision, distribution)
        self.assertIn("Exact current paths, commands, UI steps", research)

        current_guidance = skill + reference
        for cached_fact in (
            ".claude/skills/",
            ".agents/skills/",
            ".grok/skills/",
            "Customize > Skills",
            "container.skills",
            "claude --debug",
            "skills-ref validate",
            "disable-model-invocation",
            "user-invocable",
        ):
            self.assertNotIn(cached_fact, current_guidance)
        self.assertNotRegex(
            current_guidance,
            re.compile(r'^Error: "[^"\n]+"$', flags=re.MULTILINE),
        )

    def test_removed_examples_have_no_current_package_residue(self):
        examples = PACKAGE.joinpath("examples")
        self.assertFalse(examples.exists() and any(examples.iterdir()))
        for name in (
            "SKILL.md",
            "README.md",
            "REFERENCE.md",
            "SPEC.md",
            "HARNESS-RESEARCH.md",
        ):
            text = PACKAGE.joinpath(name).read_text(encoding="utf-8").lower()
            self.assertNotIn("examples/", text, name)
            self.assertNotIn("historical pattern snapshot", text, name)

    def test_release_documentation_keeps_behavior_gates_visible(self):
        readme = PACKAGE.joinpath("README.md").read_text(encoding="utf-8")
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")

        self.assertIn("necessary, not sufficient", readme)
        for workflow in ("Create", "Update", "Review", "Package/release"):
            self.assertIn(f"| {workflow} |", readme)
        for gate in (
            "fresh-context activation",
            "portable fallback",
            "isolation and coexistence",
            "clean installation",
            "`unknown`",
        ):
            self.assertIn(gate, readme)
        self.assertIn(
            "candidate validation has a result for every locked pre-install gate",
            skill,
        )
        self.assertIn("versioned final artifact itself", skill)


if __name__ == "__main__":
    unittest.main(verbosity=2)
