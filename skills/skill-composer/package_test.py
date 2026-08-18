#!/usr/bin/env python3
"""Package-contract tests for Skill Composer."""

import json
from pathlib import Path
import re
import subprocess
import sys
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

    def test_authoring_another_skill_does_not_open_maintainer_evidence(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        contract = " ".join(skill.split())

        self.assertIn(
            "Do not inspect them while using Skill Composer to author another skill",
            contract,
        )
        self.assertIn(
            "Do not seek or load it merely because it is installed", contract
        )
        self.assertIn(
            "Never scan home or user-level skill directories for examples, "
            "validators, or target evidence",
            contract,
        )

    def test_packaged_evals_are_opt_in_and_existing_suites_follow_changed_behavior(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        evaluation_step = skill.split("### Step 8:", 1)[1].split("\n## ", 1)[0]
        contract = " ".join(evaluation_step.lower().split())

        for phrase in (
            "user explicitly asks",
            "already contains an eval suite",
            "do not create eval manifests, fixtures, or runner copies",
            "recommend the smallest useful suite",
            "ask the user before adding it",
            "affected existing cases",
        ):
            self.assertIn(phrase, contract)

        manifest = json.loads(
            PACKAGE.joinpath("evals", "evals.json").read_text(encoding="utf-8")
        )
        cases = {case["id"]: case for case in manifest["evals"]}
        assertions = {
            case_id: {item["id"]: item["description"] for item in case["assertions"]}
            for case_id, case in cases.items()
        }
        self.assertIn(
            "keeps-evals-opt-in", assertions["creates-a-portable-skill"]
        )
        self.assertIn(
            "maintains-existing-evals", assertions["updates-repeatable-mechanics"]
        )
        self.assertIn(
            "keeps-evals-opt-in",
            assertions["updates-then-packages-cross-harness"],
        )

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
        for intent in (
            "create a new agent skill",
            "revise an existing skill",
            "audit a complete skill package",
            "prepare and validate its release",
        ):
            self.assertIn(intent, frontmatter)
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
        skill_contract = " ".join(skill.split())
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
        self.assertIn(
            "A portable core that names multiple compatible harnesses remains "
            "portable-only",
            skill_contract,
        )
        self.assertIn(
            "Do not enumerate `PATH`, installation directories, or language "
            "package registries to hunt for validators",
            skill_contract,
        )

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

    def test_validation_ledger_accounts_for_every_applicable_gate(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        evaluation_step = re.search(
            r"^### Step 8:[^\n]+\n(.*?)(?=^## |\Z)",
            skill,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(evaluation_step)
        contract = evaluation_step.group(1).lower()

        for phrase in (
            "validation ledger",
            "every applicable gate",
            "pass`, `fail`, or `unknown",
            "bundled tests",
            "fresh-session behavior",
            "portable fallback",
            "clean installation",
            "final response",
            "overall result is green only",
        ):
            self.assertIn(phrase, contract)

    def test_every_affected_branch_in_an_admitted_suite_has_a_regression_owner(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        evaluation_step = re.search(
            r"^### Step 8:[^\n]+\n(.*?)(?=^## |\Z)",
            skill,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(evaluation_step)
        contract = " ".join(evaluation_step.group(1).lower().split())

        for phrase in (
            "branch-to-case coverage table",
            "normal, edge, stop, failure, and unknown-handling",
            "at least one functional case",
            "before the suite is complete",
        ):
            self.assertIn(phrase, contract)

    def test_validation_ledger_is_derived_from_the_package_inventory(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        evaluation_step = re.search(
            r"^### Step 8:[^\n]+\n(.*?)(?=^## |\Z)",
            skill,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(evaluation_step)
        contract = " ".join(evaluation_step.group(1).lower().split())

        for phrase in (
            "derive its rows from the locked package inventory",
            "every discovered test entry point and executable script",
            "baseline result before editing",
            "retained, replaced, or removed",
            "unrun baseline behavior as `unknown`",
        ):
            self.assertIn(phrase, contract)

    def test_changelog_migrations_require_a_changed_public_contract(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        reference = PACKAGE.joinpath("REFERENCE.md").read_text(encoding="utf-8")

        for document in (skill, reference):
            contract = " ".join(document.lower().split())
            self.assertIn(
                "an internal implementation replacement with unchanged public "
                "invocation, inputs, and outputs has no migration entry",
                contract,
            )

    def test_script_changes_require_observed_public_seam_red_green_evidence(self):
        skill = " ".join(
            PACKAGE.joinpath("SKILL.md")
            .read_text(encoding="utf-8")
            .lower()
            .split()
        )
        reference = " ".join(
            PACKAGE.joinpath("REFERENCE.md")
            .read_text(encoding="utf-8")
            .lower()
            .split()
        )

        expected = (
            "run the public-seam test and preserve its observed failure before "
            "writing the implementation"
        )
        self.assertIn(expected, skill)
        self.assertIn(expected, reference)

    def test_repeatable_eval_infrastructure_is_package_local_and_reachable(self):
        script = PACKAGE / "scripts" / "eval-skill.py"
        script_test = PACKAGE / "scripts" / "eval-skill_test.py"
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        reference = PACKAGE.joinpath("REFERENCE.md").read_text(encoding="utf-8")
        readme = PACKAGE.joinpath("README.md").read_text(encoding="utf-8")

        self.assertTrue(script.is_file())
        self.assertTrue(script_test.is_file())
        self.assertTrue(PACKAGE.joinpath("evals", "evals.json").is_file())
        self.assertTrue(
            PACKAGE.joinpath("evals", "trigger-eval.json").is_file()
        )
        result = subprocess.run(
            [sys.executable, "-B", str(script), "check", str(PACKAGE)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("functional=4 trigger=20", result.stdout)
        self.assertIn(
            "[Repeatable Evaluation Contract]"
            "(REFERENCE.md#repeatable-evaluation-contract)",
            skill,
        )
        self.assertIn("## Repeatable Evaluation Contract", reference)
        self.assertIn("one repository owner", skill.lower())
        self.assertRegex(
            skill.lower(), r"standalone\s+self-validating\s+distribution"
        )
        self.assertIn("--target claude|codex|grok", skill)
        for target in ("Claude", "Codex", "Grok"):
            self.assertIn(target, reference)
        self.assertIn("candidate session", reference)
        self.assertIn("grader session", reference)
        self.assertIn("no attributable automatic skill activation event", reference)
        for packaged_path in (
            "scripts/eval-skill.py",
            "scripts/eval-skill_test.py",
            "evals/evals.json",
            "evals/trigger-eval.json",
        ):
            self.assertIn(packaged_path, readme)

    def test_eval_docs_match_the_observable_runner_and_iteration_method(self):
        reference = PACKAGE.joinpath("REFERENCE.md").read_text(encoding="utf-8")
        readme = PACKAGE.joinpath("README.md").read_text(encoding="utf-8")
        contract = " ".join((reference + "\n" + readme).lower().split())

        for phrase in (
            "each receive the full `--timeout` bound",
            "candidate-events.jsonl",
            "candidate-timing.json",
            "system/init",
            "matching `read_file`",
            "strict-majority",
            "evals/fixtures/skills/<name>",
            "previous skill version",
            "blind comparison",
            "benchmark.json",
            "human feedback",
            "train/validation",
        ):
            self.assertIn(phrase, contract)
        self.assertNotIn("share a 900-second case deadline", contract)
        self.assertNotIn("share a case deadline", contract)


if __name__ == "__main__":
    unittest.main(verbosity=2)
