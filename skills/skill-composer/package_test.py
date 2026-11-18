#!/usr/bin/env python3
"""Package-contract tests for Skill Composer."""

import json
from pathlib import Path
import re
import subprocess
import sys
import unittest


PACKAGE = Path(__file__).parent


def reference(name):
    return PACKAGE.joinpath("references", name).read_text(encoding="utf-8")


def lookup_material():
    """Every lookup reference: references/*.md except the branch workflows and evals."""
    return "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(PACKAGE.joinpath("references").glob("*.md"))
        if path.name not in {"evaluation.md", "review.md", "release.md"}
    )


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
        self.assertEqual("LICENSE.md", fields["license"])
        self.assertEqual(
            "# License\n\nPersonal use.\n",
            PACKAGE.joinpath(fields["license"]).read_text(encoding="utf-8"),
        )

    def test_package_check_passes_on_skill_composer_itself(self):
        result = subprocess.run(
            [sys.executable, str(PACKAGE / "scripts" / "check-skill.py"), str(PACKAGE)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_every_workflow_runs_the_package_check(self):
        skill = " ".join(PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8").split())
        step7 = skill.split("### Step 7:", 1)[1]
        self.assertIn(
            "`python3 <this skill's directory>/scripts/check-skill.py <target-skill-dir>`",
            step7,
        )
        self.assertIn("rerun it to `OK`", step7)
        self.assertIn(
            "read [references/package-check.md](references/package-check.md) in full",
            step7,
        )
        guide = " ".join(reference("package-check.md").split())
        self.assertLessEqual(len(reference("package-check.md").encode("utf-8")), 3000)
        self.assertIn("Read this file in full when the package check reports a finding", guide)
        self.assertIn("you choose the fix, not whether to comply", guide)
        for check_name in (
            "whole-file-pointers",
            "entry-point-size",
            "reachable-references",
            "cross-skill-links",
            "local-links",
        ):
            self.assertIn(f"## {check_name}", reference("package-check.md"))
        self.assertIn("Move it into `SKILL.md`", guide)
        self.assertIn("references/package-check.md", PACKAGE.joinpath("README.md").read_text(encoding="utf-8"))
        self.assertIn("the package check, package and target schema", step7)
        self.assertIn("scripts/check-skill.py <target-skill-dir>", " ".join(reference("review.md").split()))
        self.assertIn("Run the package check from [Step 7]", " ".join(reference("release.md").split()))
        spec = " ".join(PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8").split())
        self.assertIn("## Package Check Design", spec)
        design = spec.split("## Package Check Design", 1)[1].split(" ## ", 1)[0]
        for rule in (
            "satisfies the Script Requirements in "
            "[references/package-layout.md](references/package-layout.md)",
            "A finding fails hard",
            "never copied into the skills it checks",
            "A false positive is a bug",
            "Line prefixes and exit codes are stable",
            "Standard library only",
            "seen failing first",
            "**Why:**",
        ):
            self.assertIn(rule, design)
        for general_rule in ("can decide exactly", "list fixes inline", "prints it"):
            self.assertNotIn(general_rule, design.split("**Why:**", 1)[0])

    def test_references_are_whole_files_reached_from_the_entry_point(self):
        self.assertFalse(PACKAGE.joinpath("REFERENCE.md").exists())
        references = PACKAGE / "references"
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        for reference in sorted(references.glob("*.md")):
            self.assertIn(f"](references/{reference.name})", skill, reference.name)

    def test_bounded_entry_point_is_a_leading_standing_rule_with_sources(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        spec = " ".join(PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8").split())
        leading = " ".join(skill.split("## Choose the Workflow", 1)[0].split())
        bounded = leading.split("### Bounded Entry Point", 1)[1].split("### ", 1)[0]

        for phrase in (
            "stays within **15,000 bytes** ([why](SPEC.md))",
            "every standing rule (one that applies across a whole run)",
            "must-follow gates first",
            "Point at whole reference files",
            "read the file in full; a file tool cannot jump to an anchor",
            "invoke it by name",
            "([why](SPEC.md))",
            "Script what a script can check",
            "at most its core reason",
            "Within the cap, every passage still earns its place.",
        ):
            self.assertIn(phrase, bounded)
        self.assertNotIn("Split a reference", bounded)
        for match in re.finditer(r"\]\((references/[^)]+)\)", skill):
            clause = re.split(r"[.;]\s", skill[match.end():], maxsplit=1)[0]
            self.assertIn("in full", clause, match.group(1))
        portability = " ".join(
            skill.split("### Portability", 1)[1].split("**Harness research:**", 1)[0].split()
        )
        self.assertIn(
            "**portable core** (goal, inputs, outputs, decision rules, workflow, "
            "failure behavior, completion criteria)",
            portability,
        )

        self.assertIn("## Bounded Entry Point", spec)
        for evidence in (
            "https://agentskills.io/specification",
            "Instructions (< 5000 tokens recommended)",
            "https://code.claude.com/docs/en/skills.md#skill-content-lifecycle",
            "keeping the first 5,000 tokens of each",
            "combined budget of 25,000 tokens",
            "2026-11-17",
            "What a script can check is scripted",
            "A file tool cannot jump to a Markdown anchor",
            "2026-11-18",
        ):
            self.assertIn(evidence, spec)
        self.assertNotIn("Reasonable size is a behavioral property", spec)
        layout = " ".join(reference("package-layout.md").split())
        self.assertIn("[package-check.md](package-check.md) in full", layout)
        self.assertNotIn("split that section into its own reference", layout)
        for rule in (
            "checks only what it can decide exactly",
            "does not list fixes inline",
            "the output prints it",
        ):
            self.assertIn(rule, layout)

    def test_cross_skill_pointers_require_invocation_not_file_reads(self):
        skill = " ".join(PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8").split())
        spec = " ".join(PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8").split())
        review = " ".join(reference("review.md").split())
        bounded = skill.split("### Bounded Entry Point", 1)[1].split("### ", 1)[0]

        for phrase in (
            "**invoke it by name through the host's skill mechanism**",
            "the Skill tool",
            "**Reading its `SKILL.md` with a file tool is not invocation**",
            "tends to take only part of it and miss gates written elsewhere "
            "([why](SPEC.md))",
        ):
            self.assertIn(phrase, bounded)
        self.assertIn(
            "records only Skill tool and slash-command invocations for re-attachment",
            spec,
        )
        self.assertIn(
            "invoke by name through the host's skill mechanism, never by file read",
            review,
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
        lookup = lookup_material()
        sections = re.findall(
            r"^## ([^\n]+)\n(.*?)(?=^## |\Z)",
            spec,
            flags=re.MULTILINE | re.DOTALL,
        )

        self.assertGreater(len(sections), 0)
        for heading, body in sections:
            self.assertIn("**Why:**", body, heading)
        self.assertNotIn("### Skill Composer Admission Ledger", lookup)

    def test_every_instruction_step_has_a_local_completion_criterion(self):
        workflow = "\n".join(
            PACKAGE.joinpath(*name).read_text(encoding="utf-8")
            for name in (
                ("SKILL.md",),
                ("references", "review.md"),
                ("references", "release.md"),
            )
        )
        fenced_blocks = re.findall(
            r"^```[^\n]*\n(.*?)^```$",
            reference("authoring-examples.md"),
            flags=re.MULTILINE | re.DOTALL,
        )
        runtime = re.sub(
            r"^```[^\n]*\n.*?^```$",
            "",
            workflow,
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

        self.assertGreaterEqual(len(runtime_steps), 17)
        self.assertGreaterEqual(len(example_steps), 2)
        for heading, body in runtime_steps + example_steps:
            self.assertIn("**Done when:**", body, heading)

    def test_contract_lock_steps_finish_with_every_declared_input(self):
        review = PACKAGE.joinpath("references", "review.md").read_text(
            encoding="utf-8"
        )
        release = PACKAGE.joinpath("references", "release.md").read_text(
            encoding="utf-8"
        )
        research = PACKAGE.joinpath("HARNESS-RESEARCH.md").read_text(
            encoding="utf-8"
        )

        checks = {
            "Review Step 1: Lock the Contract": (
                review,
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
                release,
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
        lookup = lookup_material()

        for duplicate in (
            "**Portable required fields**",
            "your-skill-name/",
            "## Quick Checklist",
            "### Pattern 1: Sequential Orchestration",
        ):
            self.assertNotIn(duplicate, skill)
        self.assertNotIn("### Pattern 1: Sequential Orchestration", lookup)
        self.assertNotIn("**Portable core:**", lookup)
        self.assertIn("## YAML Frontmatter Specification", reference("frontmatter.md"))
        layout = reference("package-layout.md")
        self.assertIn("## Directory Structure Patterns", layout)
        self.assertIn("# Workflow Patterns", reference("workflow-patterns.md"))
        layout_contract = " ".join(layout.split())
        self.assertIn("exactly `SKILL.md`", layout_contract)
        self.assertIn("parent directory", layout_contract)

    def test_invocation_and_evaluation_boundaries_are_decision_complete(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        for phrase in (
            "context load",
            "cognitive load",
            "explicit user authorization",
            "disposable fixture",
        ):
            self.assertIn(phrase, skill.lower())
        self.assertNotIn("## Invocation Modes", lookup_material())

    def test_review_findings_keep_the_complete_record_when_changes_are_forbidden(self):
        review = PACKAGE.joinpath("references", "review.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("A finding is the complete review record", review)
        self.assertIn("only findings and evidence", review)
        self.assertIn("does not authorize applying the fix", review)

    def test_authoring_another_skill_uses_only_the_shared_eval_runner_public_seam(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        boundary = skill.split("# Skill Composer", 1)[1].split(
            "## Authoring Authority", 1
        )[0]
        contract = " ".join(boundary.split())

        self.assertIn(
            "Otherwise do not inspect its eval manifests, fixtures, package tests, "
            "or eval runner implementation",
            contract,
        )
        self.assertIn("Step 7 says when to run its scripts' public CLIs", contract)
        self.assertIn("the target needs no runner copy", contract)
        self.assertIn(
            "When modifying, reviewing, testing, or releasing Skill Composer "
            "itself, first read [SPEC.md](SPEC.md) in full",
            contract,
        )

        full_contract = " ".join(skill.split())
        step5 = full_contract.split("### Step 5:", 1)[1].split("### Step 6:", 1)[0]
        self.assertIn(
            "When the `writing-for-agents` skill is available, invoke it by name "
            "and follow it; otherwise read [references/writing.md]"
            "(references/writing.md) in full and follow it.",
            step5,
        )
        self.assertNotIn("put critical rules first", step5)
        self.assertIn("`writing-for-agents` or `references/writing.md` was applied", step5)
        self.assertIn(
            "Never scan home or user-level skill directories for examples, "
            "validators, or target evidence",
            full_contract,
        )

    def test_introduction_keeps_eval_reference_behind_the_update_router(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        boundary = skill.split("# Skill Composer", 1)[1].split(
            "## Authoring Authority", 1
        )[0]
        contract = " ".join(boundary.split())
        update_route = skill.split("- **Update:**", 1)[1].split(
            "\n- **Review:**", 1
        )[0]

        self.assertNotIn("[Evaluation Reference](references/evaluation.md)", contract)
        self.assertIn(
            "[Evaluation Reference](references/evaluation.md)", update_route
        )
        self.assertIn("the target needs no runner copy", contract)

    def test_update_router_admits_eval_guidance_from_observable_inputs_only(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        update_route = skill.split("- **Update:**", 1)[1].split(
            "\n- **Review:**", 1
        )[0]
        contract = " ".join(update_route.split())

        self.assertIn(
            "inventory contains `evals/evals.json` or `evals/trigger-eval.json`",
            contract,
        )
        self.assertIn("user explicitly asks for eval work", contract)
        self.assertIn(
            "read the [Evaluation Reference](references/evaluation.md) in full "
            "before editing the target",
            contract,
        )
        self.assertIn("Otherwise keep that reference unopened", contract)

    def test_no_suite_branch_cannot_treat_eval_check_as_a_schema_validator(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        evaluation_step = skill.split("### Step 7:", 1)[1].split("\n## ", 1)[0]
        contract = " ".join(evaluation_step.split())

        self.assertIn("do not search, grep, or open the Evaluation Reference", contract)
        self.assertIn("do not inspect or invoke `eval-skill.py`", contract)

    def test_target_compatibility_claims_require_matching_behavior_evidence(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        evaluation_step = skill.split("### Step 7:", 1)[1].split("\n## ", 1)[0]
        contract = " ".join(evaluation_step.lower().split())

        self.assertIn("frontmatter, body, changelog, and final report", contract)
        self.assertIn("verified, supported, or tested", contract)
        self.assertIn("matching target-behavior ledger row is `pass`", contract)
        self.assertIn("static schema validation", contract)
        self.assertIn("manual walkthrough", contract)

    def test_packaged_evals_are_opt_in_and_existing_suites_follow_changed_behavior(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        evaluation_step = skill.split("### Step 7:", 1)[1].split("\n## ", 1)[0]
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
        self.assertIn(
            "does not load the branch-only evaluation reference",
            assertions["creates-a-portable-skill"]["keeps-evals-opt-in"].lower(),
        )
        self.assertIn(
            "reads the evaluation reference",
            assertions["updates-repeatable-mechanics"][
                "maintains-existing-evals"
            ].lower(),
        )
        self.assertIn(
            "does not load the branch-only evaluation reference",
            assertions["updates-then-packages-cross-harness"][
                "keeps-evals-opt-in"
            ].lower(),
        )
        for case_id in (
            "creates-a-portable-skill",
            "updates-then-packages-cross-harness",
        ):
            self.assertIn("asks-before-adding-evals", assertions[case_id])

    def test_trigger_suite_stages_competitors_for_both_labels(self):
        manifest = json.loads(
            PACKAGE.joinpath("evals", "trigger-eval.json").read_text(
                encoding="utf-8"
            )
        )
        fixtures = PACKAGE / "evals" / "fixtures" / "skills"
        staged = {True: 0, False: 0}
        for query in manifest["queries"]:
            competitors = query.get("additional_skills", [])
            for name in competitors:
                self.assertTrue(
                    fixtures.joinpath(name, "SKILL.md.fixture").is_file(), name
                )
            if competitors:
                staged[query["should_trigger"]] += 1
        self.assertGreaterEqual(staged[True], 3)
        self.assertGreaterEqual(staged[False], 3)

    def test_history_is_in_date_mode_and_records_net_changes_only(self):
        changelog = PACKAGE.joinpath("CHANGELOG.md").read_text(encoding="utf-8")

        self.assertNotIn("## [Unreleased]", changelog)
        sections = re.findall(r"^## (.+)$", changelog, flags=re.MULTILINE)
        first_numbered = next(
            i for i, heading in enumerate(sections) if heading.startswith("[")
        )
        dates = sections[:first_numbered]
        self.assertGreater(len(dates), 0)
        for heading in dates:
            self.assertRegex(heading, r"^\d{4}-\d{2}-\d{2}$")
        self.assertEqual(sorted(dates, reverse=True), dates)
        self.assertEqual(len(set(dates)), len(dates))
        for heading in sections[first_numbered:]:
            self.assertRegex(heading, r"^\[\d+\.\d+\.\d+\] - \d{4}-\d{2}-\d{2}$")
        for residue in (
            "### Make transport trust explicit",
            "### State publication cleanup limits honestly",
            "harness-document",
            "Replace `HTTPS_PROXY`",
            "Remove links to `examples/*.md`",
        ):
            self.assertNotIn(residue, changelog)

    def test_all_declared_authoring_workflows_have_runtime_routes(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        frontmatter = skill.split("---\n", 2)[1].lower()
        router = skill.split("## Choose the Workflow\n", 1)[1].split(
            "\n## Planning Before Creating or Updating", 1
        )[0]

        expected_routes = {
            "Create": "#creating-or-updating-a-skill",
            "Update": "#planning-before-creating-or-updating",
            "Review": "(references/review.md)",
            "Package or release": "(references/release.md)",
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
        release = PACKAGE.joinpath("references", "release.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("# Packaging and Releasing a Skill", release)
        for gate in ("clean instance", "portable fallback", "isolation", "coexistence"):
            self.assertIn(gate, release)

    def test_dynamic_harness_facts_have_one_research_owner(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        skill_contract = " ".join(skill.split())
        lookup = lookup_material()
        research = PACKAGE.joinpath("HARNESS-RESEARCH.md").read_text(encoding="utf-8")
        distribution = reference("distribution.md")

        self.assertIn("[HARNESS-RESEARCH.md](HARNESS-RESEARCH.md)", skill)
        self.assertIn("(../HARNESS-RESEARCH.md)", distribution)
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

        current_guidance = skill + lookup
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
            "SPEC.md",
            "HARNESS-RESEARCH.md",
            *(f"references/{path.name}" for path in PACKAGE.joinpath("references").glob("*.md")),
        ):
            text = PACKAGE.joinpath(name).read_text(encoding="utf-8").lower()
            self.assertNotIn("examples/", text, name)
            self.assertNotIn("historical pattern snapshot", text, name)

    def test_release_evaluation_reference_keeps_behavior_gates_visible(self):
        readme = PACKAGE.joinpath("README.md").read_text(encoding="utf-8")
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        evaluation = PACKAGE.joinpath("references", "evaluation.md").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "[Evaluation Reference](references/evaluation.md)", readme
        )
        self.assertIn("necessary, not sufficient", evaluation)
        for workflow in ("Create", "Update", "Review", "Package/release"):
            self.assertIn(f"| {workflow} |", evaluation)
        for gate in (
            "Fresh-context activation",
            "portable fallback",
            "Isolation and coexistence",
            "clean installation",
            "`unknown`",
        ):
            self.assertIn(gate, evaluation)
        release = PACKAGE.joinpath("references", "release.md").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "candidate validation has a result for every locked pre-install gate",
            release,
        )
        self.assertIn(
            "the final artifact itself matches the clean-install inventory", release
        )

    def test_release_publishes_only_with_explicit_user_authorization(self):
        release = " ".join(reference("release.md").split())
        promote = release.split("### Release Step 5:", 1)[1]
        self.assertIn(
            "publish only when the user explicitly asked for or authorized publication",
            promote,
        )
        self.assertLess(
            promote.index("authorized publication"), promote.index("In date mode")
        )

    def test_validation_ledger_accounts_for_every_applicable_gate(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        evaluation_step = re.search(
            r"^### Step 7:[^\n]+\n(.*?)(?=^## |\Z)",
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
            r"^### Step 7:[^\n]+\n(.*?)(?=^## |\Z)",
            skill,
            flags=re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(evaluation_step)
        route = " ".join(evaluation_step.group(1).lower().split())
        contract = " ".join(
            PACKAGE.joinpath("references", "evaluation.md")
            .read_text(encoding="utf-8")
            .lower()
            .split()
        )

        self.assertIn(
            "[evaluation reference](references/evaluation.md)", route
        )

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
            r"^### Step 7:[^\n]+\n(.*?)(?=^## |\Z)",
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
        rule = (
            "an internal implementation replacement with unchanged public "
            "invocation, inputs, and outputs has no migration entry"
        )
        skill = " ".join(
            PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8").lower().split()
        )
        self.assertIn(rule, " ".join(reference("changelog.md").lower().split()))
        self.assertNotIn(rule, skill)

    def test_changelog_history_uses_the_published_artifact_as_its_baseline(self):
        skill = " ".join(
            PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8").lower().split()
        )
        changelog = " ".join(reference("changelog.md").lower().split())

        for phrase in (
            "last artifact actually published to the changelog's audience",
            "not a diary of commits, drafts, or revisions",
            "does not prove that users received it",
            "resulting first-release contract",
        ):
            self.assertIn(phrase, changelog)

        self.assertIn("establish the published baseline", changelog)
        self.assertIn("relative to that baseline", changelog)
        self.assertNotIn("relative to that baseline", skill)

    def test_changelog_mode_defaults_to_dates_and_asks_on_a_version_signal(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        route = skill.split("### Step 6:", 1)[1].split("### Step 7:", 1)[0]
        self.assertIn("(references/changelog.md) in full", route)
        step = " ".join(
            reference("changelog.md").split("### Changelog modes", 1)[1]
            .split("\n### ", 1)[0]
            .lower()
            .split()
        )

        for phrase in (
            "date mode is the default",
            "an explicit request for a mode wins",
            "an existing changelog keeps its mode",
            "without one, use date mode and do not ask",
            "ask whether to use version mode",
            "when no one can answer, use date mode and report the signal",
            "a sibling package's version is not a signal",
        ):
            self.assertIn(phrase, step)

    def test_date_mode_carries_no_release_bookkeeping(self):
        changelog_format = " ".join(reference("changelog.md").lower().split())
        release = " ".join(
            PACKAGE.joinpath("references", "release.md")
            .read_text(encoding="utf-8")
            .split("### Release Step 1:", 1)[1]
            .lower()
            .split()
        )

        for phrase in (
            "### changelog modes",
            "the date of the change",
            "date mode needs no published baseline",
            "the entry fields and the evidence gate are the same in both",
            "when date mode takes over an `unreleased` section",
        ):
            self.assertIn(phrase, changelog_format)
        for phrase in (
            "in date mode",
            "date mode adds no version bookkeeping",
            "leave any target-owned version metadata",
            "the candidate is the final artifact",
        ):
            self.assertIn(phrase, release)

    def test_date_default_is_a_maintainer_requirement_with_eval_coverage(self):
        spec = " ".join(
            PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8").lower().split()
        )
        self.assertIn("changelogs default to date mode", spec)

        manifest = json.loads(
            PACKAGE.joinpath("evals", "evals.json").read_text(encoding="utf-8")
        )
        cases = {case["id"]: case for case in manifest["evals"]}
        self.assertIn("asks-before-version-mode", cases)
        self.assertIn("keeps-an-existing-version-changelog", cases)
        history = {
            item["id"]: item["description"]
            for item in cases["updates-then-packages-cross-harness"]["assertions"]
        }["records-evidence-backed-history"]
        self.assertIn("date mode", history.lower())

    def test_script_changes_require_observed_public_seam_red_green_evidence(self):
        skill = " ".join(
            PACKAGE.joinpath("SKILL.md")
            .read_text(encoding="utf-8")
            .lower()
            .split()
        )
        layout = " ".join(reference("package-layout.md").lower().split())

        expected = (
            "run the public-seam test and preserve its observed failure before "
            "writing the implementation"
        )
        self.assertNotIn(expected, skill)
        self.assertIn(expected, layout)
        self.assertIn("add a dependency only when it removes more than it costs", layout)
        self.assertIn(
            "before adding or changing a script, read [references/package-layout.md]"
            "(references/package-layout.md) in full",
            skill,
        )
        self.assertIn(
            "invoke the `tdd` skill by name when available and follow it; "
            "otherwise follow the red-green loop in that file",
            skill,
        )
        self.assertIn("red-green loop, replaced by the `tdd` skill when available", layout)

    def test_bundled_core_writing_rules_replace_or_are_replaced_by_the_sibling_skill(self):
        writing = reference("writing.md")
        spec = " ".join(PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8").split())
        readme = PACKAGE.joinpath("README.md").read_text(encoding="utf-8")

        self.assertLessEqual(len(writing.encode("utf-8")), 1700)
        self.assertIn("Read this file in full", writing)
        self.assertIn("when the `writing-for-agents` skill is unavailable", writing)
        for principle in (
            "completion criterion",
            "every changed file",
            "hard guardrail",
            "`--help`",
            "delete the whole sentence",
            "behind a pointer",
            "one term per concept",
        ):
            self.assertIn(principle, writing)
        self.assertIn("## Bundled Core Rules", spec)
        for phrase in (
            "does not depend on a sibling skill being installed or staying unchanged",
            "replaces the bundled rules",
            "short core, not a copy",
        ):
            self.assertIn(phrase, spec)
        self.assertIn("references/writing.md", readme)
        self.assertIn(
            "https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents",
            readme,
        )

    def test_repeatable_eval_infrastructure_is_package_local_and_reachable(self):
        script = PACKAGE / "scripts" / "eval-skill.py"
        script_test = PACKAGE / "scripts" / "eval-skill_test.py"
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        evaluation = PACKAGE.joinpath("references", "evaluation.md").read_text(
            encoding="utf-8"
        )
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
        self.assertIn("functional=6 trigger=20", result.stdout)
        self.assertIn(
            "[Evaluation Reference](references/evaluation.md)",
            skill,
        )
        self.assertIn("## Repeatable Evaluation Contract", evaluation)
        self.assertIn("one repository owner", evaluation.lower())
        self.assertRegex(
            evaluation.lower(), r"standalone\s+self-validating\s+distribution"
        )
        self.assertIn("--target claude|codex|grok", evaluation)
        for target in ("Claude", "Codex", "Grok"):
            self.assertIn(target, evaluation)
        self.assertIn("candidate session", evaluation)
        self.assertIn("grader session", evaluation)
        self.assertIn(
            "no attributable automatic skill activation event", evaluation
        )
        for packaged_path in (
            "scripts/eval-skill.py",
            "scripts/eval-skill_test.py",
            "evals/evals.json",
            "evals/trigger-eval.json",
        ):
            self.assertIn(packaged_path, readme)

    def test_eval_guidance_is_disclosed_only_for_admitted_suites(self):
        evaluation_path = PACKAGE / "references" / "evaluation.md"
        self.assertTrue(evaluation_path.is_file())

        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        lookup = lookup_material()
        readme = PACKAGE.joinpath("README.md").read_text(encoding="utf-8")
        evaluation = evaluation_path.read_text(encoding="utf-8")
        evaluation_step = skill.split("### Step 7:", 1)[1].split("\n## ", 1)[0]
        routed_contract = " ".join(evaluation_step.lower().split())
        evaluation_contract = " ".join(evaluation.lower().split())
        readme_contract = " ".join(readme.lower().split())

        self.assertIn(
            "before creating, updating, running, tuning, or maintaining an "
            "admitted eval suite",
            routed_contract,
        )
        self.assertIn(
            "[evaluation reference](references/evaluation.md)", routed_contract
        )
        self.assertIn(
            "[evaluation reference](references/evaluation.md)", readme.lower()
        )

        for heading in (
            "## Repeatable Evaluation Contract",
            "## Evaluation Tuning Loop",
            "## Testing Methodology",
        ):
            self.assertIn(heading, evaluation)
            self.assertNotIn(heading, lookup)

        for disclosed_detail in (
            "branch-to-case coverage table",
            "change exactly one owner per iteration",
            "system/init",
            "benchmark.json",
        ):
            self.assertIn(disclosed_detail, evaluation_contract)
            self.assertNotIn(disclosed_detail, routed_contract)
            self.assertNotIn(disclosed_detail, readme_contract)

    def test_eval_docs_match_the_observable_runner_and_iteration_method(self):
        evaluation = PACKAGE.joinpath("references", "evaluation.md").read_text(
            encoding="utf-8"
        )
        contract = " ".join(evaluation.lower().split())

        for phrase in (
            "adapts parts of the official agent skills guide",
            "https://agentskills.io/skill-creation/evaluating-skills",
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
            "claude-sonnet-5",
            "gpt-5.6-terra",
            "grok-4.6",
            "canonical cli vocabulary",
            "claude's `--effort` flag",
            "codex's `model_reasoning_effort` configuration",
            "grok's `--reasoning-effort` flag",
            "linux process is uid 0",
            "non-root uid before claude starts",
            "without disabling claude's native sandbox",
        ):
            self.assertIn(phrase, contract)
        self.assertNotIn("share a 900-second case deadline", contract)
        self.assertNotIn("share a case deadline", contract)

    def test_eval_runner_owns_focused_execution_and_debug_evidence(self):
        evaluation = PACKAGE.joinpath("references", "evaluation.md").read_text(
            encoding="utf-8"
        )
        contract = " ".join(evaluation.lower().split())

        for phrase in (
            "## before writing a case",
            "`run-one` executes exactly one case",
            "`run-all` runs the complete suite",
            "fails fast",
            "`--keep-going`",
            "one frozen package snapshot",
            "sanitized report",
            "`inspect`",
            "`rerun`",
            "package hash has drifted",
            "deictic owner",
            "valid json is transport evidence, not completion evidence",
            "before increasing a timeout",
            "fake target",
            "one authorized real probe",
        ):
            self.assertIn(phrase, contract)

    def test_eval_tuning_changes_one_owner_and_accepts_only_the_final_tree(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        evaluation = PACKAGE.joinpath("references", "evaluation.md").read_text(
            encoding="utf-8"
        )
        skill_contract = " ".join(skill.lower().split())
        self.assertIn("## Evaluation Tuning Loop", evaluation)
        tuning_contract = " ".join(
            evaluation.split("## Evaluation Tuning Loop", 1)[1]
            .split("\n## ", 1)[0]
            .lower()
            .split()
        )

        self.assertIn(
            "[evaluation reference](references/evaluation.md)",
            skill_contract,
        )

        for phrase in (
            "change exactly one owner per iteration",
            "skill behavior, eval design, runner or adapter, or provider or environment",
            "rerun the same case",
            "freeze the final tree",
            "one explicit hypothesis",
            "a changed case starts a new baseline",
            "unknown is not a skill failure",
            "diagnostic timeout is not an acceptance threshold",
            "realistic files and competing skills",
            "do not combine passes from different intermediate trees",
        ):
            self.assertIn(phrase, tuning_contract)

        manifest = json.loads(
            PACKAGE.joinpath("evals", "evals.json").read_text(encoding="utf-8")
        )
        update_case = next(
            case
            for case in manifest["evals"]
            if case["id"] == "updates-repeatable-mechanics"
        )
        assertion = " ".join(
            item["description"] for item in update_case["assertions"]
        ).lower()
        self.assertIn("if an eval result is non-green or flaky", assertion)
        self.assertIn(
            "records unavailable fresh-session behavior as unknown", assertion
        )
        self.assertIn("explicit one-case scope and sanitized report", assertion)
        self.assertIn("full frozen-suite scope", assertion)
        for phrase in (
            "classifies the result before editing",
            "changes only the responsible owner",
            "reruns the same case",
        ):
            self.assertIn(phrase, assertion)


if __name__ == "__main__":
    unittest.main(verbosity=2)
