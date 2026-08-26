#!/usr/bin/env python3
"""Black-box tests for eval-skill.py."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
import unittest


SCRIPT = Path(__file__).with_name("eval-skill.py")


class EvalSkillTest(unittest.TestCase):
    def make_skill(self, root):
        skill = Path(root, "sample-skill")
        skill.mkdir()
        skill.joinpath("SKILL.md").write_text(
            "---\n"
            "name: sample-skill\n"
            'description: "Test fixture skill."\n'
            "---\n\n"
            "# Sample Skill\n",
            encoding="utf-8",
        )
        evals = skill.joinpath("evals")
        evals.mkdir()
        evals.joinpath("evals.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "skill_name": "sample-skill",
                    "evals": [
                        {
                            "id": "returns-requested-artifact",
                            "category": "functional",
                            "prompt": "Create the requested artifact.",
                            "side_effects": "fixture",
                            "assertions": [
                                {
                                    "id": "artifact-created",
                                    "description": "The requested artifact exists.",
                                }
                            ],
                        }
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        return skill

    def run_cli(self, *arguments, env=None):
        return subprocess.run(
            [sys.executable, str(SCRIPT), *map(str, arguments)],
            capture_output=True,
            text=True,
            env=env,
        )

    def make_auxiliary_skill(self, root, name="other-skill"):
        skill = Path(root, name)
        skill.mkdir()
        skill.joinpath("SKILL.md").write_text(
            "---\n"
            f"name: {name}\n"
            f'description: "Auxiliary {name} fixture."\n'
            "---\n\n"
            f"# {name}\n",
            encoding="utf-8",
        )
        return skill

    def make_fake_target(self, root, target):
        bin_dir = Path(root, "bin")
        bin_dir.mkdir(exist_ok=True)
        executable = bin_dir / target
        executable.write_text(
            """#!/usr/bin/env python3
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid

target = Path(sys.argv[0]).name
arguments = sys.argv[1:]
cwd = Path.cwd()
schema_grader = "--json-schema" in arguments or "--output-schema" in arguments

child_marker = os.environ.get("FAKE_CHILD_MARKER")
if child_marker:
    if os.environ.get("FAKE_PARTIAL_ARTIFACT"):
        cwd.joinpath("partial-artifact.txt").write_text(
            "created before timeout\\n", encoding="utf-8"
        )
    if target == "grok" and os.environ.get("FAKE_TIMEOUT_EVENT"):
        print(json.dumps({
            "type": "assistant",
            "session_id": "partial-session",
            "message": {
                "content": [{
                    "type": "tool_use",
                    "name": "read_file",
                    "input": {"target_file": "SKILL.md"},
                }],
                "stop_reason": "tool_use",
            },
        }), flush=True)
        print(json.dumps({
            "type": "user",
            "session_id": "partial-session",
            "message": {
                "content": [{
                    "type": "tool_result",
                    "tool_use_id": "read-file-call",
                    "content": "permission denied",
                    "is_error": True,
                }],
            },
        }), flush=True)
    subprocess.Popen([
        sys.executable,
        "-c",
        "import sys, time; time.sleep(0.5); "
        "open(sys.argv[1], 'w').write('still running')",
        child_marker,
    ])
    time.sleep(30)

detached_pipe_seconds = os.environ.get("FAKE_DETACHED_PIPE_SECONDS")
if detached_pipe_seconds:
    subprocess.Popen(
        [
            sys.executable,
            "-c",
            "import sys, time; time.sleep(float(sys.argv[1]))",
            detached_pipe_seconds,
        ],
        start_new_session=True,
    )
    time.sleep(30)

def option_value(name):
    index = arguments.index(name)
    return arguments[index + 1]

if target == "codex":
    prompt = arguments[-1]
else:
    prompt = option_value("-p")
is_grader = schema_grader or prompt.startswith(
    "You are the independent grader for one completed skill evaluation."
)
candidate_delay = os.environ.get("FAKE_CANDIDATE_DELAY_SECONDS")
if candidate_delay and not is_grader:
    time.sleep(float(candidate_delay))
grader_delay = os.environ.get("FAKE_GRADER_DELAY_SECONDS")
if grader_delay and is_grader:
    time.sleep(float(grader_delay))

host_directory = {
    "claude": ".claude",
    "codex": ".agents",
    "grok": ".grok",
}[target]
staged_skill = cwd / host_directory / "skills" / "sample-skill"
record = {
    "target": target,
    "euid": os.geteuid(),
    "arguments": arguments,
    "cwd": str(cwd),
    "staged_skill": str(staged_skill),
    "grader": is_grader,
    "prompt": prompt,
    "skill_staged": staged_skill.joinpath("SKILL.md").is_file(),
    "skill_text": (
        staged_skill.joinpath("SKILL.md").read_text(encoding="utf-8")
        if staged_skill.joinpath("SKILL.md").is_file()
        else None
    ),
    "top_level_skill_staged": cwd.joinpath("sample-skill", "SKILL.md").is_file(),
    "evals_staged": staged_skill.joinpath("evals").exists(),
    "other_staged": cwd.joinpath(
        host_directory, "skills", "other-skill", "SKILL.md"
    ).is_file(),
    "assertion_leaked": (
        "artifact-created" in prompt
        or "The requested artifact exists" in prompt
        or "should_trigger" in prompt
    ),
    "disable_autoupdater": os.environ.get("GROK_DISABLE_AUTOUPDATER"),
    "skill_named_directory_visible": cwd.joinpath(
        "candidate", "sample-skill", "notes.txt"
    ).is_file(),
    "after_state_lists_skill_named_file": (
        "sample-skill/notes.txt" in json.loads(
            cwd.joinpath("after.json").read_text(encoding="utf-8")
        )
        if cwd.joinpath("after.json").is_file()
        else None
    ),
    "sandbox_toml": (
        cwd.joinpath(".grok", "sandbox.toml").read_text(encoding="utf-8")
        if cwd.joinpath(".grok", "sandbox.toml").is_file()
        else None
    ),
}
with Path(os.environ["FAKE_TARGET_LOG"]).open("a", encoding="utf-8") as stream:
    stream.write(json.dumps(record) + "\\n")

mutation_target = os.environ.get("FAKE_MUTATE_SOURCE_SKILL")
mutation_marker = os.environ.get("FAKE_MUTATION_MARKER")
if mutation_target and mutation_marker and not is_grader:
    marker = Path(mutation_marker)
    if not marker.exists():
        Path(mutation_target).write_text("mutated during run\\n", encoding="utf-8")
        marker.write_text("mutated\\n", encoding="utf-8")

session_id = (
    os.environ.get("FAKE_FIXED_GRADER_SESSION") if is_grader else None
) or os.environ.get("FAKE_FIXED_SESSION") or str(uuid.uuid4())
grader_status = "invalid" if os.environ.get("FAKE_BAD_GRADER") else "pass"
grader_evidence = "candidate/artifact.txt exists in the graded snapshot"
if (
    is_grader
    and os.environ.get("FAKE_PROGRESS_GRADER_UNLESS_FINAL")
    and "Complete every inspection before emitting the structured object." not in prompt
):
    grader_status = "unknown"
    grader_evidence = "Starting read-only inspection of the candidate snapshot."
assertion_result = {
    "assertions": [
        {
            "id": "artifact-created",
            "status": grader_status,
            "evidence": grader_evidence,
        }
    ]
}
if is_grader and os.environ.get("FAKE_OMIT_ASSERTIONS_UNLESS_COUNTED"):
    required_sentence = (
        "The assertions array must contain exactly 2 results in this order: "
        "artifact-created, artifact-preserved."
    )
    if required_sentence in prompt:
        assertion_result["assertions"].append({
            "id": "artifact-preserved",
            "status": "pass",
            "evidence": "candidate/artifact.txt retained the expected content",
        })

if is_grader:
    if target == "claude":
        print(json.dumps({
            "type": "result",
            "subtype": "success",
            "is_error": False,
            "session_id": session_id,
            "structured_output": assertion_result,
        }))
    elif target == "codex":
        output_path = Path(option_value("-o"))
        output_path.write_text(json.dumps(assertion_result), encoding="utf-8")
        print(json.dumps({"type": "thread.started", "thread_id": session_id}))
        print(json.dumps({
            "type": "item.completed",
            "item": {
                "id": "grader-message",
                "type": "agent_message",
                "text": json.dumps(assertion_result),
            },
        }))
        print(json.dumps({"type": "turn.completed", "usage": {}}))
    else:
        grok_grader_text = json.dumps(assertion_result)
        if os.environ.get("FAKE_FENCED_GROK_GRADER"):
            grok_grader_text = f"```json\\n{grok_grader_text}\\n```"
        if os.environ.get("FAKE_PROSE_FENCED_GROK_GRADER"):
            grok_grader_text = (
                "Inspection complete.\\n"
                f"```json\\n{grok_grader_text}\\n```"
            )
        if os.environ.get("FAKE_GROK_ASSISTANT_FINAL"):
            print(json.dumps({
                "type": "assistant",
                "session_id": session_id,
                "message": {
                    "content": [
                        {"type": "thinking", "thinking": "grading"},
                        {"type": "text", "text": grok_grader_text},
                    ],
                    "stop_reason": "end_turn",
                },
            }))
            print(json.dumps({
                "type": "result",
                "subtype": "success",
                "is_error": False,
                "session_id": session_id,
                "stop_reason": "end_turn",
                "duration_ms": 123,
                "usage": {"input_tokens": 10, "output_tokens": 5},
                "result": "",
            }))
        else:
            print(json.dumps({
                "type": "result",
                "subtype": "success",
                "is_error": False,
                "session_id": session_id,
                "stop_reason": "end_turn",
                "duration_ms": 123,
                "usage": {"input_tokens": 10, "output_tokens": 5},
                "result": (
                    "" if os.environ.get("FAKE_EMPTY_GROK_GRADER")
                    else grok_grader_text
                ),
            }))
    raise SystemExit(0)

cwd.joinpath("artifact.txt").write_text("created by candidate\\n", encoding="utf-8")
if os.environ.get("FAKE_WRITE_SKILL_NAMED_DIRECTORY"):
    cwd.joinpath("sample-skill").mkdir(exist_ok=True)
    cwd.joinpath("sample-skill", "notes.txt").write_text(
        "candidate notes\\n", encoding="utf-8"
    )
should_activate = "Create a skill" in prompt
explore_seconds = os.environ.get("FAKE_EXPLORE_BEFORE_DECIDING_SECONDS")
if target == "claude":
    print(json.dumps({
        "type": "system",
        "subtype": "init",
        "session_id": session_id,
        "tools": ["Skill", "Read", "Edit"],
        "skills": [] if os.environ.get("FAKE_NO_CATALOG") else ["sample-skill"],
        "slash_commands": [] if os.environ.get("FAKE_NO_CATALOG") else ["sample-skill"],
    }))
    if explore_seconds:
        print(json.dumps({
            "type": "assistant",
            "session_id": session_id,
            "message": {
                "content": [{
                    "type": "tool_use",
                    "name": "Read",
                    "input": {"file_path": str(cwd / "README.md")},
                }],
                "stop_reason": "tool_use",
            },
        }), flush=True)
        time.sleep(float(explore_seconds))
    if should_activate:
        print(json.dumps({
            "type": "assistant",
            "session_id": session_id,
            "message": {
                "content": [{
                    "type": "tool_use",
                    "name": "Skill",
                    "input": {"skill": "sample-skill"},
                }],
            },
        }), flush=True)
        if os.environ.get("FAKE_SLEEP_AFTER_CLAUDE_ACTIVATION"):
            time.sleep(float(os.environ["FAKE_SLEEP_AFTER_CLAUDE_ACTIVATION"]))
    print(json.dumps({
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "session_id": session_id,
        "stop_reason": "end_turn",
        "duration_ms": 123,
        "usage": {"input_tokens": 10, "output_tokens": 5},
        "result": "candidate completed",
    }))
elif target == "codex":
    print(json.dumps({"type": "thread.started", "thread_id": session_id}))
    print(json.dumps({
        "type": "item.completed",
        "item": {
            "id": "candidate-message",
            "type": "agent_message",
            "text": "candidate completed",
        },
    }))
    print(json.dumps({"type": "turn.completed", "usage": {}}))
else:
    print(json.dumps({
        "type": "system",
        "subtype": "init",
        "session_id": session_id,
        "skills": [] if os.environ.get("FAKE_NO_CATALOG") else ["sample-skill"],
        "slash_commands": [] if os.environ.get("FAKE_NO_CATALOG") else ["sample-skill"],
        "tools": ["read_file", "search_replace"],
    }))
    if explore_seconds:
        print(json.dumps({
            "type": "assistant",
            "session_id": session_id,
            "message": {
                "content": [{
                    "type": "tool_use",
                    "name": "list_dir",
                    "input": {"target_directory": str(cwd)},
                }],
                "stop_reason": "tool_use",
            },
        }), flush=True)
        time.sleep(float(explore_seconds))
    if should_activate:
        print(json.dumps({
            "type": "assistant",
            "session_id": session_id,
            "message": {
                "content": [{
                    "type": "tool_use",
                    "name": "read_file",
                    "input": {
                        "target_file": str(staged_skill / "SKILL.md"),
                    },
                }],
                "stop_reason": "tool_use",
            },
        }), flush=True)
        if os.environ.get("FAKE_SLEEP_AFTER_GROK_ACTIVATION"):
            time.sleep(float(os.environ["FAKE_SLEEP_AFTER_GROK_ACTIVATION"]))
    print(json.dumps({
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "session_id": session_id,
        "stop_reason": "end_turn",
        "duration_ms": 123,
        "usage": {"input_tokens": 10, "output_tokens": 5},
        "result": "candidate completed",
    }))
    if os.environ.get("FAKE_DELETE_GROK_SANDBOX_AFTER_CANDIDATE"):
        cwd.joinpath(".grok", "sandbox.toml").unlink()
""",
            encoding="utf-8",
        )
        executable.chmod(0o755)
        return bin_dir

    def fake_target_environment(self, bin_dir, log_path):
        environment = os.environ.copy()
        environment["PATH"] = str(bin_dir) + os.pathsep + environment["PATH"]
        environment["FAKE_TARGET_LOG"] = str(log_path)
        return environment

    def read_target_log(self, path):
        return [
            json.loads(line)
            for line in Path(path).read_text(encoding="utf-8").splitlines()
        ]

    def report_path_from(self, result):
        lines = [
            line
            for line in result.stdout.splitlines()
            if line.startswith("REPORT ")
        ]
        self.assertEqual(1, len(lines), result.stdout)
        label, value = lines[0].split(" path=", 1)
        self.assertEqual("REPORT", label)
        return Path(json.loads(value))

    def read_evals(self, skill):
        path = skill / "evals" / "evals.json"
        return path, json.loads(path.read_text(encoding="utf-8"))

    def write_trigger_evals(self, skill):
        skill.joinpath("evals", "trigger-eval.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "skill_name": "sample-skill",
                    "queries": [
                        {
                            "id": "create-a-skill",
                            "query": "Create a skill for release notes.",
                            "should_trigger": True,
                        },
                        {
                            "id": "install-a-skill",
                            "query": (
                                "Install package https://example.invalid/acme/"
                                "agent-skill into Codex."
                            ),
                            "should_trigger": False,
                        },
                    ],
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def test_check_accepts_a_valid_skill_and_eval_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)

            result = self.run_cli("check", skill)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            "OK sample-skill: eval_contract=valid functional=1 trigger=0\n",
            result.stdout,
        )
        self.assertEqual("", result.stderr)

    def test_list_reports_case_ids_without_starting_a_target(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            self.write_trigger_evals(skill)

            result = self.run_cli("list", skill)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            "functional\treturns-requested-artifact\n"
            "trigger\tcreate-a-skill\tshould_trigger=true\n"
            "trigger\tinstall-a-skill\tshould_trigger=false\n",
            result.stdout,
        )

    def test_run_one_executes_exactly_one_case(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            self.write_trigger_evals(skill)
            log_path = Path(temp_dir, "claude.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "claude")
            environment = self.fake_target_environment(bin_dir, log_path)

            result = self.run_cli(
                "run-one",
                skill,
                "create-a-skill",
                "--target",
                "claude",
                env=environment,
            )
            report_path = self.report_path_from(result)
            self.addCleanup(report_path.unlink, missing_ok=True)
            records = self.read_target_log(log_path)

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertEqual(1, len(records), records)
        self.assertIn("PASS create-a-skill iteration=1", result.stdout)
        self.assertIn("SUMMARY pass=1 fail=0 unknown=0", result.stdout)

    def test_run_all_stops_after_the_first_non_green_case_by_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            second = dict(document["evals"][0])
            second["id"] = "returns-second-artifact"
            document["evals"].append(second)
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_BAD_GRADER"] = "1"

            result = self.run_cli(
                "run-all", skill, "--target", "grok", env=environment
            )
            report_path = self.report_path_from(result)
            self.addCleanup(report_path.unlink, missing_ok=True)
            records = self.read_target_log(log_path)

        self.assertEqual(1, result.returncode)
        self.assertEqual(2, len(records), records)
        self.assertIn("UNKNOWN returns-requested-artifact", result.stdout)
        self.assertNotIn("returns-second-artifact", result.stdout)
        self.assertIn("SUMMARY pass=0 fail=0 unknown=1", result.stdout)

    def test_run_all_keep_going_runs_every_case(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            second = dict(document["evals"][0])
            second["id"] = "returns-second-artifact"
            document["evals"].append(second)
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_BAD_GRADER"] = "1"

            result = self.run_cli(
                "run-all",
                skill,
                "--target",
                "grok",
                "--keep-going",
                env=environment,
            )
            report_path = self.report_path_from(result)
            self.addCleanup(report_path.unlink, missing_ok=True)
            records = self.read_target_log(log_path)

        self.assertEqual(1, result.returncode)
        self.assertEqual(4, len(records), records)
        self.assertIn("UNKNOWN returns-requested-artifact", result.stdout)
        self.assertIn("UNKNOWN returns-second-artifact", result.stdout)
        self.assertIn("SUMMARY pass=0 fail=0 unknown=2", result.stdout)

    def test_run_one_writes_a_sanitized_inspectable_report_automatically(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)

            result = self.run_cli(
                "run-one",
                skill,
                "returns-requested-artifact",
                "--target",
                "grok",
                env=environment,
            )
            report_path = self.report_path_from(result)
            self.addCleanup(report_path.unlink, missing_ok=True)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            report_mode = report_path.stat().st_mode & 0o777
            inspected = self.run_cli("inspect", report_path)

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertEqual(0, inspected.returncode, inspected.stderr)
        self.assertEqual(0o600, report_mode)
        self.assertEqual("skill-eval-run", report["kind"])
        self.assertEqual("run-one", report["run"]["scope"])
        self.assertEqual("grok", report["target"]["name"])
        self.assertEqual("grok-4.6", report["target"]["model"])
        self.assertEqual("high", report["target"]["reasoning_effort"])
        self.assertEqual("pass", report["cases"][0]["status"])
        phases = report["cases"][0]["iterations"][0]["phases"]
        self.assertEqual({"candidate", "grader"}, set(phases))
        serialized = json.dumps(report)
        for secret in (
            "prompt",
            "assertions",
            "evidence",
            "artifact-created",
            "candidate completed",
        ):
            self.assertNotIn(secret, serialized)
        self.assertIn(
            "CASE returns-requested-artifact status=pass", inspected.stdout
        )
        self.assertIn("PHASE candidate status=complete", inspected.stdout)
        self.assertIn("PHASE grader status=complete", inspected.stdout)

    def test_inspect_rejects_malformed_case_records_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            report_path = Path(temp_dir, "report.json")
            report_path.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "kind": "skill-eval-run",
                        "skill": {
                            "name": "sample-skill",
                            "source_path": "/tmp/sample-skill",
                            "package_sha256": "0" * 64,
                        },
                        "target": {
                            "name": "grok",
                            "model": "grok-4.6",
                            "reasoning_effort": "high",
                        },
                        "run": {
                            "scope": "run-one",
                            "selected_case_ids": ["case"],
                            "repeat": 1,
                            "timeout_seconds": 10,
                            "fail_fast": True,
                            "additional_skills": [],
                        },
                        "cases": [{}],
                        "summary": {"pass": 1, "fail": 0, "unknown": 0},
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            result = self.run_cli("inspect", report_path)

        self.assertEqual(2, result.returncode)
        self.assertIn("invalid report case results", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_run_all_uses_one_frozen_skill_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            second = dict(document["evals"][0])
            second["id"] = "returns-second-artifact"
            document["evals"].append(second)
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            original = skill.joinpath("SKILL.md").read_text(encoding="utf-8")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_MUTATE_SOURCE_SKILL"] = str(skill / "SKILL.md")
            environment["FAKE_MUTATION_MARKER"] = str(Path(temp_dir, "mutated"))

            result = self.run_cli(
                "run-all",
                skill,
                "--target",
                "grok",
                "--keep-going",
                env=environment,
            )
            report_path = self.report_path_from(result)
            self.addCleanup(report_path.unlink, missing_ok=True)
            records = self.read_target_log(log_path)
            candidate_records = [
                record for record in records if not record["grader"]
            ]

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertEqual(2, len(candidate_records), candidate_records)
        self.assertEqual(
            [original, original],
            [record["skill_text"] for record in candidate_records],
        )

    def test_rerun_reuses_a_reported_case_but_refuses_package_drift(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            self.write_trigger_evals(skill)
            log_path = Path(temp_dir, "claude.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "claude")
            environment = self.fake_target_environment(bin_dir, log_path)

            first = self.run_cli(
                "run-one",
                skill,
                "create-a-skill",
                "--target",
                "claude",
                env=environment,
            )
            first_report = self.report_path_from(first)
            self.addCleanup(first_report.unlink, missing_ok=True)
            rerun = self.run_cli("rerun", first_report, env=environment)
            rerun_report = self.report_path_from(rerun)
            self.addCleanup(rerun_report.unlink, missing_ok=True)
            before_drift = self.read_target_log(log_path)
            skill.joinpath("SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: Changed.\n---\n",
                encoding="utf-8",
            )
            drifted = self.run_cli("rerun", first_report, env=environment)
            after_drift = self.read_target_log(log_path)

        self.assertEqual(0, first.returncode, first.stderr + first.stdout)
        self.assertEqual(0, rerun.returncode, rerun.stderr + rerun.stdout)
        self.assertEqual(2, len(before_drift), before_drift)
        self.assertEqual(2, drifted.returncode)
        self.assertIn("package changed since the recorded run", drifted.stderr)
        self.assertEqual(before_drift, after_drift)

    def test_check_requires_an_integer_schema_version(self):
        for invalid_version in (True, 1.0):
            with self.subTest(invalid_version=invalid_version):
                with tempfile.TemporaryDirectory() as temp_dir:
                    skill = self.make_skill(temp_dir)
                    path, document = self.read_evals(skill)
                    document["schema_version"] = invalid_version
                    path.write_text(
                        json.dumps(document) + "\n", encoding="utf-8"
                    )

                    result = self.run_cli("check", skill)

                self.assertEqual(2, result.returncode)
                self.assertIn("schema_version must be 1", result.stderr)

    def test_check_rejects_an_ownerless_deictic_negative_trigger(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            self.write_trigger_evals(skill)
            path = skill / "evals" / "trigger-eval.json"
            document = json.loads(path.read_text(encoding="utf-8"))
            document["queries"][1]["query"] = "Install this skill from GitHub."
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")

            result = self.run_cli("check", skill)

        self.assertEqual(2, result.returncode)
        self.assertIn("deictic owner needs a fixture or competing skill", result.stderr)

    def test_check_rejects_a_skill_without_evaluation_cases(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"] = []
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")

            result = self.run_cli("check", skill)

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn("no evaluation cases found", result.stderr)

    def test_check_rejects_a_functional_case_without_assertions(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            del document["evals"][0]["assertions"]
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")

            result = self.run_cli("check", skill)

        self.assertEqual(2, result.returncode)
        self.assertEqual("", result.stdout)
        self.assertIn(
            "evals.json: eval returns-requested-artifact assertions must be a "
            "non-empty array",
            result.stderr,
        )

    def test_check_rejects_unknown_manifest_fields(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"][0]["expected_output"] = "A stale schema field"
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")

            result = self.run_cli("check", skill)

        self.assertEqual(2, result.returncode)
        self.assertIn(
            "eval returns-requested-artifact has unknown fields: expected_output",
            result.stderr,
        )

    def test_check_reports_malformed_enum_fields_without_a_traceback(self):
        for field in ("category", "side_effects", "skill_mode"):
            with self.subTest(field=field):
                with tempfile.TemporaryDirectory() as temp_dir:
                    skill = self.make_skill(temp_dir)
                    path, document = self.read_evals(skill)
                    document["evals"][0][field] = ["not", "a", "string"]
                    path.write_text(
                        json.dumps(document) + "\n", encoding="utf-8"
                    )

                    result = self.run_cli("check", skill)

                self.assertEqual(2, result.returncode)
                self.assertEqual("", result.stdout)
                self.assertNotIn("Traceback", result.stderr)
                self.assertIn(field, result.stderr)

    def test_check_enforces_functional_category_semantics(self):
        variants = (
            (
                {"category": "baseline", "skill_mode": "enabled"},
                "baseline cases must set skill_mode to 'disabled'",
            ),
            (
                {"category": "functional", "skill_mode": "disabled"},
                "only baseline cases may disable the evaluated skill",
            ),
            (
                {"category": "coexistence"},
                "coexistence cases must declare additional_skills",
            ),
            (
                {"category": "isolation", "additional_skills": ["other-skill"]},
                "isolation cases must not declare additional_skills",
            ),
        )
        for changes, message in variants:
            with self.subTest(changes=changes):
                with tempfile.TemporaryDirectory() as temp_dir:
                    skill = self.make_skill(temp_dir)
                    path, document = self.read_evals(skill)
                    document["evals"][0].update(changes)
                    path.write_text(
                        json.dumps(document) + "\n", encoding="utf-8"
                    )

                    result = self.run_cli("check", skill)

                self.assertEqual(2, result.returncode)
                self.assertIn(message, result.stderr)

    def test_check_accepts_balanced_trigger_queries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            self.write_trigger_evals(skill)

            result = self.run_cli("check", skill)

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            "OK sample-skill: eval_contract=valid functional=1 trigger=2\n",
            result.stdout,
        )

    def test_check_resolves_fixture_files_inside_the_eval_package(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            fixtures = skill / "evals" / "fixtures"
            fixtures.mkdir()
            fixtures.joinpath("input.txt").write_text("fixture\n", encoding="utf-8")
            path, document = self.read_evals(skill)
            document["evals"][0]["files"] = ["input.txt"]
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")

            valid = self.run_cli("check", skill)

            document["evals"][0]["files"] = ["../evals.json"]
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            escaped = self.run_cli("check", skill)

        self.assertEqual(0, valid.returncode, valid.stderr)
        self.assertEqual(2, escaped.returncode)
        self.assertIn("fixture path must stay inside evals/fixtures", escaped.stderr)

    @unittest.skipUnless(hasattr(os, "symlink"), "symbolic links unavailable")
    def test_check_rejects_symlinks_before_staging_the_skill(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            outside = Path(temp_dir, "outside.txt")
            outside.write_text("caller-owned data\n", encoding="utf-8")
            skill.joinpath("leak.txt").symlink_to(outside)

            result = self.run_cli("check", skill)

        self.assertEqual(2, result.returncode)
        self.assertIn("symbolic links are not supported: leak.txt", result.stderr)

    def test_run_executes_a_functional_case_in_an_isolated_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            fixtures = skill / "evals" / "fixtures"
            fixtures.mkdir()
            fixtures.joinpath("input.txt").write_text(
                "fixture input\n", encoding="utf-8"
            )
            path, document = self.read_evals(skill)
            document["evals"][0]["files"] = ["input.txt"]
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            adapter = Path(temp_dir, "passing-adapter.py")
            adapter.write_text(
                "import json\n"
                "from pathlib import Path\n"
                "import sys\n"
                "request = json.load(sys.stdin)\n"
                "skill = Path(request['skill']['path'])\n"
                "assert not skill.joinpath('evals').exists()\n"
                "assert skill.parent == Path.cwd()\n"
                "inputs = request['case']['inputs']\n"
                "assert [item['name'] for item in inputs] == ['input.txt']\n"
                "assert Path(inputs[0]['path']).parent == Path.cwd() / 'inputs'\n"
                "assert Path(inputs[0]['path']).read_text() == 'fixture input\\n'\n"
                "json.dump({\n"
                "    'protocol_version': 1,\n"
                "    'case_id': request['case']['id'],\n"
                "    'session_id': 'fresh-session-1',\n"
                "    'fresh_session': True,\n"
                "    'assertions': [{\n"
                "        'id': 'artifact-created',\n"
                "        'status': 'pass',\n"
                "        'evidence': 'artifact.txt exists',\n"
                "    }],\n"
                "}, sys.stdout)\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                "run", skill, "--", sys.executable, adapter
            )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            "PASS returns-requested-artifact iteration=1\n"
            "  PASS artifact-created: artifact.txt exists\n"
            "SUMMARY pass=1 fail=0 unknown=0\n",
            result.stdout,
        )
        self.assertEqual("", result.stderr)

    def test_run_grades_trigger_observations_against_the_manifest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"] = []
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            self.write_trigger_evals(skill)
            adapter = Path(temp_dir, "trigger-adapter.py")
            adapter.write_text(
                "import json\n"
                "import sys\n"
                "request = json.load(sys.stdin)\n"
                "case_id = request['case']['id']\n"
                "observed = {\n"
                "    'create-a-skill': True,\n"
                "    'install-a-skill': False,\n"
                "}[case_id]\n"
                "json.dump({\n"
                "    'protocol_version': 1,\n"
                "    'case_id': case_id,\n"
                "    'session_id': 'session-' + case_id,\n"
                "    'fresh_session': True,\n"
                "    'activated': observed,\n"
                "    'evidence': 'target trace recorded activation state',\n"
                "}, sys.stdout)\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                "run", skill, "--", sys.executable, adapter
            )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual(
            "PASS create-a-skill iteration=1\n"
            "  ACTIVATION expected=true observed=true: target trace recorded "
            "activation state\n"
            "PASS install-a-skill iteration=1\n"
            "  ACTIVATION expected=false observed=false: target trace recorded "
            "activation state\n"
            "SUMMARY pass=2 fail=0 unknown=0\n",
            result.stdout,
        )

    def test_run_stages_declared_trigger_fixture_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"] = []
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            self.write_trigger_evals(skill)
            trigger_path = skill / "evals" / "trigger-eval.json"
            trigger = json.loads(trigger_path.read_text(encoding="utf-8"))
            trigger["queries"][0]["files"] = ["trigger/context.txt"]
            trigger_path.write_text(
                json.dumps(trigger) + "\n", encoding="utf-8"
            )
            fixture = skill / "evals" / "fixtures" / "trigger" / "context.txt"
            fixture.parent.mkdir(parents=True)
            fixture.write_text("realistic project context\n", encoding="utf-8")
            adapter = Path(temp_dir, "trigger-fixture-adapter.py")
            adapter.write_text(
                "import json\n"
                "from pathlib import Path\n"
                "import sys\n"
                "request = json.load(sys.stdin)\n"
                "inputs = request['case']['inputs']\n"
                "assert [item['name'] for item in inputs] == ['trigger/context.txt']\n"
                "assert Path(inputs[0]['path']).read_text() == "
                "'realistic project context\\n'\n"
                "json.dump({\n"
                "    'protocol_version': 1,\n"
                "    'case_id': request['case']['id'],\n"
                "    'session_id': 'trigger-fixture-session',\n"
                "    'fresh_session': True,\n"
                "    'activated': True,\n"
                "    'evidence': 'target trace recorded activation',\n"
                "}, sys.stdout)\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                "run",
                skill,
                "--case",
                "create-a-skill",
                "--",
                sys.executable,
                adapter,
            )

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("PASS create-a-skill", result.stdout)

    def test_run_keeps_failed_and_unverifiable_results_non_green(self):
        responses = {
            "fail": {
                "protocol_version": 1,
                "case_id": "returns-requested-artifact",
                "session_id": "fresh-session",
                "fresh_session": True,
                "assertions": [
                    {
                        "id": "artifact-created",
                        "status": "fail",
                        "evidence": "artifact.txt is absent",
                    }
                ],
            },
            "unknown": {
                "protocol_version": 1,
                "case_id": "returns-requested-artifact",
                "session_id": "reused-session",
                "fresh_session": False,
            },
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            for expected, response in responses.items():
                with self.subTest(expected=expected):
                    adapter = Path(temp_dir, f"{expected}-adapter.py")
                    adapter.write_text(
                        "import json\n"
                        "import sys\n"
                        f"json.dump({response!r}, sys.stdout)\n",
                        encoding="utf-8",
                    )

                    result = self.run_cli(
                        "run", skill, "--", sys.executable, adapter
                    )

                    self.assertEqual(1, result.returncode)
                    self.assertTrue(
                        result.stdout.startswith(
                            f"{expected.upper()} returns-requested-artifact "
                            "iteration=1"
                        ),
                        result.stdout,
                    )
                    self.assertIn(
                        f"SUMMARY pass=0 fail={int(expected == 'fail')} "
                        f"unknown={int(expected == 'unknown')}",
                        result.stdout,
                    )

    def test_run_turns_malformed_assertion_fields_into_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            adapter = Path(temp_dir, "malformed-adapter.py")
            adapter.write_text(
                "import json\n"
                "import sys\n"
                "request = json.load(sys.stdin)\n"
                "json.dump({\n"
                "    'protocol_version': 1,\n"
                "    'case_id': request['case']['id'],\n"
                "    'session_id': 'malformed-session',\n"
                "    'fresh_session': True,\n"
                "    'assertions': [{\n"
                "        'id': ['not', 'a', 'string'],\n"
                "        'status': ['not', 'a', 'string'],\n"
                "        'evidence': 'malformed fields',\n"
                "    }],\n"
                "}, sys.stdout)\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                "run", skill, "--", sys.executable, adapter
            )

        self.assertEqual(1, result.returncode)
        self.assertEqual("", result.stderr)
        self.assertIn(
            "UNKNOWN returns-requested-artifact iteration=1", result.stdout
        )
        self.assertIn("invalid adapter response", result.stdout)
        self.assertIn("SUMMARY pass=0 fail=0 unknown=1", result.stdout)

    def test_run_repeats_each_case_in_a_new_adapter_process(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            adapter = Path(temp_dir, "repeating-adapter.py")
            adapter.write_text(
                "import json\n"
                "import sys\n"
                "request = json.load(sys.stdin)\n"
                "iteration = request['run']['iteration']\n"
                "json.dump({\n"
                "    'protocol_version': 1,\n"
                "    'case_id': request['case']['id'],\n"
                "    'session_id': f'fresh-session-{iteration}',\n"
                "    'fresh_session': True,\n"
                "    'assertions': [{\n"
                "        'id': 'artifact-created',\n"
                "        'status': 'pass',\n"
                "        'evidence': f'iteration {iteration}',\n"
                "    }],\n"
                "}, sys.stdout)\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                "run",
                skill,
                "--repeat",
                "2",
                "--",
                sys.executable,
                adapter,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("PASS returns-requested-artifact iteration=1", result.stdout)
        self.assertIn("PASS returns-requested-artifact iteration=2", result.stdout)
        self.assertIn("SUMMARY pass=2 fail=0 unknown=0", result.stdout)

    def test_run_aggregates_repeated_trigger_cases_by_strict_majority(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"] = []
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            self.write_trigger_evals(skill)
            counter = Path(temp_dir, "counter.txt")
            adapter = Path(temp_dir, "trigger-rate-adapter.py")
            adapter.write_text(
                "import json\n"
                "from pathlib import Path\n"
                "import sys\n"
                f"counter = Path({str(counter)!r})\n"
                "iteration = int(counter.read_text()) if counter.exists() else 0\n"
                "counter.write_text(str(iteration + 1))\n"
                "request = json.load(sys.stdin)\n"
                "json.dump({\n"
                "    'protocol_version': 1,\n"
                "    'case_id': request['case']['id'],\n"
                "    'session_id': f'trigger-session-{iteration}',\n"
                "    'fresh_session': True,\n"
                "    'activated': [True, False, True][iteration],\n"
                "    'evidence': f'observed activation={ [True, False, True][iteration] }',\n"
                "}, sys.stdout)\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                "run",
                skill,
                "--case",
                "create-a-skill",
                "--repeat",
                "3",
                "--",
                sys.executable,
                adapter,
            )

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("FAIL create-a-skill iteration=2", result.stdout)
        self.assertIn(
            "TRIGGER_RATE create-a-skill triggered=2/3 rate=0.667 "
            "expected=true threshold=0.5 status=pass",
            result.stdout,
        )
        self.assertIn("SUMMARY pass=1 fail=0 unknown=0", result.stdout)

    def test_run_keeps_an_undecidable_trigger_rate_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"] = []
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            self.write_trigger_evals(skill)
            counter = Path(temp_dir, "counter.txt")
            adapter = Path(temp_dir, "unknown-trigger-rate-adapter.py")
            adapter.write_text(
                "import json\n"
                "from pathlib import Path\n"
                "import sys\n"
                f"counter = Path({str(counter)!r})\n"
                "iteration = int(counter.read_text()) if counter.exists() else 0\n"
                "counter.write_text(str(iteration + 1))\n"
                "request = json.load(sys.stdin)\n"
                "states = [True, False, None]\n"
                "state = states[iteration]\n"
                "json.dump({\n"
                "    'protocol_version': 1,\n"
                "    'case_id': request['case']['id'],\n"
                "    'session_id': f'trigger-session-{iteration}',\n"
                "    'fresh_session': state is not None,\n"
                "    'activated': bool(state),\n"
                "    'evidence': 'target observation',\n"
                "}, sys.stdout)\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                "run",
                skill,
                "--case",
                "create-a-skill",
                "--repeat",
                "3",
                "--",
                sys.executable,
                adapter,
            )

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "TRIGGER_RATE create-a-skill triggered=1/3 rate=0.333..0.667 "
            "expected=true threshold=0.5 status=unknown",
            result.stdout,
        )
        self.assertIn("SUMMARY pass=0 fail=0 unknown=1", result.stdout)

    def test_run_marks_a_reused_target_session_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            adapter = Path(temp_dir, "reused-session-adapter.py")
            adapter.write_text(
                "import json\n"
                "import sys\n"
                "request = json.load(sys.stdin)\n"
                "json.dump({\n"
                "    'protocol_version': 1,\n"
                "    'case_id': request['case']['id'],\n"
                "    'session_id': 'same-target-session',\n"
                "    'fresh_session': True,\n"
                "    'assertions': [{\n"
                "        'id': 'artifact-created',\n"
                "        'status': 'pass',\n"
                "        'evidence': 'adapter claimed a pass',\n"
                "    }],\n"
                "}, sys.stdout)\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                "run",
                skill,
                "--repeat",
                "2",
                "--",
                sys.executable,
                adapter,
            )

        self.assertEqual(1, result.returncode)
        self.assertIn("PASS returns-requested-artifact iteration=1", result.stdout)
        self.assertIn("UNKNOWN returns-requested-artifact iteration=2", result.stdout)
        self.assertIn("reused target session id", result.stdout)
        self.assertIn("SUMMARY pass=1 fail=0 unknown=1", result.stdout)

    def test_run_supports_claude_codex_and_grok_without_leaking_the_rubric(self):
        expected_flags = {
            "claude": {
                "--no-session-persistence",
                "--setting-sources",
                "--strict-mcp-config",
            },
            "codex": {
                "--ephemeral",
                "--ignore-user-config",
                "--ignore-rules",
                "--skip-git-repo-check",
            },
            "grok": {
                "--no-memory",
                "--no-subagents",
                "--disable-web-search",
            },
        }
        host_directories = {
            "claude": ".claude",
            "codex": ".agents",
            "grok": ".grok",
        }
        for target in ("claude", "codex", "grok"):
            with self.subTest(target=target):
                with tempfile.TemporaryDirectory() as temp_dir:
                    skill = self.make_skill(temp_dir)
                    log_path = Path(temp_dir, f"{target}.jsonl")
                    bin_dir = self.make_fake_target(temp_dir, target)
                    environment = self.fake_target_environment(bin_dir, log_path)

                    result = self.run_cli(
                        "run",
                        skill,
                        "--target",
                        target,
                        "--model",
                        "fixture-model",
                        env=environment,
                    )
                    records = self.read_target_log(log_path)

                self.assertEqual(0, result.returncode, result.stderr + result.stdout)
                self.assertIn("PASS returns-requested-artifact", result.stdout)
                self.assertIn("SUMMARY pass=1 fail=0 unknown=0", result.stdout)
                self.assertEqual(2, len(records), records)
                candidate = next(item for item in records if not item["grader"])
                grader = next(item for item in records if item["grader"])
                self.assertTrue(candidate["skill_staged"])
                self.assertFalse(candidate["top_level_skill_staged"])
                self.assertFalse(candidate["evals_staged"])
                self.assertFalse(candidate["assertion_leaked"])
                self.assertTrue(grader["assertion_leaked"])
                self.assertIn(host_directories[target], candidate["staged_skill"])
                for record in records:
                    self.assertIn("fixture-model", record["arguments"])
                self.assertTrue(
                    expected_flags[target].issubset(set(candidate["arguments"])),
                    candidate["arguments"],
                )
                if target == "grok":
                    self.assertIn("skill-eval-strict", candidate["arguments"])
                    effort_index = candidate["arguments"].index(
                        "--reasoning-effort"
                    )
                    self.assertEqual(
                        "high", candidate["arguments"][effort_index + 1]
                    )
                    self.assertEqual("1", candidate["disable_autoupdater"])
                    self.assertIn("streaming-messages-json", grader["arguments"])
                    self.assertIn("--no-plan", grader["arguments"])
                    self.assertNotIn("--json-schema", grader["arguments"])
                    deny_rules = {
                        candidate["arguments"][index + 1]
                        for index, value in enumerate(candidate["arguments"][:-1])
                        if value == "--deny"
                    }
                    home = Path.home()
                    self.assertIn(f"Read({home}/**)", deny_rules)
                    self.assertIn(f"Grep({home}/**)", deny_rules)
                    self.assertIn(f"Bash(*{home}*)", deny_rules)
                    self.assertNotIn(f"Edit({home}/**)", deny_rules)
                    self.assertIn(
                        '[profiles.skill-eval-strict]', candidate["sandbox_toml"]
                    )
                    self.assertIn('extends = "strict"', candidate["sandbox_toml"])
                    self.assertIn(
                        str(skill.resolve()), candidate["sandbox_toml"]
                    )
                    self.assertIn(
                        "Do not inspect the outer eval manifests, rubrics, or "
                        "grader materials used to judge this session.",
                        candidate["prompt"],
                    )
                    self.assertIn(
                        "Treat a task package's own existing evals as task inputs",
                        candidate["prompt"],
                    )

    def test_run_forwards_codex_reasoning_effort_to_candidate_and_grader(self):
        for effort in (
            "none",
            "minimal",
            "low",
            "medium",
            "high",
            "xhigh",
            "max",
            "ultra",
        ):
            with self.subTest(effort=effort):
                with tempfile.TemporaryDirectory() as temp_dir:
                    skill = self.make_skill(temp_dir)
                    log_path = Path(temp_dir, "codex.jsonl")
                    bin_dir = self.make_fake_target(temp_dir, "codex")
                    environment = self.fake_target_environment(bin_dir, log_path)

                    result = self.run_cli(
                        "run",
                        skill,
                        "--target",
                        "codex",
                        "--model",
                        "gpt-5.6-terra",
                        "--reasoning-effort",
                        effort,
                        env=environment,
                    )
                    records = (
                        self.read_target_log(log_path)
                        if log_path.exists()
                        else []
                    )

                self.assertEqual(
                    0, result.returncode, result.stderr + result.stdout
                )
                self.assertEqual(2, len(records), records)
                for record in records:
                    self.assertIn("gpt-5.6-terra", record["arguments"])
                    config_index = record["arguments"].index("-c")
                    self.assertEqual(
                        f'model_reasoning_effort="{effort}"',
                        record["arguments"][config_index + 1],
                    )

    def test_run_forwards_claude_reasoning_effort_to_candidate_and_grader(self):
        for effort in ("low", "medium", "high", "xhigh", "max"):
            with self.subTest(effort=effort):
                with tempfile.TemporaryDirectory() as temp_dir:
                    skill = self.make_skill(temp_dir)
                    log_path = Path(temp_dir, "claude.jsonl")
                    bin_dir = self.make_fake_target(temp_dir, "claude")
                    environment = self.fake_target_environment(bin_dir, log_path)

                    result = self.run_cli(
                        "run",
                        skill,
                        "--target",
                        "claude",
                        "--model",
                        "claude-sonnet-5",
                        "--reasoning-effort",
                        effort,
                        env=environment,
                    )
                    records = (
                        self.read_target_log(log_path)
                        if log_path.exists()
                        else []
                    )

                self.assertEqual(
                    0, result.returncode, result.stderr + result.stdout
                )
                self.assertEqual(2, len(records), records)
                for record in records:
                    self.assertIn("claude-sonnet-5", record["arguments"])
                    effort_index = record["arguments"].index("--effort")
                    self.assertEqual(
                        effort, record["arguments"][effort_index + 1]
                    )
                    mcp_config_index = record["arguments"].index("--mcp-config")
                    self.assertEqual(
                        {"mcpServers": {}},
                        json.loads(record["arguments"][mcp_config_index + 1]),
                    )

    def test_run_forwards_grok_reasoning_effort_to_candidate_and_grader(self):
        for effort in (
            "none",
            "minimal",
            "low",
            "medium",
            "high",
            "xhigh",
            "max",
        ):
            with self.subTest(effort=effort):
                with tempfile.TemporaryDirectory() as temp_dir:
                    skill = self.make_skill(temp_dir)
                    log_path = Path(temp_dir, "grok.jsonl")
                    bin_dir = self.make_fake_target(temp_dir, "grok")
                    environment = self.fake_target_environment(bin_dir, log_path)

                    result = self.run_cli(
                        "run",
                        skill,
                        "--target",
                        "grok",
                        "--model",
                        "grok-4.6",
                        "--reasoning-effort",
                        effort,
                        env=environment,
                    )
                    records = (
                        self.read_target_log(log_path)
                        if log_path.exists()
                        else []
                    )

                self.assertEqual(
                    0, result.returncode, result.stderr + result.stdout
                )
                self.assertEqual(2, len(records), records)
                for record in records:
                    self.assertIn("grok-4.6", record["arguments"])
                    effort_index = record["arguments"].index(
                        "--reasoning-effort"
                    )
                    self.assertEqual(
                        effort, record["arguments"][effort_index + 1]
                    )

    def test_run_uses_target_default_model_and_reasoning_effort(self):
        defaults = {
            "claude": ("claude-sonnet-5", "high"),
            "codex": ("gpt-5.6-terra", "high"),
            "grok": ("grok-4.6", "high"),
        }
        for target, (model, effort) in defaults.items():
            with self.subTest(target=target):
                with tempfile.TemporaryDirectory() as temp_dir:
                    skill = self.make_skill(temp_dir)
                    log_path = Path(temp_dir, f"{target}.jsonl")
                    bin_dir = self.make_fake_target(temp_dir, target)
                    environment = self.fake_target_environment(bin_dir, log_path)

                    result = self.run_cli(
                        "run",
                        skill,
                        "--target",
                        target,
                        env=environment,
                    )
                    records = self.read_target_log(log_path)

                self.assertEqual(
                    0, result.returncode, result.stderr + result.stdout
                )
                self.assertEqual(2, len(records), records)
                for record in records:
                    model_index = record["arguments"].index("--model")
                    self.assertEqual(
                        model, record["arguments"][model_index + 1]
                    )
                    if target == "codex":
                        config_index = record["arguments"].index("-c")
                        self.assertEqual(
                            f'model_reasoning_effort="{effort}"',
                            record["arguments"][config_index + 1],
                        )
                    else:
                        effort_flag = (
                            "--effort"
                            if target == "claude"
                            else "--reasoning-effort"
                        )
                        effort_index = record["arguments"].index(effort_flag)
                        self.assertEqual(
                            effort, record["arguments"][effort_index + 1]
                        )

    @unittest.skipUnless(
        sys.platform.startswith("linux")
        and os.geteuid() == 0
        and shutil.which("bwrap"),
        "Claude's root sandbox regression is Linux/root/bubblewrap-specific",
    )
    def test_run_executes_writable_claude_candidate_as_non_root(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "claude.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "claude")
            environment = self.fake_target_environment(bin_dir, log_path)

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "claude",
                env=environment,
            )
            records = self.read_target_log(log_path) if log_path.exists() else []

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        candidate = next(item for item in records if not item["grader"])
        grader = next(item for item in records if item["grader"])
        self.assertNotEqual(0, candidate["euid"])
        self.assertEqual(0, grader["euid"])

    def test_run_requires_a_completed_inspection_before_grader_output(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_PROGRESS_GRADER_UNLESS_FINAL"] = "1"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                env=environment,
            )

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("PASS returns-requested-artifact", result.stdout)

    def test_run_rebuilds_the_grok_sandbox_before_grading(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_DELETE_GROK_SANDBOX_AFTER_CANDIDATE"] = "1"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                env=environment,
            )
            records = self.read_target_log(log_path)

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        grader = next(item for item in records if item["grader"])
        self.assertIsNotNone(grader["sandbox_toml"])
        self.assertIn("[profiles.skill-eval-strict]", grader["sandbox_toml"])
        self.assertNotIn("Starting read-only inspection", result.stdout)

    def test_run_observes_grok_candidate_and_grader_protocol_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_EMPTY_GROK_GRADER"] = "1"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--timeout",
                "30",
                env=environment,
            )

        self.assertEqual(1, result.returncode)
        self.assertIn("phase=candidate status=start", result.stderr)
        self.assertRegex(
            result.stderr,
            r"phase=candidate status=complete elapsed_ms=\d+ "
            r"stdout_bytes=\d+ stderr_bytes=\d+",
        )
        self.assertIn("phase=grader status=start", result.stderr)
        self.assertRegex(
            result.stderr,
            r"phase=grader status=complete elapsed_ms=\d+ "
            r"stdout_bytes=\d+ stderr_bytes=\d+",
        )
        self.assertIn("phase=grader status=protocol_error", result.stderr)
        self.assertIn("reason=grader protocol:", result.stdout)

    def test_run_reports_a_sanitized_terminal_summary_for_fast_targets(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                env=environment,
            )

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        terminal = next(
            line
            for line in result.stderr.splitlines()
            if "phase=candidate status=complete" in line
        )
        self.assertIn("event_types=", terminal)
        self.assertIn("tool_calls=", terminal)
        self.assertIn("tool_targets=", terminal)
        self.assertIn("last_stop_reason=end_turn", terminal)

    def test_run_uses_grok_end_turn_assistant_text_for_grading(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_GROK_ASSISTANT_FINAL"] = "1"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                env=environment,
            )
            records = self.read_target_log(log_path)

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("PASS returns-requested-artifact", result.stdout)
        grader = next(item for item in records if item["grader"])
        self.assertIn("streaming-messages-json", grader["arguments"])
        self.assertNotIn("--json-schema", grader["arguments"])

    def test_run_accepts_one_fenced_grok_grader_object(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_FENCED_GROK_GRADER"] = "1"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                env=environment,
            )

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("PASS returns-requested-artifact", result.stdout)

    def test_run_rejects_a_grok_object_embedded_in_prose(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_PROSE_FENCED_GROK_GRADER"] = "1"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                env=environment,
            )

        self.assertEqual(1, result.returncode)
        self.assertIn("grader final response is invalid JSON", result.stdout)
        self.assertIn("SUMMARY pass=0 fail=0 unknown=1", result.stdout)

    def test_run_requires_every_assertion_in_the_grader_verdict(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            evals_path, document = self.read_evals(skill)
            document["evals"][0]["assertions"].append(
                {
                    "id": "artifact-preserved",
                    "description": "The artifact retains the expected content.",
                }
            )
            evals_path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_OMIT_ASSERTIONS_UNLESS_COUNTED"] = "1"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                env=environment,
            )

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("PASS artifact-created", result.stdout)
        self.assertIn("PASS artifact-preserved", result.stdout)

    def test_run_stages_explicit_additional_skills_for_coexistence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            other_skill = self.make_auxiliary_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"][0]["category"] = "coexistence"
            document["evals"][0]["additional_skills"] = ["other-skill"]
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            log_path = Path(temp_dir, "codex.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "codex")
            environment = self.fake_target_environment(bin_dir, log_path)

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "codex",
                "--additional-skill",
                f"other-skill={other_skill}",
                env=environment,
            )
            records = self.read_target_log(log_path)

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        candidate = next(item for item in records if not item["grader"])
        self.assertTrue(candidate["other_staged"])

    def test_run_stages_a_package_local_additional_skill_fixture(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            fixture_skill = (
                skill / "evals" / "fixtures" / "skills" / "other-skill"
            )
            fixture_skill.mkdir(parents=True)
            fixture_skill.joinpath("SKILL.md").write_text(
                "---\n"
                "name: other-skill\n"
                'description: "A competing fixture skill."\n'
                "---\n\n"
                "# Other Skill\n",
                encoding="utf-8",
            )
            path, document = self.read_evals(skill)
            document["evals"][0]["category"] = "coexistence"
            document["evals"][0]["additional_skills"] = ["other-skill"]
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                env=environment,
            )
            records = self.read_target_log(log_path)

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        candidate = next(item for item in records if not item["grader"])
        self.assertTrue(candidate["other_staged"])
        self.assertIn(str(skill.resolve()), candidate["sandbox_toml"])
        self.assertNotIn(
            str(fixture_skill.resolve()), candidate["sandbox_toml"]
        )

    def test_run_keeps_missing_additional_skill_evidence_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"][0]["category"] = "coexistence"
            document["evals"][0]["additional_skills"] = ["other-skill"]
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")

            result = self.run_cli("run", skill, "--target", "codex")

        self.assertEqual(1, result.returncode)
        self.assertIn("UNKNOWN returns-requested-artifact", result.stdout)
        self.assertIn("missing additional skill path: other-skill", result.stdout)
        self.assertIn("SUMMARY pass=0 fail=0 unknown=1", result.stdout)

    def test_run_observes_claude_and_grok_trigger_calls(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"] = []
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            self.write_trigger_evals(skill)
            claude_log = Path(temp_dir, "claude.jsonl")
            claude_bin = self.make_fake_target(temp_dir, "claude")
            claude_environment = self.fake_target_environment(
                claude_bin, claude_log
            )

            claude_result = self.run_cli(
                "run",
                skill,
                "--target",
                "claude",
                env=claude_environment,
            )

            grok_log = Path(temp_dir, "grok.jsonl")
            grok_bin = self.make_fake_target(temp_dir, "grok")
            grok_environment = self.fake_target_environment(grok_bin, grok_log)
            grok_result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                env=grok_environment,
            )

            opaque_results = {}
            opaque_call_counts = {}
            for target in ("codex",):
                log_path = Path(temp_dir, f"{target}.jsonl")
                bin_dir = self.make_fake_target(temp_dir, target)
                environment = self.fake_target_environment(bin_dir, log_path)
                opaque_results[target] = self.run_cli(
                    "run",
                    skill,
                    "--target",
                    target,
                    "--case",
                    "create-a-skill",
                    env=environment,
                )
                opaque_call_counts[target] = (
                    len(self.read_target_log(log_path)) if log_path.exists() else 0
                )

        self.assertEqual(
            0, claude_result.returncode, claude_result.stderr + claude_result.stdout
        )
        self.assertIn("PASS create-a-skill", claude_result.stdout)
        self.assertIn("PASS install-a-skill", claude_result.stdout)
        self.assertIn("SUMMARY pass=2 fail=0 unknown=0", claude_result.stdout)
        self.assertEqual(
            0, grok_result.returncode, grok_result.stderr + grok_result.stdout
        )
        self.assertIn("PASS create-a-skill", grok_result.stdout)
        self.assertIn("PASS install-a-skill", grok_result.stdout)
        self.assertIn("SUMMARY pass=2 fail=0 unknown=0", grok_result.stdout)
        for target, result in opaque_results.items():
            with self.subTest(target=target):
                self.assertEqual(1, result.returncode)
                self.assertIn("UNKNOWN create-a-skill", result.stdout)
                self.assertIn(
                    "no attributable automatic skill activation event",
                    result.stdout,
                )
                self.assertIn("SUMMARY pass=0 fail=0 unknown=1", result.stdout)
                self.assertEqual(
                    0,
                    opaque_call_counts[target],
                    "known-unobservable trigger evaluation spent a target call",
                )

    def test_run_stops_claude_after_attributable_positive_activation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"] = []
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            self.write_trigger_evals(skill)
            log_path = Path(temp_dir, "claude.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "claude")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_SLEEP_AFTER_CLAUDE_ACTIVATION"] = "30"

            started = time.monotonic()
            result = self.run_cli(
                "run",
                skill,
                "--target",
                "claude",
                "--case",
                "create-a-skill",
                "--timeout",
                "0.2",
                env=environment,
            )
            elapsed = time.monotonic() - started

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("PASS create-a-skill", result.stdout)
        self.assertIn("phase=candidate status=observed", result.stderr)
        self.assertLess(elapsed, 2.0, result.stdout + result.stderr)

    def test_run_waits_for_claude_to_finish_before_judging_nonactivation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"] = []
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            self.write_trigger_evals(skill)
            log_path = Path(temp_dir, "claude.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "claude")
            environment = self.fake_target_environment(bin_dir, log_path)
            # The model explores first and only decides on a later turn, after
            # the runner's first observation tick has already seen a tool call.
            environment["FAKE_EXPLORE_BEFORE_DECIDING_SECONDS"] = "6"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "claude",
                "--case",
                "create-a-skill",
                "--case",
                "install-a-skill",
                "--timeout",
                "30",
                env=environment,
            )

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("PASS create-a-skill", result.stdout)
        self.assertIn("PASS install-a-skill", result.stdout)
        self.assertIn("SUMMARY pass=2 fail=0 unknown=0", result.stdout)
        negative_prefix = (
            "OBSERVE case=install-a-skill iteration=1 target=claude "
            "phase=candidate"
        )
        self.assertIn(f"{negative_prefix} status=complete", result.stderr)
        self.assertNotIn(f"{negative_prefix} status=observed", result.stderr)

    def test_run_stops_grok_after_attributable_positive_activation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"] = []
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            self.write_trigger_evals(skill)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_SLEEP_AFTER_GROK_ACTIVATION"] = "30"

            started = time.monotonic()
            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--case",
                "create-a-skill",
                "--timeout",
                "0.2",
                env=environment,
            )
            elapsed = time.monotonic() - started

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("PASS create-a-skill", result.stdout)
        self.assertIn("phase=candidate status=observed", result.stderr)
        self.assertLess(elapsed, 2.0, result.stdout + result.stderr)

    def test_run_waits_for_grok_to_finish_before_judging_nonactivation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"] = []
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            self.write_trigger_evals(skill)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            # The model explores first and only decides on a later turn, after
            # the runner's first observation tick has already seen a tool call.
            environment["FAKE_EXPLORE_BEFORE_DECIDING_SECONDS"] = "6"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--case",
                "create-a-skill",
                "--case",
                "install-a-skill",
                "--timeout",
                "30",
                env=environment,
            )

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("PASS create-a-skill", result.stdout)
        self.assertIn("PASS install-a-skill", result.stdout)
        self.assertIn("SUMMARY pass=2 fail=0 unknown=0", result.stdout)
        negative_prefix = (
            "OBSERVE case=install-a-skill iteration=1 target=grok "
            "phase=candidate"
        )
        self.assertIn(f"{negative_prefix} status=complete", result.stderr)
        self.assertNotIn(f"{negative_prefix} status=observed", result.stderr)

    def test_run_grader_sees_a_workspace_directory_named_after_the_skill(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "claude.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "claude")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_WRITE_SKILL_NAMED_DIRECTORY"] = "1"

            result = self.run_cli(
                "run", skill, "--target", "claude", env=environment
            )
            records = self.read_target_log(log_path)

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        grader = next(item for item in records if item["grader"])
        self.assertTrue(grader["skill_named_directory_visible"], grader)
        self.assertTrue(grader["after_state_lists_skill_named_file"], grader)

    def test_rerun_ignores_non_executable_permission_bits(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            self.write_trigger_evals(skill)
            log_path = Path(temp_dir, "claude.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "claude")
            environment = self.fake_target_environment(bin_dir, log_path)
            skill_md = skill / "SKILL.md"
            skill_md.chmod(0o644)

            first = self.run_cli(
                "run-one",
                skill,
                "create-a-skill",
                "--target",
                "claude",
                env=environment,
            )
            first_report = self.report_path_from(first)
            self.addCleanup(first_report.unlink, missing_ok=True)
            skill_md.chmod(0o600)
            same_content = self.run_cli("rerun", first_report, env=environment)
            if same_content.returncode == 0:
                self.addCleanup(
                    self.report_path_from(same_content).unlink, missing_ok=True
                )
            skill_md.chmod(0o755)
            executable_drift = self.run_cli(
                "rerun", first_report, env=environment
            )

        self.assertEqual(0, first.returncode, first.stderr + first.stdout)
        self.assertEqual(
            0, same_content.returncode, same_content.stderr + same_content.stdout
        )
        self.assertEqual(2, executable_drift.returncode)
        self.assertIn(
            "package changed since the recorded run", executable_drift.stderr
        )

    def test_run_requires_target_catalog_evidence_for_non_activation(self):
        for target in ("claude", "grok"):
            with self.subTest(target=target):
                with tempfile.TemporaryDirectory() as temp_dir:
                    skill = self.make_skill(temp_dir)
                    path, document = self.read_evals(skill)
                    document["evals"] = []
                    path.write_text(json.dumps(document) + "\n", encoding="utf-8")
                    self.write_trigger_evals(skill)
                    log_path = Path(temp_dir, f"{target}.jsonl")
                    bin_dir = self.make_fake_target(temp_dir, target)
                    environment = self.fake_target_environment(bin_dir, log_path)
                    environment["FAKE_NO_CATALOG"] = "1"

                    result = self.run_cli(
                        "run",
                        skill,
                        "--target",
                        target,
                        "--case",
                        "install-a-skill",
                        env=environment,
                    )

                self.assertEqual(1, result.returncode)
                self.assertIn("UNKNOWN install-a-skill", result.stdout)
                self.assertIn("did not advertise 'sample-skill'", result.stdout)

    def test_run_keeps_builtin_target_failures_and_bad_grading_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            missing_environment = os.environ.copy()
            missing_environment["PATH"] = str(Path(temp_dir, "empty-bin"))
            missing = self.run_cli(
                "run",
                skill,
                "--target",
                "codex",
                env=missing_environment,
            )

            log_path = Path(temp_dir, "claude.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "claude")
            bad_environment = self.fake_target_environment(bin_dir, log_path)
            bad_environment["FAKE_BAD_GRADER"] = "1"
            malformed = self.run_cli(
                "run",
                skill,
                "--target",
                "claude",
                env=bad_environment,
            )

        self.assertEqual(1, missing.returncode)
        self.assertIn("UNKNOWN returns-requested-artifact", missing.stdout)
        self.assertIn("codex could not start", missing.stdout)
        self.assertEqual(1, malformed.returncode)
        self.assertIn("phase=candidate status=complete", malformed.stderr)
        self.assertIn("phase=grader status=complete", malformed.stderr)
        self.assertIn("UNKNOWN returns-requested-artifact", malformed.stdout)
        self.assertIn("invalid status", malformed.stdout)

    def test_run_terminates_target_descendants_on_timeout(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            marker = Path(temp_dir, "orphan-marker.txt")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_CHILD_MARKER"] = str(marker)
            environment["FAKE_TIMEOUT_EVENT"] = "1"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--timeout",
                "0.2",
                env=environment,
            )
            time.sleep(1)

            self.assertEqual(1, result.returncode)
            self.assertIn("grok timed out", result.stdout)
            self.assertIn("json_events=2", result.stdout)
            self.assertIn("event_types=assistant:1,user:1", result.stdout)
            self.assertIn("tool_calls=read_file:1", result.stdout)
            self.assertIn("tool_results=error:1", result.stdout)
            self.assertIn("tool_targets=SKILL.md:1", result.stdout)
            self.assertIn("last_stop_reason=tool_use", result.stdout)
            self.assertIn("phase=candidate status=progress", result.stderr)
            self.assertIn("tool_calls=read_file:1", result.stderr)
            self.assertNotIn("permission denied", result.stderr)
            self.assertNotIn("partial-session", result.stderr)
            self.assertFalse(marker.exists(), "timed-out target left a live child")

    def test_run_preserves_a_failed_workspace_only_when_requested(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            marker = Path(temp_dir, "orphan-marker.txt")
            artifacts = Path(temp_dir, "artifacts")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_CHILD_MARKER"] = str(marker)
            environment["FAKE_PARTIAL_ARTIFACT"] = "1"
            environment["FAKE_TIMEOUT_EVENT"] = "1"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--timeout",
                "0.2",
                "--artifacts-dir",
                artifacts,
                env=environment,
            )
            saved = artifacts / "returns-requested-artifact" / "iteration-1"

            self.assertEqual(1, result.returncode)
            self.assertEqual(
                "created before timeout\n",
                saved.joinpath("partial-artifact.txt").read_text(),
            )
            metadata = json.loads(saved.joinpath("eval-result.json").read_text())
            self.assertEqual("unknown", metadata["status"])
            observation = saved / "observation"
            self.assertIn(
                '"type": "assistant"',
                observation.joinpath("candidate-events.jsonl").read_text(),
            )
            timing = json.loads(
                observation.joinpath("candidate-timing.json").read_text()
            )
            self.assertEqual("process_error", timing["status"])
            self.assertGreaterEqual(timing["wall_duration_ms"], 0)
            self.assertFalse(saved.joinpath(".grok").exists())
            self.assertIn("phase=artifacts status=saved", result.stderr)

    def test_run_preserves_phase_transcripts_and_timing_when_requested(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            artifacts = Path(temp_dir, "artifacts")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--artifacts-dir",
                artifacts,
                env=environment,
            )
            observation = (
                artifacts
                / "returns-requested-artifact"
                / "iteration-1"
                / "observation"
            )
            phase_artifacts = {
                phase: {
                    "events": observation.joinpath(
                        f"{phase}-events.jsonl"
                    ).is_file(),
                    "stderr": observation.joinpath(
                        f"{phase}-stderr.txt"
                    ).is_file(),
                    "timing": json.loads(
                        observation.joinpath(f"{phase}-timing.json").read_text()
                    ),
                }
                for phase in ("candidate", "grader")
            }

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        for phase in ("candidate", "grader"):
            self.assertTrue(phase_artifacts[phase]["events"])
            self.assertTrue(phase_artifacts[phase]["stderr"])
            timing = phase_artifacts[phase]["timing"]
            self.assertEqual("complete", timing["status"])
            self.assertEqual(15, timing["total_tokens"])
            self.assertEqual(123, timing["target_duration_ms"])
            self.assertGreaterEqual(timing["wall_duration_ms"], 0)

    def test_run_refuses_to_overwrite_an_artifacts_directory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            artifacts = Path(temp_dir, "artifacts")
            artifacts.mkdir()
            sentinel = artifacts / "owned-by-user.txt"
            sentinel.write_text("keep me\n", encoding="utf-8")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--artifacts-dir",
                artifacts,
                env=environment,
            )
            sentinel_text = sentinel.read_text()
            target_ran = log_path.exists()

        self.assertEqual(2, result.returncode)
        self.assertIn("--artifacts-dir already exists", result.stderr)
        self.assertEqual("keep me\n", sentinel_text)
        self.assertFalse(target_ran, "target ran before overwrite rejection")

    def test_run_refuses_artifacts_inside_the_evaluated_skill(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            artifacts = skill / "debug-artifacts"
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--artifacts-dir",
                artifacts,
                env=environment,
            )

        self.assertEqual(2, result.returncode)
        self.assertIn("must be outside the skill package", result.stderr)
        self.assertFalse(log_path.exists(), "target ran before path rejection")

    def test_run_timeout_does_not_wait_for_a_detached_pipe_holder(self):
        detached_seconds = 3.0
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_DETACHED_PIPE_SECONDS"] = str(detached_seconds)

            started = time.monotonic()
            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--timeout",
                "0.2",
                env=environment,
            )
            elapsed = time.monotonic() - started
            time.sleep(max(0, detached_seconds + 0.2 - elapsed))

        self.assertEqual(1, result.returncode)
        self.assertIn("grok timed out", result.stdout)
        self.assertLess(elapsed, 2.0, result.stdout + result.stderr)

    def test_run_accepts_completion_after_an_observation_heartbeat(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_CANDIDATE_DELAY_SECONDS"] = "5.2"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--timeout",
                "8",
                env=environment,
            )

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("phase=candidate status=progress", result.stderr)
        self.assertIn("phase=candidate status=complete", result.stderr)
        self.assertIn("PASS returns-requested-artifact", result.stdout)

    def test_run_gives_candidate_and_grader_independent_timeouts(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_CANDIDATE_DELAY_SECONDS"] = "0.15"
            environment["FAKE_GRADER_DELAY_SECONDS"] = "0.15"

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--timeout",
                "0.25",
                env=environment,
            )

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("PASS returns-requested-artifact", result.stdout)

    def test_run_help_describes_timeout_as_per_phase(self):
        result = self.run_cli("run", "--help")

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn(
            "per built-in candidate or grader phase",
            " ".join(result.stdout.split()),
        )

    def test_run_help_describes_target_defaults(self):
        result = self.run_cli("run", "--help")
        help_text = " ".join(result.stdout.split())

        self.assertEqual(0, result.returncode, result.stderr)
        for target_default in (
            "claude=claude-sonnet-5",
            "codex=gpt-5.6-terra",
            "grok=grok-4.6",
        ):
            self.assertIn(target_default, help_text)
        self.assertIn(
            "defaults: claude=high, codex=high, grok=high",
            help_text,
        )
        for target_efforts in (
            "claude=low/medium/high/xhigh/max",
            "codex=none/minimal/low/medium/high/xhigh/max/ultra",
            "grok=none/minimal/low/medium/high/xhigh/max",
        ):
            self.assertIn(target_efforts, help_text)

    def test_run_rejects_a_reused_builtin_grader_session_as_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            artifacts = Path(temp_dir, "artifacts")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)
            environment["FAKE_FIXED_GRADER_SESSION"] = (
                "11111111-1111-4111-8111-111111111111"
            )

            result = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--repeat",
                "2",
                "--artifacts-dir",
                artifacts,
                env=environment,
            )
            second_metadata = json.loads(
                artifacts.joinpath(
                    "returns-requested-artifact",
                    "iteration-2",
                    "eval-result.json",
                ).read_text()
            )

        self.assertEqual(1, result.returncode)
        self.assertIn(
            "PASS returns-requested-artifact iteration=1", result.stdout
        )
        self.assertIn(
            "UNKNOWN returns-requested-artifact iteration=2", result.stdout
        )
        self.assertEqual("unknown", second_metadata["status"])
        self.assertIn("reused target session id", second_metadata["detail"])
        self.assertIn("reused target session id", result.stdout)

    def test_run_keeps_uncontrolled_codex_isolation_unknown(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"][0]["category"] = "isolation"
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")

            result = self.run_cli("run", skill, "--target", "codex")

        self.assertEqual(1, result.returncode)
        self.assertIn("UNKNOWN returns-requested-artifact", result.stdout)
        self.assertIn("cannot suppress ambient user skills", result.stdout)

    def test_run_uses_a_fail_closed_grok_workspace_for_isolation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"][0]["category"] = "isolation"
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)

            result = self.run_cli(
                "run", skill, "--target", "grok", env=environment
            )

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        self.assertIn("PASS returns-requested-artifact", result.stdout)

    def test_run_stages_the_grok_sandbox_when_the_skill_is_disabled(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            path, document = self.read_evals(skill)
            document["evals"][0]["category"] = "baseline"
            document["evals"][0]["skill_mode"] = "disabled"
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            log_path = Path(temp_dir, "grok.jsonl")
            bin_dir = self.make_fake_target(temp_dir, "grok")
            environment = self.fake_target_environment(bin_dir, log_path)

            result = self.run_cli(
                "run", skill, "--target", "grok", env=environment
            )
            records = self.read_target_log(log_path)

        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        candidate = next(item for item in records if not item["grader"])
        self.assertFalse(candidate["skill_staged"])
        self.assertIsNotNone(candidate["sandbox_toml"])

    def test_run_rejects_ambiguous_target_commands(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            target_and_adapter = self.run_cli(
                "run",
                skill,
                "--target",
                "claude",
                "--",
                sys.executable,
                "-c",
                "pass",
            )
            model_without_target = self.run_cli(
                "run", skill, "--model", "fixture-model"
            )
            reasoning_without_target = self.run_cli(
                "run", skill, "--reasoning-effort", "high"
            )
            unsupported_grok_reasoning = self.run_cli(
                "run",
                skill,
                "--target",
                "grok",
                "--reasoning-effort",
                "ultra",
            )
            unsupported_claude_reasoning = self.run_cli(
                "run",
                skill,
                "--target",
                "claude",
                "--reasoning-effort",
                "minimal",
            )
            unsupported_reasoning = self.run_cli(
                "run",
                skill,
                "--target",
                "codex",
                "--reasoning-effort",
                "extreme",
                env={"PATH": ""},
            )
            malformed_mapping = self.run_cli(
                "run",
                skill,
                "--target",
                "claude",
                "--additional-skill",
                "missing-equals-sign",
            )

        self.assertEqual(2, target_and_adapter.returncode)
        self.assertIn("choose either --target or an adapter", target_and_adapter.stderr)
        self.assertEqual(2, model_without_target.returncode)
        self.assertIn("--model requires --target", model_without_target.stderr)
        self.assertEqual(2, reasoning_without_target.returncode)
        self.assertIn(
            "--reasoning-effort requires --target",
            reasoning_without_target.stderr,
        )
        self.assertEqual(2, unsupported_grok_reasoning.returncode)
        self.assertIn(
            "--reasoning-effort 'ultra' is not supported for --target grok",
            unsupported_grok_reasoning.stderr,
        )
        self.assertEqual(2, unsupported_claude_reasoning.returncode)
        self.assertIn(
            "--reasoning-effort 'minimal' is not supported for --target claude",
            unsupported_claude_reasoning.stderr,
        )
        self.assertEqual(2, unsupported_reasoning.returncode)
        self.assertIn("invalid choice: 'extreme'", unsupported_reasoning.stderr)
        self.assertEqual(2, malformed_mapping.returncode)
        self.assertIn("NAME=PATH", malformed_mapping.stderr)

    def test_run_can_select_an_affected_case(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            self.write_trigger_evals(skill)
            adapter = Path(temp_dir, "selected-case-adapter.py")
            adapter.write_text(
                "import json\n"
                "import sys\n"
                "request = json.load(sys.stdin)\n"
                "assert request['case']['id'] == 'install-a-skill'\n"
                "json.dump({\n"
                "    'protocol_version': 1,\n"
                "    'case_id': 'install-a-skill',\n"
                "    'session_id': 'selected-case-session',\n"
                "    'fresh_session': True,\n"
                "    'activated': False,\n"
                "    'evidence': 'activation trace is empty',\n"
                "}, sys.stdout)\n",
                encoding="utf-8",
            )

            result = self.run_cli(
                "run",
                skill,
                "--case",
                "install-a-skill",
                "--",
                sys.executable,
                adapter,
            )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertNotIn("returns-requested-artifact", result.stdout)
        self.assertNotIn("create-a-skill", result.stdout)
        self.assertIn("PASS install-a-skill iteration=1", result.stdout)
        self.assertIn("SUMMARY pass=1 fail=0 unknown=0", result.stdout)

    def test_run_rejects_unknown_or_duplicate_case_selection(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skill = self.make_skill(temp_dir)
            self.write_trigger_evals(skill)

            unknown = self.run_cli("run", skill, "--case", "missing-case")
            duplicate = self.run_cli(
                "run",
                skill,
                "--case",
                "install-a-skill",
                "--case",
                "install-a-skill",
            )

        self.assertEqual(2, unknown.returncode)
        self.assertIn("--case not found: missing-case", unknown.stderr)
        self.assertEqual(2, duplicate.returncode)
        self.assertIn("--case values must be unique", duplicate.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
