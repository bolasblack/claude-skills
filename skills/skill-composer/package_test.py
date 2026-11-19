#!/usr/bin/env python3
"""Package-contract tests for Skill Composer."""

import ast
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
        self.assertIn("Read this file in full when the package check reports a finding", guide)
        self.assertIn("you choose the fix, not whether to comply", guide)
        self.assertIn("states its requirement and why it exists", guide)
        sections = {
            part.split("\n", 1)[0]: " ".join(part.split())
            for part in reference("package-check.md").split("\n## ")[1:]
        }
        # The reason each check used to print now lives in its own section.
        for check_name, reason in (
            ("entry-point", "discover a skill by the `SKILL.md` at its root"),
            ("entry-point-size", "([why](bounded-entry-point.md))"),
            ("frontmatter", "route by `name` and `description`"),
            ("local-links", "installed on its own"),
            ("whole-file-pointers", "cannot jump to an anchor"),
            ("cross-skill-links", "not re-attached after compaction"),
            ("nested-entry-points", "published as a separate skill"),
            ("reachable-references", "no pointer reaches is never read"),
            ("spec-pointer", "never read by the agent maintaining the skill"),
        ):
            self.assertIn(check_name, sections)
            self.assertIn(reason, sections[check_name], check_name)
        self.assertIn("Move it into `SKILL.md`", guide)
        self.assertIn("references/package-check.md", PACKAGE.joinpath("README.md").read_text(encoding="utf-8"))
        self.assertIn("the package check, package and target schema", step7)
        self.assertIn("scripts/check-skill.py <target-skill-dir>", " ".join(reference("review.md").split()))
        self.assertIn("Run the package check from [Step 7]", " ".join(reference("release.md").split()))
        spec = " ".join(PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8").split())
        mechanical = spec.split("## Mechanical Work Is a Script", 1)[1].split(" ## ", 1)[0]
        self.assertIn("`scripts/check-skill.py`, run on every skill it creates, updates, reviews, or releases", mechanical)
        self.assertNotIn("one reason per finding kind", spec)
        self.assertIn("you choose the fix, not whether to comply", guide)
        layout = " ".join(reference("package-layout.md").split())
        for rule in (
            "One copy of the package check lives in Skill Composer and is never copied into a skill it checks",
            "A false positive is a bug",
            "Prefixes and exit codes stay stable, so the output can be filtered and scripted",
            "A script uses only its runtime's standard library",
            "preserve its observed failure",
        ):
            self.assertIn(rule, layout)

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
            "stays within **15,000 bytes** ([why](references/bounded-entry-point.md))",
            "every standing rule (one that applies across a whole run)",
            "must-follow gates first",
            "Point at whole reference files",
            "read the file in full; a file tool cannot jump to an anchor",
            "invoke it by name",
            "Script what a script can check",
            "Within the cap, every passage still earns its place.",
        ):
            self.assertIn(phrase, bounded)
        self.assertNotIn("Split a reference", bounded)
        for match in re.finditer(r"\[([^\]]*)\]\((references/[^)]+)\)", skill):
            if match.group(1) == "why":
                continue
            clause = re.split(r"[.;]\s", skill[match.end():], maxsplit=1)[0]
            self.assertIn("in full", clause, match.group(2))
        portability = " ".join(
            skill.split("### Portability", 1)[1].split("**Harness research:**", 1)[0].split()
        )
        self.assertIn(
            "**portable core** (goal, inputs, outputs, decision rules, workflow, "
            "failure behavior, completion criteria)",
            portability,
        )

        self.assertIn("## Efficient Use of the Agent's Context", spec)
        self.assertIn("## The Agent Acts on the Complete Original Text", spec)
        explanation = " ".join(reference("bounded-entry-point.md").split())
        for evidence in (
            "https://agentskills.io/specification",
            "Instructions (< 5000 tokens recommended)",
            "https://code.claude.com/docs/en/skills.md#skill-content-lifecycle",
            "keeping the first 5,000 tokens of each",
            "combined budget of 25,000 tokens",
            "The cap is in bytes because no local tokenizer is available",
            "Text that is mostly CJK may use more tokens per byte",
            "2026-11-17",
            "A file tool cannot jump to a Markdown anchor",
            "about ten real violations",
        ):
            self.assertIn(evidence, explanation)
        self.assertNotIn("Reasonable size is a behavioral property", spec)
        layout = " ".join(reference("package-layout.md").split())
        self.assertIn("[package-check.md](package-check.md) in full", layout)
        self.assertNotIn("split that section into its own reference", layout)
        for rule in (
            "checks only what it can decide exactly",
            "does not list fixes inline",
            "A script's output is written for an agent to read and act on",
            "one fact per line behind a stable prefix",
            "the facts the next decision needs",
            "exit codes that separate pass, findings, and a usage error",
            "run Skill Composer's own `scripts/check-skill.py`",
            "model a new script on it rather than copying it",
            "points to the file in the skill that holds the requirement",
            "one pointer for the whole run is enough",
            "because a wording check rewards the phrase, not the behavior",
            "carries no reason of its own",
            "The pointed-to text exists",
        ):
            self.assertIn(rule, layout)
        self.assertNotIn("one core reason per kind of finding", layout)

    def test_entry_point_explanation_lives_once_behind_why_links(self):
        skill = PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8")
        spec = PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8")
        guide = reference("package-check.md")
        readme = PACKAGE.joinpath("README.md").read_text(encoding="utf-8")
        link = "([why](references/bounded-entry-point.md))"

        self.assertIn(f"stays within **15,000 bytes** {link}", skill)
        why = spec.split("## Efficient Use of the Agent's Context", 1)[1].split("\n## ", 1)[0]
        why = " ".join(why.split("**Why:**", 1)[1].split())
        self.assertTrue(why.endswith(f"{link}."), why)
        size = guide.split("## entry-point-size", 1)[1].split("\n## ", 1)[0]
        self.assertIn("([why](bounded-entry-point.md))", size)
        for repeated in ("5,000 tokens", "bytes per token", "agentskills.io"):
            self.assertNotIn(repeated, size)
            self.assertNotIn(repeated, why)
        self.assertIn("`references/bounded-entry-point.md`", readme)

    def test_references_hold_three_kinds_and_only_explanations_skip_a_read_condition(self):
        skill = " ".join(PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8").split())
        bounded = skill.split("### Bounded Entry Point", 1)[1].split("### ", 1)[0]
        for rule in (
            "because a host may not restore a reference read earlier once the context is compacted",
            "A reference holds one branch's workflow, lookup material, or the explanation of rules; "
            "a run does not read an explanation, and only why links reach it.",
            "each workflow or lookup file with its read condition (a why link needs none)",
        ):
            self.assertIn(rule, bounded)
        self.assertIn("A run does not need it", reference("bounded-entry-point.md"))

    def test_reason_provenance_rule_names_its_boundary(self):
        reasons = " ".join(reference("rule-reasons.md").split())
        self.assertIn(
            "This governs `SKILL.md` and its references only: a `SPEC.md` Why may quote "
            "the author, and a changelog records history by design.",
            reasons,
        )
        self.assertIn("it may quote the author", " ".join(reference("spec.md").split()))

    def test_package_check_docstring_names_its_current_line_prefixes(self):
        script = PACKAGE.joinpath("scripts", "check-skill.py").read_text(encoding="utf-8")
        printed = set(re.findall(r"print\(\s*f?[\"']([A-Z]+:?)[ \"']", script))
        docstring = ast.get_docstring(ast.parse(script))
        self.assertEqual({"FAIL", "INFO", "FIX:", "RESULT", "OK"}, printed)
        for prefix in printed:
            self.assertIn(f'"{prefix}', docstring, prefix)

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
            "([why](references/bounded-entry-point.md))",
        ):
            self.assertIn(phrase, bounded)
        self.assertIn(
            "records only Skill tool and slash-command invocations for re-attachment",
            " ".join(reference("bounded-entry-point.md").split()),
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
        self.assertIn(
            "harnesses change often, so a harness fact written into a skill goes stale quickly",
            skill,
        )
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
            self.assertLessEqual(body.count("**Why:**"), 1, heading)
        self.assertNotRegex(spec, r"\d{4}-\d{2}-\d{2}")
        self.assertNotIn("### Skill Composer Admission Ledger", lookup)

    def test_spec_guidance_has_one_owner_with_an_extraction_method_and_invented_shape(self):
        skill = " ".join(PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8").split())
        step2 = skill.split("### Step 2:", 1)[1].split("### Step 3:", 1)[0]
        raw = reference("spec.md")
        guide = " ".join(raw.split())
        layout = " ".join(reference("package-layout.md").split())
        review = " ".join(reference("review.md").split())

        self.assertIn("read [references/spec.md](references/spec.md) in full", step2)
        self.assertIn("Read this file in full", guide)
        self.assertIn("Add `SPEC.md` only when every condition holds", guide)
        self.assertNotIn("Add `SPEC.md` only when every condition holds", layout)
        self.assertNotIn("## Exceptional Maintainer Specifications", layout)
        for rule in (
            "core pillars",
            "not frozen",
            "never silently by an agent",
            "corrections made more than once in the same direction",
            "adopted from elsewhere",
            "rewritten from scratch",
            "not the mechanism",
            "locally correct",
            "`SKILL.md` keeps the rules that apply it",
            "with what it rests on",
            "Only what the author keeps enters",
            "Expect most candidates to be cut",
            "validity boundary",
            "do not invent one",
            "has no Why yet",
        ):
            self.assertIn(rule, guide)
        for narrow in (
            "is not a candidate",
            "never write a reason you inferred",
            "ordinary skill execution does not need it",
            "does not qualify",
        ):
            self.assertNotIn(narrow, guide)
        self.assertIn("verify that the author adopted every entry", review)
        admission = guide.split("## Admission Test", 1)[1].split("## Extracting Entries", 1)[0]
        for rule in (
            "Most skills have none",
            "role is complex",
            "a `SPEC.md` would repeat it",
            "no longer visible from its rules",
            "the author's judgment",
            "Size and importance do not make a role complex",
        ):
            self.assertIn(rule, guide if rule == "Most skills have none" else admission)
        self.assertNotIn("Skill importance, size, or complexity does not satisfy the test", guide)
        self.assertNotIn("one screen", guide)
        self.assertIn("A `SPEC.md` is not a summary assembled from the skill's rules", guide)
        self.assertIn("several existing rules read as applications of the candidate", guide)
        self.assertIn("marked as today's application", guide)
        self.assertIn("A `SPEC.md` holds the core of the core, so its entries are few.", guide)
        self.assertIn("Repeated corrections are a good test of what belongs", guide)
        self.assertIn("A draft with numbered rules, source labels, or transcript line numbers is a rule ledger", guide)
        for elsewhere in (
            "reasons for runtime rules",
            "rejected alternatives",
            "open questions",
            "which file owns what",
            "acceptance checklists",
            "where a rule came from",
        ):
            self.assertIn(elsewhere, guide.lower())
        self.assertNotIn("git-hook", raw)
        example = re.search(r"^````markdown\n(.*?)^````$", raw, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(example)
        sections = re.findall(
            r"^## [^\n]+\n(.*?)(?=^## |\Z)", example.group(1), re.MULTILINE | re.DOTALL
        )
        self.assertGreaterEqual(len(sections), 2)
        for body in sections:
            self.assertEqual(1, body.count("**Why:**"), body)
            self.assertTrue(body.rstrip().splitlines()[-1].startswith("**Why:**"), body)
        self.assertIn("[spec.md](spec.md) in full", review)

    def test_spec_md_is_for_skills_whose_role_is_complex(self):
        spec = " ".join(PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8").split())
        readme = " ".join(PACKAGE.joinpath("README.md").read_text(encoding="utf-8").split())
        context = spec.split("## Maintenance Knowledge Travels with the Package", 1)[1]
        self.assertNotIn("The file exists only when explicit, stable requirements", spec)
        self.assertNotIn("ordinary execution does not need them", spec)
        for rule in ("`SPEC.md` is rare", "core pillars"):
            self.assertIn(rule, context.split("**Why:**", 1)[0])
        self.assertIn("role is complex", " ".join(reference("spec.md").split()))
        self.assertNotIn("rare maintainer-only contract", readme)
        self.assertIn("role is complex", readme)

    def test_a_reason_stays_beside_its_rule_only_for_a_named_case(self):
        skill = " ".join(PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8").split())
        spec = " ".join(PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8").split())
        readme = " ".join(PACKAGE.joinpath("README.md").read_text(encoding="utf-8").split())
        guide = " ".join(reference("spec.md").split())
        bounded = skill.split("### Bounded Entry Point", 1)[1].split("### ", 1)[0]

        reasons = " ".join(reference("rule-reasons.md").split())
        # SKILL.md keeps the three requirements; the rest lives in the reference.
        for rule in (
            "Write a rule's or principle's reason down when it tells the reader something, "
            "not when it is plainly obvious or simply the author's choice.",
            "only when you can name a case in which an agent following the rule "
            "without it would act wrongly, written as the clause that settles that case.",
            "Every other reason goes in a file under `references/` behind a why link",
            "never into `SPEC.md`",
            "Before writing, moving, or removing a rule's reason, read "
            "[references/rule-reasons.md](references/rule-reasons.md) in full.",
        ):
            self.assertIn(rule, bounded)
        for rule in (
            "Read this file in full before writing, moving, or removing the reason",
            "Who stated it, when, and where are not part of it",
            "ask rather than write a guess",
            "\"It is just my choice\" is a complete answer",
            "Length does not decide",
            "keeps that clause beside the rule and links the rest",
            "is for someone questioning or changing the rule. A run does not follow it, "
            "so it needs no read condition",
            "`SPEC.md` holds core pillars, not rule reasons",
            "A pillar's Why stays in its entry, and a rule applying that pillar may link it",
            "lives once in a reference file that both link",
            "keeps its reason beside it, because the reason settles which fix the author chooses",
            "The byte cap links its reason, because an agent obeys the number either way",
            "It never creates or grows a `SPEC.md`",
        ):
            self.assertIn(rule, reasons)
        self.assertNotIn("at most its core reason", bounded)
        self.assertNotIn("reason for every rule and principle unless", bounded)
        self.assertNotIn("in a reference or `SPEC.md` behind a link", bounded)
        self.assertNotIn("the reason protects one of its entries", bounded)
        self.assertNotIn("stays out of the runtime text", bounded)
        self.assertNotIn("at most the core reason", spec)
        self.assertIn("a named case", readme)
        self.assertIn("written down when it tells the reader something", readme)
        self.assertNotIn("detailed reasons sit in a reference or `SPEC.md`", readme)
        self.assertIn(
            "Reasons for runtime rules: they sit beside the rule or in a reference behind a "
            "why link; before placing one, read [rule-reasons.md](rule-reasons.md) in full.",
            guide,
        )
        for rule in (
            "A pillar's own Why stays in its entry",
            "written once in a reference file that both link",
            "An entry has a Why when the author's reason tells the reader something",
        ):
            self.assertIn(rule, guide)
        self.assertNotIn("Every entry should have a Why", guide)

    def test_spec_automation_puts_scripts_over_prose_first(self):
        spec = PACKAGE.joinpath("SPEC.md").read_text(encoding="utf-8")
        skill = " ".join(PACKAGE.joinpath("SKILL.md").read_text(encoding="utf-8").split())
        section = spec.split("## Mechanical Work Is a Script\n", 1)[1].split("\n## ", 1)[0]
        lead = " ".join(section.strip().split("\n\n", 1)[0].split())
        flat = " ".join(section.split())

        self.assertIn("is a tested script, not prose", lead)
        self.assertIn("needs judgment", lead)
        self.assertIn("standard library unless the skill's author explicitly allows a dependency", lead)
        self.assertNotIn("when that reduces agent reinterpretation", flat)
        self.assertNotIn("Python and zero dependencies are examples", flat)
        self.assertEqual(1, flat.count("**Why:**"))
        automation = skill.split("### Environment-Native Automation", 1)[1].split("## ", 1)[0]
        self.assertIn("instead of prose that tells the agent to do them", automation)
        self.assertIn(
            "a single existing command is already a script, so name it in the instructions "
            "and do not wrap it in a script file",
            automation,
        )

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
        self.assertIn("a finding is neither actionable nor closable", review)

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
        self.assertIn("it validates eval suites only, not packages", contract)
        intro = " ".join(skill.split("## Authoring Authority", 1)[0].split())
        self.assertIn("none of them validates your target", intro)

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
            "an entry records the net change relative to the last committed or published state",
            "do not record a draft that never left the working tree",
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
        self.assertIn("dates are the default and versions are opted into", spec)

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
        self.assertIn("a script uses only its runtime's standard library", layout)
        self.assertIn("only when the skill's author explicitly allows it", layout)
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
        self.assertIn("These rules stay a short core, not a copy of that skill.", writing)
        for phrase in (
            "does not depend on a host-only feature, a sibling skill, or the source repository",
            "which a sibling skill replaces only when it is installed",
            "must not carry Skill Composer's writing quality",
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
