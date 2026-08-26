#!/usr/bin/env python3
"""Validate and run portable skill evaluation cases."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import time


SCHEMA_VERSION = 1
IDENTIFIER = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
DEICTIC_NEGATIVE_OWNER = re.compile(
    r"\b(?:this|that|the)\s+(?:package|project|script|skill)\b",
    re.IGNORECASE,
)
FUNCTIONAL_CATEGORIES = {"baseline", "coexistence", "functional", "isolation"}
SAFE_SIDE_EFFECTS = {"fixture", "none"}
RESULT_STATUSES = {"fail", "pass", "unknown"}
TARGET_CONFIGS = {
    "claude": {
        "model": "claude-sonnet-5",
        "reasoning_effort": "high",
        "canonical_reasoning_efforts": (
            "low",
            "medium",
            "high",
            "xhigh",
            "max",
        ),
    },
    "codex": {
        "model": "gpt-5.6-terra",
        "reasoning_effort": "high",
        "canonical_reasoning_efforts": (
            "none",
            "minimal",
            "low",
            "medium",
            "high",
            "xhigh",
            "max",
            "ultra",
        ),
    },
    "grok": {
        "model": "grok-4.6",
        "reasoning_effort": "high",
        "canonical_reasoning_efforts": (
            "none",
            "minimal",
            "low",
            "medium",
            "high",
            "xhigh",
            "max",
        ),
    },
}
TARGETS = set(TARGET_CONFIGS)
REASONING_EFFORTS = set().union(
    *(config["canonical_reasoning_efforts"] for config in TARGET_CONFIGS.values())
)
TARGET_SKILL_ROOTS = {
    "claude": Path(".claude/skills"),
    "codex": Path(".agents/skills"),
    "grok": Path(".grok/skills"),
}
TARGET_OUTPUT_LIMIT = 32 * 1024 * 1024
TARGET_OBSERVATION_INTERVAL = 5.0
TARGET_TERMINATION_GRACE = 1.0
GROK_EVAL_SANDBOX_PROFILE = "skill-eval-strict"
FUNCTIONAL_EVAL_BOUNDARY = (
    "Evaluation boundary: work only inside the current workspace and use only "
    "the staged skills and task inputs. Do not inspect the outer eval manifests, "
    "rubrics, or grader materials used to judge this session. Do not inspect "
    "user-level skill directories. Treat a task package's own existing evals as "
    "task inputs: inspect and run them when the staged skill workflow requires it. "
    "Complete the requested task, run only relevant checks, give the final response, "
    "and stop."
)
TOKEN_FIELDS = {
    "cache_creation_input_tokens",
    "cache_read_input_tokens",
    "cached_input_tokens",
    "input_tokens",
    "output_tokens",
    "total_tokens",
}


class ContractError(ValueError):
    """The skill or its evaluation package is invalid."""


class TargetError(RuntimeError):
    """A target run could not provide trustworthy evaluation evidence."""


def reject_unknown_fields(value, allowed, location):
    unknown = set(value) - set(allowed)
    if unknown:
        raise ContractError(
            f"{location} has unknown fields: {', '.join(sorted(unknown))}"
        )


def validate_additional_skills(value, location, skill_name):
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not IDENTIFIER.fullmatch(item)
        for item in value
    ):
        raise ContractError(
            f"{location} additional_skills must be hyphen-case names"
        )
    if len(value) != len(set(value)) or skill_name in value:
        raise ContractError(
            f"{location} additional_skills must be unique other skills"
        )


def validate_fixture_files(value, location, fixtures_dir):
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item for item in value
    ):
        raise ContractError(f"{location} files must be an array of paths")
    if len(value) != len(set(value)):
        raise ContractError(f"{location} files must not contain duplicates")
    fixtures_root = fixtures_dir.resolve()
    for item in value:
        fixture = fixtures_dir.joinpath(item).resolve()
        try:
            fixture.relative_to(fixtures_root)
        except ValueError as error:
            raise ContractError(
                f"{location} fixture path must stay inside evals/fixtures: {item}"
            ) from error
        if not fixture.is_file():
            raise ContractError(f"{location} fixture file not found: {item}")


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ContractError(f"{path}: {error}") from error


def read_skill_name(skill_dir):
    skill_md = skill_dir / "SKILL.md"
    try:
        text = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise ContractError(f"{skill_md}: {error}") from error
    frontmatter = re.match(r"^---\n(.*?)\n---(?:\n|$)", text, re.DOTALL)
    if frontmatter is None:
        raise ContractError(f"{skill_md}: missing YAML frontmatter")
    name = re.search(
        r"^name:\s*(?:\"([^\"]+)\"|'([^']+)'|([^\s#]+))\s*$",
        frontmatter.group(1),
        re.MULTILINE,
    )
    if name is None:
        raise ContractError(f"{skill_md}: missing one-line name")
    value = next(group for group in name.groups() if group is not None)
    if not IDENTIFIER.fullmatch(value):
        raise ContractError(f"{skill_md}: invalid skill name {value!r}")
    if value != skill_dir.name:
        raise ContractError(
            f"{skill_md}: name {value!r} does not match directory {skill_dir.name!r}"
        )
    return value


def validate_skill_package(skill_path, expected_name=None):
    supplied_path = Path(skill_path)
    if supplied_path.is_symlink():
        raise ContractError(f"{supplied_path}: skill directory must not be a symlink")
    skill_dir = supplied_path.resolve()
    if not skill_dir.is_dir():
        raise ContractError(f"{skill_dir}: skill directory not found")
    for packaged_path in skill_dir.rglob("*"):
        if packaged_path.is_symlink():
            relative = packaged_path.relative_to(skill_dir)
            raise ContractError(
                f"{skill_dir}: symbolic links are not supported: {relative}"
            )
    skill_name = read_skill_name(skill_dir)
    if expected_name is not None and skill_name != expected_name:
        raise ContractError(
            f"additional skill {expected_name!r} points to package {skill_name!r}"
        )
    return skill_dir, skill_name


def copy_skill_without_evals(source, destination):
    source = Path(source).resolve()

    def ignore_eval_answers(current_source, names):
        if Path(current_source).resolve() == source and "evals" in names:
            return {"evals"}
        return set()

    shutil.copytree(source, destination, ignore=ignore_eval_answers)


def package_digest(package_dir):
    package_dir = Path(package_dir).resolve()
    digest = hashlib.sha256()
    try:
        paths = sorted(
            (package_dir, *package_dir.rglob("*")),
            key=lambda path: path.relative_to(package_dir).as_posix(),
        )
        for path in paths:
            relative = path.relative_to(package_dir).as_posix() or "."
            mode = path.lstat().st_mode
            if stat.S_ISLNK(mode):
                raise ContractError(
                    f"{package_dir}: symbolic links are not supported: {relative}"
                )
            if stat.S_ISDIR(mode):
                kind = b"directory"
                content = b""
            elif stat.S_ISREG(mode):
                kind = b"file"
                content = path.read_bytes()
            else:
                raise ContractError(
                    f"{package_dir}: unsupported special file: {relative}"
                )
            digest.update(kind + b"\0")
            digest.update(relative.encode("utf-8") + b"\0")
            # Only the executable bit is identity; other permission bits vary
            # with the checkout umask and would make identical content drift.
            digest.update((b"x" if mode & 0o111 else b"-") + b"\0")
            digest.update(str(len(content)).encode("ascii") + b"\0")
            digest.update(content)
    except (OSError, UnicodeError) as error:
        raise ContractError(f"could not hash skill package {package_dir}: {error}") from error
    return digest.hexdigest()


def copy_stable_package(source, destination):
    source = Path(source).resolve()
    before = package_digest(source)
    try:
        shutil.copytree(source, destination)
    except OSError as error:
        raise ContractError(f"could not snapshot skill package {source}: {error}") from error
    after = package_digest(source)
    copied = package_digest(destination)
    if before != after or before != copied:
        raise ContractError(f"{source}: package changed while it was being snapshotted")
    return copied


def validate_functional_evals(path, skill_name):
    if not path.exists():
        return []
    document = load_json(path)
    if not isinstance(document, dict):
        raise ContractError(f"{path}: root must be an object")
    reject_unknown_fields(
        document, {"schema_version", "skill_name", "evals"}, str(path)
    )
    if (
        type(document.get("schema_version")) is not int
        or document["schema_version"] != SCHEMA_VERSION
    ):
        raise ContractError(f"{path}: schema_version must be {SCHEMA_VERSION}")
    if document.get("skill_name") != skill_name:
        raise ContractError(f"{path}: skill_name must be {skill_name!r}")
    cases = document.get("evals")
    if not isinstance(cases, list):
        raise ContractError(f"{path}: evals must be an array")
    case_ids = set()
    for index, case in enumerate(cases):
        location = f"{path}: eval #{index + 1}"
        if not isinstance(case, dict):
            raise ContractError(f"{location} must be an object")
        case_id = case.get("id")
        if not isinstance(case_id, str) or not IDENTIFIER.fullmatch(case_id):
            raise ContractError(f"{location} id must be a hyphen-case string")
        if case_id in case_ids:
            raise ContractError(f"{path}: duplicate eval id {case_id!r}")
        case_ids.add(case_id)
        location = f"{path}: eval {case_id}"
        reject_unknown_fields(
            case,
            {
                "additional_skills",
                "assertions",
                "category",
                "files",
                "id",
                "prompt",
                "side_effects",
                "skill_mode",
            },
            location,
        )
        category = case.get("category")
        if not isinstance(category, str) or category not in FUNCTIONAL_CATEGORIES:
            choices = ", ".join(sorted(FUNCTIONAL_CATEGORIES))
            raise ContractError(f"{location} category must be one of: {choices}")
        prompt = case.get("prompt")
        if not isinstance(prompt, str) or not prompt.strip():
            raise ContractError(f"{location} prompt must be a non-empty string")
        side_effects = case.get("side_effects")
        if not isinstance(side_effects, str) or side_effects not in SAFE_SIDE_EFFECTS:
            raise ContractError(
                f"{location} side_effects must be 'none' or 'fixture'"
            )
        skill_mode = case.get("skill_mode", "enabled")
        if not isinstance(skill_mode, str) or skill_mode not in {
            "disabled",
            "enabled",
        }:
            raise ContractError(
                f"{location} skill_mode must be 'enabled' or 'disabled'"
            )
        additional_skills = case.get("additional_skills", [])
        validate_additional_skills(additional_skills, location, skill_name)
        if category == "baseline" and skill_mode != "disabled":
            raise ContractError(
                f"{location} baseline cases must set skill_mode to 'disabled'"
            )
        if category != "baseline" and skill_mode == "disabled":
            raise ContractError(
                f"{location} only baseline cases may disable the evaluated skill"
            )
        if category == "coexistence" and not additional_skills:
            raise ContractError(
                f"{location} coexistence cases must declare additional_skills"
            )
        if category == "isolation" and additional_skills:
            raise ContractError(
                f"{location} isolation cases must not declare additional_skills"
            )
        validate_fixture_files(
            case.get("files", []), location, path.parent / "fixtures"
        )
        assertions = case.get("assertions")
        if not isinstance(assertions, list) or not assertions:
            raise ContractError(
                f"{location} assertions must be a non-empty array"
            )
        assertion_ids = set()
        for assertion_index, assertion in enumerate(assertions):
            assertion_location = f"{location} assertion #{assertion_index + 1}"
            if not isinstance(assertion, dict):
                raise ContractError(f"{assertion_location} must be an object")
            assertion_id = assertion.get("id")
            if not isinstance(assertion_id, str) or not IDENTIFIER.fullmatch(
                assertion_id
            ):
                raise ContractError(
                    f"{assertion_location} id must be a hyphen-case string"
                )
            if assertion_id in assertion_ids:
                raise ContractError(
                    f"{location} has duplicate assertion id {assertion_id!r}"
                )
            assertion_ids.add(assertion_id)
            reject_unknown_fields(
                assertion, {"id", "description"}, f"{location} assertion {assertion_id}"
            )
            description = assertion.get("description")
            if not isinstance(description, str) or not description.strip():
                raise ContractError(
                    f"{location} assertion {assertion_id} description must be a "
                    "non-empty string"
                )
    return cases


def validate_trigger_evals(path, skill_name):
    if not path.exists():
        return []
    document = load_json(path)
    if not isinstance(document, dict):
        raise ContractError(f"{path}: root must be an object")
    reject_unknown_fields(
        document, {"schema_version", "skill_name", "queries"}, str(path)
    )
    if (
        type(document.get("schema_version")) is not int
        or document["schema_version"] != SCHEMA_VERSION
    ):
        raise ContractError(f"{path}: schema_version must be {SCHEMA_VERSION}")
    if document.get("skill_name") != skill_name:
        raise ContractError(f"{path}: skill_name must be {skill_name!r}")
    queries = document.get("queries")
    if not isinstance(queries, list) or not queries:
        raise ContractError(f"{path}: queries must be a non-empty array")
    query_ids = set()
    expected = set()
    for index, query in enumerate(queries):
        location = f"{path}: query #{index + 1}"
        if not isinstance(query, dict):
            raise ContractError(f"{location} must be an object")
        query_id = query.get("id")
        if not isinstance(query_id, str) or not IDENTIFIER.fullmatch(query_id):
            raise ContractError(f"{location} id must be a hyphen-case string")
        if query_id in query_ids:
            raise ContractError(f"{path}: duplicate query id {query_id!r}")
        query_ids.add(query_id)
        location = f"{path}: query {query_id}"
        reject_unknown_fields(
            query,
            {"additional_skills", "files", "id", "query", "should_trigger"},
            location,
        )
        text = query.get("query")
        if not isinstance(text, str) or not text.strip():
            raise ContractError(f"{location} query must be a non-empty string")
        should_trigger = query.get("should_trigger")
        if not isinstance(should_trigger, bool):
            raise ContractError(f"{location} should_trigger must be boolean")
        validate_additional_skills(
            query.get("additional_skills", []), location, skill_name
        )
        validate_fixture_files(
            query.get("files", []), location, path.parent / "fixtures"
        )
        if (
            not should_trigger
            and DEICTIC_NEGATIVE_OWNER.search(text)
            and not query.get("files")
            and not query.get("additional_skills")
        ):
            raise ContractError(
                f"{location} deictic owner needs a fixture or competing skill"
            )
        expected.add(should_trigger)
    if expected != {False, True}:
        raise ContractError(
            f"{path}: queries must include should_trigger true and false"
        )
    return queries


def inspect_skill(skill_path):
    skill_dir, skill_name = validate_skill_package(skill_path)
    evals_dir = skill_dir / "evals"
    functional = validate_functional_evals(evals_dir / "evals.json", skill_name)
    trigger = validate_trigger_evals(evals_dir / "trigger-eval.json", skill_name)
    if not functional and not trigger:
        raise ContractError(f"{evals_dir}: no evaluation cases found")
    case_ids = [case["id"] for case in functional + trigger]
    if len(case_ids) != len(set(case_ids)):
        raise ContractError(f"{evals_dir}: case ids must be unique across manifests")
    return skill_name, functional, trigger


def validate_functional_result(case, response):
    results = response.get("assertions")
    if not isinstance(results, list):
        raise ContractError("adapter response assertions must be an array")
    expected_ids = {assertion["id"] for assertion in case["assertions"]}
    observed = {}
    evidence_lines = []
    for result in results:
        if not isinstance(result, dict):
            raise ContractError("adapter assertion result must be an object")
        assertion_id = result.get("id")
        if not isinstance(assertion_id, str):
            raise ContractError("adapter assertion id must be a string")
        if assertion_id in observed:
            raise ContractError(
                f"adapter returned duplicate assertion id {assertion_id!r}"
            )
        if assertion_id not in expected_ids:
            raise ContractError(
                f"adapter returned unexpected assertion id {assertion_id!r}"
            )
        status = result.get("status")
        if not isinstance(status, str) or status not in RESULT_STATUSES:
            raise ContractError(
                f"adapter assertion {assertion_id!r} has invalid status"
            )
        evidence = result.get("evidence")
        if not isinstance(evidence, str) or not evidence.strip():
            raise ContractError(
                f"adapter assertion {assertion_id!r} needs evidence"
            )
        observed[assertion_id] = status
        evidence_lines.append(
            f"  {status.upper()} {assertion_id}: {evidence.strip()}"
        )
    missing = expected_ids - observed.keys()
    if missing:
        raise ContractError(
            "adapter omitted assertion ids: " + ", ".join(sorted(missing))
        )
    if "fail" in observed.values():
        return "fail", "one or more assertions failed", evidence_lines
    if "unknown" in observed.values():
        return "unknown", "one or more assertions are unknown", evidence_lines
    return "pass", "all assertions passed", evidence_lines


def validate_trigger_result(case, response):
    activated = response.get("activated")
    if not isinstance(activated, bool):
        raise ContractError("adapter trigger response needs boolean activated")
    evidence = response.get("evidence")
    if not isinstance(evidence, str) or not evidence.strip():
        raise ContractError("adapter trigger response needs activation evidence")
    if activated == case["should_trigger"]:
        status = "pass"
        detail = "activation matched"
    else:
        status = "fail"
        detail = (
            f"expected activated={case['should_trigger']} observed={activated}"
        )
    line = (
        "  ACTIVATION "
        f"expected={str(case['should_trigger']).lower()} "
        f"observed={str(activated).lower()}: {evidence.strip()}"
    )
    return status, detail, [line]


def validate_adapter_response(case, response):
    if not isinstance(response, dict):
        raise ContractError("adapter response must be an object")
    if (
        type(response.get("protocol_version")) is not int
        or response["protocol_version"] != SCHEMA_VERSION
    ):
        raise ContractError(
            f"adapter protocol_version must be {SCHEMA_VERSION}"
        )
    if response.get("case_id") != case["id"]:
        raise ContractError("adapter case_id does not match the request")
    session_id = response.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip():
        raise ContractError("adapter response needs a session_id")
    if response.get("fresh_session") is not True:
        detail = "adapter did not attest a fresh target session"
        return "unknown", detail, [f"  UNKNOWN session: {detail}"], session_id
    if "should_trigger" in case:
        result = validate_trigger_result(case, response)
    else:
        result = validate_functional_result(case, response)
    return result[0], result[1], result[2], session_id


def stage_request(
    skill_dir, skill_name, case, workspace, iteration, *, copy_skill
):
    if copy_skill:
        staged_skill = workspace / skill_name
        copy_skill_without_evals(skill_dir, staged_skill)
    else:
        staged_skill = skill_dir
    inputs = []
    for item in case.get("files", []):
        source = skill_dir / "evals" / "fixtures" / item
        destination = workspace / "inputs" / item
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        inputs.append({"name": item, "path": str(destination)})
    staged_case = dict(case)
    staged_case.pop("files", None)
    staged_case["inputs"] = inputs
    return {
        "protocol_version": SCHEMA_VERSION,
        "skill": {
            "name": skill_name,
            "path": str(staged_skill),
            "enabled": case.get("skill_mode", "enabled") == "enabled",
        },
        "case": staged_case,
        "run": {
            "iteration": iteration,
            "fresh_session_required": True,
        },
    }


def parse_additional_skill_paths(values, evaluated_skill_name):
    paths = {}
    for value in values or []:
        if not isinstance(value, str) or "=" not in value:
            raise ContractError("--additional-skill must use NAME=PATH")
        name, raw_path = value.split("=", 1)
        if not IDENTIFIER.fullmatch(name) or not raw_path:
            raise ContractError("--additional-skill must use NAME=PATH")
        if name == evaluated_skill_name:
            raise ContractError(
                "--additional-skill must not replace the evaluated skill"
            )
        if name in paths:
            raise ContractError(f"duplicate --additional-skill name: {name}")
        skill_dir, _ = validate_skill_package(raw_path, expected_name=name)
        paths[name] = skill_dir
    return paths


def add_package_fixture_skill_paths(paths, skill_dir, cases):
    fixture_root = skill_dir / "evals" / "fixtures" / "skills"
    declared = {
        name
        for case in cases
        for name in case.get("additional_skills", [])
    }
    for name in sorted(declared):
        if name in paths:
            continue
        candidate = fixture_root / name
        if not candidate.exists():
            continue
        skill_path, _ = validate_skill_package(candidate, expected_name=name)
        paths[name] = skill_path
    return paths


def target_skill_sources(request, additional_skill_paths):
    if not request["skill"]["enabled"]:
        return {}
    sources = {
        request["skill"]["name"]: Path(request["skill"]["path"]),
    }
    for name in request["case"].get("additional_skills", []):
        source = additional_skill_paths.get(name)
        if source is None:
            raise TargetError(f"missing additional skill path: {name}")
        sources[name] = source
    return sources


def grok_sandbox_sources(
    request, additional_skill_paths, denied_source_skill_paths=()
):
    sources = [Path(request["skill"]["path"])]
    for name in request["case"].get("additional_skills", []):
        source = additional_skill_paths.get(name)
        if source is None:
            raise TargetError(f"missing additional skill path: {name}")
        sources.append(source)
    sources.extend(Path(path) for path in denied_source_skill_paths)
    return sources


def stage_target_skills(
    request,
    target,
    workspace,
    additional_skill_paths,
    denied_source_skill_paths=(),
):
    sources = target_skill_sources(request, additional_skill_paths)
    if target == "grok":
        write_grok_eval_sandbox(
            workspace,
            grok_sandbox_sources(
                request, additional_skill_paths, denied_source_skill_paths
            ),
        )
    if not sources:
        return
    target_root = workspace / TARGET_SKILL_ROOTS[target]
    target_root.mkdir(parents=True, exist_ok=True)
    for name, source in sources.items():
        copy_skill_without_evals(source, target_root / name)


def write_grok_eval_sandbox(workspace, source_skills):
    home = Path.home()
    candidates = [
        home / ".agents",
        home / ".claude",
        home / ".codex",
        home / ".grok" / "agents",
        home / ".grok" / "bundled" / "skills",
        home / ".grok" / "commands",
        home / ".grok" / "docs",
        home / ".grok" / "marketplace-cache",
        home / ".grok" / "plugins",
        home / ".grok" / "skills",
        *(Path(source).resolve() for source in source_skills),
    ]
    workspace_root = Path(workspace).resolve()
    denied = []
    for candidate in candidates:
        candidate = candidate.resolve()
        if not candidate.exists():
            continue
        try:
            candidate.relative_to(workspace_root)
        except ValueError:
            if any(
                root == candidate or root in candidate.parents
                for root in denied
            ):
                continue
            denied = [
                root for root in denied if candidate not in root.parents
            ]
            denied.append(candidate)
    grok_root = Path(workspace) / ".grok"
    grok_root.mkdir(parents=True, exist_ok=True)
    lines = [
        f"[profiles.{GROK_EVAL_SANDBOX_PROFILE}]",
        'extends = "strict"',
        "restrict_network = true",
        "deny = [",
        *(f"  {json.dumps(str(path))}," for path in denied),
        "]",
        "",
    ]
    grok_root.joinpath("sandbox.toml").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def build_candidate_prompt(target, request):
    case = request["case"]
    if "should_trigger" in case:
        return case["query"]
    prompt = case["prompt"]
    if not request["skill"]["enabled"]:
        return f"{FUNCTIONAL_EVAL_BOUNDARY}\n\n{prompt}"
    names = [request["skill"]["name"], *case.get("additional_skills", [])]
    if target == "codex":
        invocation = " ".join(f"${name}" for name in names)
    else:
        invocation = f"/{names[0]}"
        if len(names) > 1:
            invocation += "\n\nAlso apply these explicitly named skills: " + " ".join(
                f"/{name}" for name in names[1:]
            )
    return f"{invocation}\n\n{FUNCTIONAL_EVAL_BOUNDARY}\n\n{prompt}"


def claude_settings(writable):
    settings = {
        "permissions": {
            "deny": [
                "Read(~/**)",
                "Edit(~/**)",
                "WebFetch",
                "WebSearch",
                "Agent",
            ]
        }
    }
    if writable:
        settings["sandbox"] = {
            "enabled": True,
            "failIfUnavailable": True,
            "allowUnsandboxedCommands": False,
            "filesystem": {
                "denyRead": ["~/"],
                "allowRead": ["."],
            },
            "network": {"allowedDomains": []},
        }
    return settings


def claude_command_prefix(writable, grader):
    if not (
        writable
        and not grader
        and sys.platform.startswith("linux")
        and os.geteuid() == 0
    ):
        return ["claude"]
    bwrap = shutil.which("bwrap")
    if bwrap is None:
        return ["claude"]
    return [
        bwrap,
        "--die-with-parent",
        "--unshare-user",
        "--uid",
        "1000",
        "--gid",
        "1000",
        "--bind",
        "/",
        "/",
        "--dev-bind",
        "/dev",
        "/dev",
        "--proc",
        "/proc",
        "--",
        "claude",
    ]


def build_target_command(
    target,
    prompt,
    workspace,
    model,
    writable,
    *,
    reasoning_effort=None,
    grader=False,
    schema=None,
    schema_path=None,
    output_path=None,
    disable_skills=False,
):
    if target == "claude":
        if grader:
            tools = "Read,Glob,Grep"
        elif writable:
            tools = "Skill,Read,Glob,Grep,Edit,Write,Bash"
        else:
            tools = "Skill,Read,Glob,Grep"
        command = [
            *claude_command_prefix(writable, grader),
            "-p",
            prompt,
            "--output-format",
            "json" if grader else "stream-json",
            "--no-session-persistence",
            # "project" excludes the user source that owns ~/.claude/skills
            # and ~/.claude/commands, so the staged project copy is the only
            # one Claude loads; a same-name user skill would otherwise win.
            "--setting-sources",
            "project",
            "--strict-mcp-config",
            "--mcp-config",
            '{"mcpServers":{}}',
            "--no-chrome",
            "--permission-mode",
            "dontAsk",
            "--tools",
            tools,
            "--allowed-tools",
            tools,
            "--settings",
            json.dumps(claude_settings(writable and not grader), separators=(",", ":")),
        ]
        if not grader:
            command.append("--verbose")
        if grader:
            command.extend(["--json-schema", json.dumps(schema, separators=(",", ":"))])
        if disable_skills:
            command.append("--disable-slash-commands")
        if model:
            command.extend(["--model", model])
        if reasoning_effort:
            command.extend(["--effort", reasoning_effort])
        return command

    if target == "codex":
        command = [
            "codex",
            "exec",
            "--ephemeral",
            "--json",
            "--ignore-user-config",
            "--ignore-rules",
            "--skip-git-repo-check",
            "--sandbox",
            "workspace-write" if writable and not grader else "read-only",
            "--color",
            "never",
            "-C",
            str(workspace),
        ]
        if grader:
            command.extend(
                ["--output-schema", str(schema_path), "-o", str(output_path)]
            )
        if model:
            command.extend(["--model", model])
        if reasoning_effort:
            command.extend(
                ["-c", f'model_reasoning_effort="{reasoning_effort}"']
            )
        command.append(prompt)
        return command

    tools = "read_file,grep,list_dir" if grader or not writable else (
        "run_terminal_cmd,grep,read_file,search_replace,list_dir"
    )
    home = Path.home()
    command = [
        "grok",
        "-p",
        prompt,
        "--cwd",
        str(workspace),
        "--output-format",
        "streaming-messages-json",
        "--no-memory",
        "--no-subagents",
        "--disable-web-search",
        "--sandbox",
        GROK_EVAL_SANDBOX_PROFILE,
        "--permission-mode",
        "bypassPermissions",
        "--reasoning-effort",
        reasoning_effort,
        "--deny",
        f"Read({home}/**)",
        "--deny",
        f"Grep({home}/**)",
        "--deny",
        f"Bash(*{home}*)",
        "--tools",
        tools,
    ]
    if grader:
        command.append("--no-plan")
    if model:
        command.extend(["--model", model])
    return command


def target_output_summary(stdout, stderr, workspace):
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", errors="replace")
    stdout = stdout or ""
    stderr = stderr or ""
    event_types = {}
    tool_calls = {}
    tool_results = {}
    tool_targets = {}
    invalid_json_lines = 0
    json_events = 0
    last_stop_reason = None
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            invalid_json_lines += 1
            continue
        if not isinstance(event, dict):
            invalid_json_lines += 1
            continue
        json_events += 1
        event_type = event.get("type")
        if isinstance(event_type, str) and event_type:
            event_types[event_type] = event_types.get(event_type, 0) + 1
        message = event.get("message")
        if isinstance(message, dict):
            content = message.get("content")
            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict):
                        continue
                    if block.get("type") == "tool_result":
                        result_status = (
                            "error" if block.get("is_error") is True else "ok"
                        )
                        tool_results[result_status] = (
                            tool_results.get(result_status, 0) + 1
                        )
                        continue
                    if block.get("type") != "tool_use":
                        continue
                    tool_name = block.get("name")
                    if not isinstance(tool_name, str) or not tool_name:
                        tool_name = "unknown"
                    tool_calls[tool_name] = tool_calls.get(tool_name, 0) + 1
                    inputs = block.get("input")
                    if isinstance(inputs, dict):
                        for key in (
                            "target_file",
                            "target_directory",
                            "path",
                            "directory",
                        ):
                            value = inputs.get(key)
                            if not isinstance(value, str) or not value:
                                continue
                            candidate = Path(value)
                            if not candidate.is_absolute():
                                candidate = Path(workspace, candidate)
                            try:
                                relative = candidate.resolve().relative_to(
                                    Path(workspace).resolve()
                                )
                            except (OSError, RuntimeError, ValueError):
                                target = "<outside-workspace>"
                            else:
                                target = str(relative) or "."
                            target = re.sub(
                                r"[^A-Za-z0-9._/+<>-]", "?", target
                            )
                            tool_targets[target] = (
                                tool_targets.get(target, 0) + 1
                            )
                            break
            message_stop_reason = message.get("stop_reason") or message.get(
                "stopReason"
            )
            if isinstance(message_stop_reason, str) and message_stop_reason:
                last_stop_reason = message_stop_reason
        event_stop_reason = event.get("stop_reason") or event.get("stopReason")
        if isinstance(event_stop_reason, str) and event_stop_reason:
            last_stop_reason = event_stop_reason
    type_summary = ",".join(
        f"{name}:{count}" for name, count in sorted(event_types.items())
    ) or "none"
    tool_summary = ",".join(
        f"{name}:{count}" for name, count in sorted(tool_calls.items())
    ) or "none"
    result_summary = ",".join(
        f"{name}:{count}" for name, count in sorted(tool_results.items())
    ) or "none"
    target_items = sorted(tool_targets.items())
    target_summary = ",".join(
        f"{name}:{count}" for name, count in target_items[:12]
    ) or "none"
    if len(target_items) > 12:
        target_summary += f",other:{len(target_items) - 12}"
    stop_summary = last_stop_reason or "none"
    return (
        f"stdout_bytes={len(stdout.encode())} "
        f"stderr_bytes={len(stderr.encode())} json_events={json_events} "
        f"invalid_json_lines={invalid_json_lines} event_types={type_summary} "
        f"tool_calls={tool_summary} tool_results={result_summary} "
        f"tool_targets={target_summary} "
        f"last_stop_reason={stop_summary}"
    )


def target_metrics(stdout):
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    metrics = {
        "num_turns": None,
        "target_api_duration_ms": None,
        "target_duration_ms": None,
        "total_cost_usd": None,
        "total_tokens": None,
        "usage": {},
    }
    for line in (stdout or "").splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        usage = event.get("usage")
        if isinstance(usage, dict):
            filtered = {
                key: value
                for key, value in usage.items()
                if key in TOKEN_FIELDS
                and isinstance(value, (int, float))
                and not isinstance(value, bool)
            }
            if filtered:
                metrics["usage"] = filtered
        for source, destination in (
            ("duration_ms", "target_duration_ms"),
            ("duration_api_ms", "target_api_duration_ms"),
            ("total_cost_usd", "total_cost_usd"),
            ("num_turns", "num_turns"),
        ):
            value = event.get(source)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                metrics[destination] = value
    usage = metrics["usage"]
    if "total_tokens" in usage:
        metrics["total_tokens"] = usage["total_tokens"]
    elif "input_tokens" in usage and "output_tokens" in usage:
        metrics["total_tokens"] = usage["input_tokens"] + usage["output_tokens"]
    return metrics


def record_phase_observation(
    phase_records,
    phase,
    status,
    stdout,
    stderr,
    elapsed_ms,
    workspace,
):
    if phase_records is None:
        return
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", errors="replace")
    stdout = stdout or ""
    stderr = stderr or ""
    phase_records[phase] = {
        "elapsed_ms": elapsed_ms,
        "metrics": target_metrics(stdout),
        "status": status,
        "stderr": stderr,
        "stdout": stdout,
        "summary": target_output_summary(stdout, stderr, workspace),
    }


def run_target_process(
    target, command, workspace, timeout, observe=None, stop_when=None
):
    if timeout <= 0:
        raise TargetError("target case timed out")
    environment = None
    if target == "grok":
        environment = os.environ.copy()
        environment["GROK_DISABLE_AUTOUPDATER"] = "1"
    popen_options = {}
    if os.name == "posix":
        popen_options["start_new_session"] = True
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=workspace,
            env=environment,
            **popen_options,
        )
        deadline = time.monotonic() + timeout
        timeout_error = None
        stopped_early = False
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timeout_error = subprocess.TimeoutExpired(command, timeout)
                break
            try:
                stdout, stderr = process.communicate(
                    timeout=min(TARGET_OBSERVATION_INTERVAL, remaining)
                )
                timeout_error = None
                break
            except subprocess.TimeoutExpired as error:
                timeout_error = error
                if observe is not None:
                    observe(
                        error.stdout or "",
                        error.stderr or "",
                        time.monotonic(),
                    )
                if stop_when is not None and stop_when(
                    error.stdout or "", error.stderr or ""
                ):
                    stopped_early = True
                    break
                if time.monotonic() >= deadline:
                    break
        if timeout_error is not None:
            error = timeout_error
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=TARGET_TERMINATION_GRACE)
                except subprocess.TimeoutExpired:
                    pass
                try:
                    os.killpg(process.pid, 0)
                except ProcessLookupError:
                    pass
                else:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
            else:
                process.kill()
            try:
                stdout, stderr = process.communicate(
                    timeout=TARGET_TERMINATION_GRACE
                )
            except subprocess.TimeoutExpired as cleanup_error:
                stdout = (
                    cleanup_error.stdout
                    if cleanup_error.stdout is not None
                    else error.stdout
                )
                stderr = (
                    cleanup_error.stderr
                    if cleanup_error.stderr is not None
                    else error.stderr
                )
                for stream in (process.stdout, process.stderr):
                    if stream is not None:
                        stream.close()
                if process.poll() is None:
                    process.kill()
                    try:
                        process.wait(timeout=TARGET_TERMINATION_GRACE)
                    except subprocess.TimeoutExpired:
                        pass
            if not stopped_early:
                if observe is not None:
                    observe(stdout, stderr, time.monotonic())
                summary = target_output_summary(stdout, stderr, workspace)
                raise TargetError(f"{target} timed out; {summary}") from error
    except OSError as error:
        raise TargetError(f"{target} could not start: {error}") from error
    completed = subprocess.CompletedProcess(
        command,
        process.returncode,
        stdout,
        stderr,
    )
    output_size = len(completed.stdout.encode()) + len(completed.stderr.encode())
    if output_size > TARGET_OUTPUT_LIMIT:
        if observe is not None:
            observe(completed.stdout, completed.stderr, time.monotonic())
        raise TargetError(
            f"{target} output exceeded {TARGET_OUTPUT_LIMIT} bytes"
        )
    if completed.returncode != 0 and not stopped_early:
        if observe is not None:
            observe(completed.stdout, completed.stderr, time.monotonic())
        detail = completed.stderr.strip() or completed.stdout.strip()
        if not detail:
            detail = f"exit {completed.returncode}"
        raise TargetError(f"{target} failed: {detail[:2000]}")
    return completed, stopped_early


def run_observed_target_phase(
    target,
    phase,
    case_id,
    iteration,
    command,
    workspace,
    timeout,
    stop_when=None,
    phase_records=None,
):
    prefix = (
        f"OBSERVE case={case_id} iteration={iteration} "
        f"target={target} phase={phase}"
    )
    print(
        f"{prefix} status=start timeout_ms={max(0, round(timeout * 1000))}",
        file=sys.stderr,
        flush=True,
    )
    started = time.monotonic()

    def observe(stdout, stderr, observed_at):
        elapsed_ms = round((observed_at - started) * 1000)
        summary = target_output_summary(stdout, stderr, workspace)
        record_phase_observation(
            phase_records,
            phase,
            "progress",
            stdout,
            stderr,
            elapsed_ms,
            workspace,
        )
        print(
            f"{prefix} status=progress elapsed_ms={elapsed_ms} {summary}",
            file=sys.stderr,
            flush=True,
        )

    try:
        completed, stopped_early = run_target_process(
            target,
            command,
            workspace,
            timeout,
            observe=observe,
            stop_when=stop_when,
        )
    except TargetError as error:
        elapsed_ms = round((time.monotonic() - started) * 1000)
        previous = (phase_records or {}).get(phase, {})
        record_phase_observation(
            phase_records,
            phase,
            "process_error",
            previous.get("stdout", ""),
            previous.get("stderr", ""),
            elapsed_ms,
            workspace,
        )
        print(
            f"{prefix} status=process_error elapsed_ms={elapsed_ms}",
            file=sys.stderr,
            flush=True,
        )
        raise TargetError(f"{phase} process: {error}") from error
    elapsed_ms = round((time.monotonic() - started) * 1000)
    summary = target_output_summary(
        completed.stdout, completed.stderr, workspace
    )
    status = "observed" if stopped_early else "complete"
    record_phase_observation(
        phase_records,
        phase,
        status,
        completed.stdout,
        completed.stderr,
        elapsed_ms,
        workspace,
    )
    print(
        f"{prefix} status={status} elapsed_ms={elapsed_ms} {summary}",
        file=sys.stderr,
        flush=True,
    )
    return completed, stopped_early


def parse_json_lines(text, target):
    events = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            raise TargetError(
                f"{target} emitted invalid JSON on line {line_number}: {error}"
            ) from error
        if not isinstance(event, dict):
            raise TargetError(
                f"{target} emitted a non-object event on line {line_number}"
            )
        events.append(event)
    if not events:
        raise TargetError(f"{target} emitted no JSON events")
    return events


def parse_candidate_output(target, completed):
    events = parse_json_lines(completed.stdout, target)
    if target == "codex":
        starts = [event for event in events if event.get("type") == "thread.started"]
        if len(starts) != 1:
            raise TargetError("codex did not emit exactly one thread.started event")
        session_id = starts[0].get("thread_id")
        if not isinstance(session_id, str) or not session_id.strip():
            raise TargetError("codex thread.started did not include a thread_id")
        if any(event.get("type") in {"error", "turn.failed"} for event in events):
            raise TargetError("codex event stream reported a failed turn")
        if not any(event.get("type") == "turn.completed" for event in events):
            raise TargetError("codex did not emit turn.completed")
        messages = [
            event.get("item", {}).get("text")
            for event in events
            if event.get("type") == "item.completed"
            and event.get("item", {}).get("type") == "agent_message"
        ]
        final_text = next(
            (message for message in reversed(messages) if isinstance(message, str)),
            "",
        )
        init = None
    else:
        results = [event for event in events if event.get("type") == "result"]
        if len(results) != 1:
            raise TargetError(f"{target} did not emit exactly one result event")
        result = results[0]
        if result.get("is_error") is True or result.get("subtype") not in {
            None,
            "success",
        }:
            raise TargetError(f"{target} result reported an error")
        session_id = result.get("session_id") or result.get("sessionId")
        if not isinstance(session_id, str) or not session_id.strip():
            raise TargetError(f"{target} result did not include a session id")
        event_session_ids = {
            event.get("session_id") or event.get("sessionId")
            for event in events
            if event.get("session_id") or event.get("sessionId")
        }
        if event_session_ids != {session_id}:
            raise TargetError(f"{target} event stream mixed session ids")
        final_text = result.get("result", "")
        if target == "grok":
            stop_reason = result.get("stop_reason") or result.get(
                "stopReason"
            )
            if stop_reason != "end_turn":
                raise TargetError(
                    f"grok result did not finish with end_turn: {stop_reason!r}"
                )
            if not isinstance(final_text, str):
                raise TargetError("grok result text must be a string")
            if not final_text.strip():
                end_turn_texts = []
                for event in events:
                    if event.get("type") != "assistant":
                        continue
                    message = event.get("message")
                    if not isinstance(message, dict):
                        continue
                    message_stop = message.get("stop_reason") or message.get(
                        "stopReason"
                    )
                    if message_stop != "end_turn":
                        continue
                    content = message.get("content")
                    if not isinstance(content, list):
                        continue
                    text_blocks = [
                        block.get("text")
                        for block in content
                        if isinstance(block, dict)
                        and block.get("type") == "text"
                        and isinstance(block.get("text"), str)
                    ]
                    text = "".join(text_blocks)
                    if text.strip():
                        end_turn_texts.append(text)
                if len(end_turn_texts) != 1:
                    raise TargetError(
                        "grok did not emit exactly one textual end_turn response"
                    )
                final_text = end_turn_texts[0]
        init = next(
            (
                event
                for event in events
                if event.get("type") == "system"
                and event.get("subtype") == "init"
            ),
            None,
        )
    return {
        "events": events,
        "final_text": final_text,
        "init": init,
        "session_id": session_id,
        "stderr": completed.stderr,
        "stdout": completed.stdout,
    }


def parse_target_observation(target, stdout, stderr):
    if target not in {"claude", "grok"}:
        raise TargetError(f"{target} has no attributable trigger observation")
    if isinstance(stdout, bytes):
        stdout = stdout.decode("utf-8", errors="replace")
    if isinstance(stderr, bytes):
        stderr = stderr.decode("utf-8", errors="replace")
    stdout = stdout or ""
    stderr = stderr or ""
    events = parse_json_lines(stdout, target)
    init_events = [
        event
        for event in events
        if event.get("type") == "system" and event.get("subtype") == "init"
    ]
    if len(init_events) != 1:
        raise TargetError(f"{target} did not emit exactly one system/init event")
    init = init_events[0]
    session_id = init.get("session_id") or init.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        raise TargetError(f"{target} system/init did not include a session id")
    event_session_ids = {
        event.get("session_id") or event.get("sessionId")
        for event in events
        if event.get("session_id") or event.get("sessionId")
    }
    if event_session_ids != {session_id}:
        raise TargetError(f"{target} observation stream mixed session ids")
    return {
        "events": events,
        "final_text": "",
        "init": init,
        "session_id": session_id,
        "stderr": stderr,
        "stdout": stdout,
    }


def parse_grok_observation(stdout, stderr):
    return parse_target_observation("grok", stdout, stderr)


def normalized_catalog_names(values):
    names = set()
    if not isinstance(values, list):
        return names
    for value in values:
        if isinstance(value, dict):
            value = value.get("name")
        if not isinstance(value, str):
            continue
        name = value.strip().lstrip("/")
        if name:
            names.add(name)
            names.add(name.rsplit(":", 1)[-1])
    return names


def observe_claude_activation(candidate, skill_name):
    for event in candidate["events"]:
        if event.get("type") != "assistant":
            continue
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if str(block.get("name", "")).lower() != "skill":
                continue
            inputs = block.get("input")
            if not isinstance(inputs, dict):
                continue
            invoked = inputs.get("skill") or inputs.get("name") or inputs.get(
                "command"
            )
            if not isinstance(invoked, str):
                continue
            normalized = invoked.strip().lstrip("/").rsplit(":", 1)[-1]
            if normalized == skill_name:
                return True, f"Claude Skill tool invoked {invoked!r}"
    init = candidate.get("init")
    if not isinstance(init, dict):
        return None, "Claude emitted no system/init skill catalog"
    offered = normalized_catalog_names(init.get("skills"))
    offered.update(normalized_catalog_names(init.get("slash_commands")))
    if skill_name not in offered:
        return None, f"Claude init did not advertise {skill_name!r}"
    return (
        False,
        f"Claude advertised {skill_name!r} and emitted no matching Skill tool call",
    )


def observe_grok_activation(candidate, skill_name, workspace):
    init = candidate.get("init")
    if not isinstance(init, dict):
        return None, "Grok emitted no system/init skill catalog"
    offered = normalized_catalog_names(init.get("skills"))
    offered.update(normalized_catalog_names(init.get("slash_commands")))
    if skill_name not in offered:
        return None, f"Grok init did not advertise {skill_name!r}"

    expected = (
        Path(workspace) / TARGET_SKILL_ROOTS["grok"] / skill_name / "SKILL.md"
    ).resolve()
    for event in candidate["events"]:
        if event.get("type") != "assistant":
            continue
        message = event.get("message")
        if not isinstance(message, dict):
            continue
        content = message.get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            if str(block.get("name", "")).lower() != "read_file":
                continue
            inputs = block.get("input")
            if not isinstance(inputs, dict):
                continue
            target_file = inputs.get("target_file") or inputs.get("path")
            if not isinstance(target_file, str) or not target_file:
                continue
            observed = Path(target_file)
            if not observed.is_absolute():
                observed = Path(workspace) / observed
            try:
                observed = observed.resolve()
            except (OSError, RuntimeError):
                continue
            if observed == expected:
                relative = expected.relative_to(Path(workspace).resolve())
                return True, f"Grok read staged {str(relative)!r}"
    return (
        False,
        f"Grok advertised {skill_name!r} and emitted no matching read_file call",
    )


def observe_target_activation(target, candidate, skill_name, workspace):
    if target == "claude":
        return observe_claude_activation(candidate, skill_name)
    if target == "grok":
        return observe_grok_activation(candidate, skill_name, workspace)
    return None, f"{target} exposes no attributable automatic skill activation event"


def workspace_state(workspace, excluded_roots):
    state = {}
    for path in sorted(workspace.rglob("*")):
        relative = path.relative_to(workspace)
        if relative.parts and relative.parts[0] in excluded_roots:
            continue
        mode = path.lstat().st_mode
        if stat.S_ISLNK(mode):
            raise TargetError(f"candidate created unsupported symlink: {relative}")
        if stat.S_ISDIR(mode):
            continue
        if not stat.S_ISREG(mode):
            raise TargetError(
                f"candidate created unsupported special file: {relative}"
            )
        try:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as error:
            raise TargetError(
                f"could not snapshot candidate file {relative}: {error}"
            ) from error
        state[str(relative)] = digest
    return state


def copy_candidate_snapshot(workspace, destination, excluded_roots):
    workspace = workspace.resolve()

    def ignore_target_context(source, names):
        if Path(source).resolve() == workspace:
            return set(names).intersection(excluded_roots)
        return set()

    shutil.copytree(
        workspace,
        destination,
        ignore=ignore_target_context,
        symlinks=True,
    )


def prepare_artifacts_root(value, skill_dir):
    if value is None:
        return None
    root = Path(value).expanduser().resolve()
    if root.exists():
        raise ContractError(f"--artifacts-dir already exists: {root}")
    try:
        root.relative_to(skill_dir)
    except ValueError:
        pass
    else:
        raise ContractError("--artifacts-dir must be outside the skill package")
    try:
        root.mkdir(parents=True)
    except OSError as error:
        raise ContractError(f"could not create --artifacts-dir {root}: {error}") from error
    return root


def sanitized_phase_records(phase_records):
    sanitized = {}
    for phase, record in sorted((phase_records or {}).items()):
        sanitized[phase] = {
            "status": record["status"],
            "wall_duration_ms": record["elapsed_ms"],
            "stdout_bytes": len(record["stdout"].encode()),
            "stderr_bytes": len(record["stderr"].encode()),
            "summary": record["summary"],
            "metrics": record["metrics"],
        }
    return sanitized


def result_reason_code(case, status, phases):
    if status == "pass":
        return "passed"
    if status == "fail":
        return (
            "activation_mismatch"
            if "should_trigger" in case
            else "assertion_failed"
        )
    for phase, record in phases.items():
        if record["status"] == "process_error":
            return f"{phase}_process_error"
    if "grader" in phases:
        return "grader_protocol_or_evidence_unknown"
    if "candidate" in phases:
        return "candidate_protocol_or_evidence_unknown"
    return "unverifiable"


def validate_report_destination(value, skill_dir):
    if value is None:
        return None
    destination = Path(value).expanduser().resolve()
    if destination.exists():
        raise ContractError(f"--report already exists: {destination}")
    try:
        destination.relative_to(skill_dir)
    except ValueError:
        pass
    else:
        raise ContractError("--report must be outside the skill package")
    if not destination.parent.is_dir():
        raise ContractError(f"--report parent directory not found: {destination.parent}")
    return destination


def write_run_report(document, destination=None):
    encoded = (json.dumps(document, indent=2, sort_keys=True) + "\n").encode()
    try:
        if destination is None:
            descriptor, raw_path = tempfile.mkstemp(
                prefix="skill-eval-report-", suffix=".json"
            )
            path = Path(raw_path)
        else:
            path = destination
            descriptor = os.open(
                path,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                0o600,
            )
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(encoded)
    except OSError as error:
        raise ContractError(f"could not write eval report: {error}") from error
    print(f"REPORT path={json.dumps(str(path))}")
    return path


def validate_report_case_results(path, cases, repeat, summary):
    if not isinstance(cases, list) or not cases:
        raise ContractError(f"{path}: invalid report case results")
    observed_case_ids = set()
    observed_summary = {status: 0 for status in RESULT_STATUSES}
    phase_fields = {
        "metrics",
        "status",
        "stderr_bytes",
        "stdout_bytes",
        "summary",
        "wall_duration_ms",
    }
    for case in cases:
        if not isinstance(case, dict) or set(case) != {
            "case_id",
            "iterations",
            "kind",
            "status",
        }:
            raise ContractError(f"{path}: invalid report case results")
        case_id = case.get("case_id")
        if (
            not isinstance(case_id, str)
            or not IDENTIFIER.fullmatch(case_id)
            or case_id in observed_case_ids
            or case.get("kind") not in {"functional", "trigger"}
            or case.get("status") not in RESULT_STATUSES
        ):
            raise ContractError(f"{path}: invalid report case results")
        observed_case_ids.add(case_id)
        iterations = case.get("iterations")
        if not isinstance(iterations, list) or not iterations:
            raise ContractError(f"{path}: invalid report case results")
        statuses = []
        observed_iterations = set()
        for iteration in iterations:
            if not isinstance(iteration, dict) or set(iteration) != {
                "iteration",
                "phases",
                "reason_code",
                "status",
            }:
                raise ContractError(f"{path}: invalid report case results")
            number = iteration.get("iteration")
            reason = iteration.get("reason_code")
            status = iteration.get("status")
            phases = iteration.get("phases")
            if (
                type(number) is not int
                or number < 1
                or number > repeat
                or number in observed_iterations
                or status not in RESULT_STATUSES
                or not isinstance(reason, str)
                or not reason
                or "\n" in reason
                or "\r" in reason
                or not isinstance(phases, dict)
            ):
                raise ContractError(f"{path}: invalid report case results")
            observed_iterations.add(number)
            statuses.append(status)
            for phase, record in phases.items():
                if (
                    phase not in {"candidate", "grader"}
                    or not isinstance(record, dict)
                    or set(record) != phase_fields
                    or record.get("status")
                    not in {"complete", "observed", "process_error", "progress"}
                    or any(
                        type(record.get(field)) is not int or record[field] < 0
                        for field in (
                            "stderr_bytes",
                            "stdout_bytes",
                            "wall_duration_ms",
                        )
                    )
                    or not isinstance(record.get("summary"), str)
                    or "\n" in record["summary"]
                    or "\r" in record["summary"]
                    or not isinstance(record.get("metrics"), dict)
                ):
                    raise ContractError(f"{path}: invalid report case results")
        if case["kind"] == "functional":
            for status in statuses:
                observed_summary[status] += 1
            if "fail" in statuses:
                expected_status = "fail"
            elif "unknown" in statuses:
                expected_status = "unknown"
            else:
                expected_status = "pass"
        else:
            required_correct = repeat // 2 + 1
            if statuses.count("pass") >= required_correct:
                expected_status = "pass"
            elif statuses.count("fail") >= required_correct:
                expected_status = "fail"
            else:
                expected_status = "unknown"
            observed_summary[expected_status] += 1
        if case["status"] != expected_status:
            raise ContractError(f"{path}: invalid report case results")
    if summary != observed_summary:
        raise ContractError(f"{path}: report summary does not match case results")


def load_run_report(value):
    path = Path(value).expanduser().resolve()
    document = load_json(path)
    if not isinstance(document, dict):
        raise ContractError(f"{path}: report root must be an object")
    required = {"cases", "kind", "run", "schema_version", "skill", "summary", "target"}
    if set(document) != required:
        raise ContractError(f"{path}: invalid eval report fields")
    if (
        type(document.get("schema_version")) is not int
        or document["schema_version"] != SCHEMA_VERSION
    ):
        raise ContractError(f"{path}: unsupported eval report schema")
    if document.get("kind") != "skill-eval-run":
        raise ContractError(f"{path}: not a skill eval run report")
    skill = document.get("skill")
    target = document.get("target")
    run = document.get("run")
    cases = document.get("cases")
    summary = document.get("summary")
    if not isinstance(skill, dict) or set(skill) != {"name", "package_sha256", "source_path"}:
        raise ContractError(f"{path}: invalid report skill metadata")
    if not all(isinstance(skill.get(key), str) and skill[key] for key in skill):
        raise ContractError(f"{path}: invalid report skill metadata")
    if (
        not IDENTIFIER.fullmatch(skill["name"])
        or not re.fullmatch(r"[0-9a-f]{64}", skill["package_sha256"])
    ):
        raise ContractError(f"{path}: invalid report skill metadata")
    if not isinstance(target, dict) or set(target) != {"model", "name", "reasoning_effort"}:
        raise ContractError(f"{path}: invalid report target metadata")
    if target.get("name") not in TARGETS | {"external-adapter"}:
        raise ContractError(f"{path}: invalid report target")
    if not all(isinstance(target.get(key), str) and target[key] for key in target):
        raise ContractError(f"{path}: invalid report target metadata")
    expected_run_fields = {
        "additional_skills",
        "fail_fast",
        "repeat",
        "scope",
        "selected_case_ids",
        "timeout_seconds",
    }
    if not isinstance(run, dict) or set(run) != expected_run_fields:
        raise ContractError(f"{path}: invalid report run metadata")
    if run.get("scope") not in {"run", "run-all", "run-one"}:
        raise ContractError(f"{path}: invalid report run scope")
    if type(run.get("repeat")) is not int or run["repeat"] < 1:
        raise ContractError(f"{path}: invalid report repeat")
    if not isinstance(run.get("timeout_seconds"), (int, float)) or isinstance(
        run["timeout_seconds"], bool
    ) or run["timeout_seconds"] <= 0:
        raise ContractError(f"{path}: invalid report timeout")
    selected = run.get("selected_case_ids")
    if selected is not None and (
        not isinstance(selected, list)
        or any(
            not isinstance(item, str) or not IDENTIFIER.fullmatch(item)
            for item in selected
        )
        or len(selected) != len(set(selected))
    ):
        raise ContractError(f"{path}: invalid report case selection")
    if not isinstance(run.get("fail_fast"), bool):
        raise ContractError(f"{path}: invalid report fail-fast setting")
    additional = run.get("additional_skills")
    if not isinstance(additional, list) or any(
        not isinstance(item, dict)
        or set(item) != {"name", "package_sha256", "source_path"}
        or any(not isinstance(item.get(key), str) or not item[key] for key in item)
        for item in additional
    ):
        raise ContractError(f"{path}: invalid report additional skills")
    if len({item["name"] for item in additional}) != len(additional) or any(
        not IDENTIFIER.fullmatch(item["name"])
        or not re.fullmatch(r"[0-9a-f]{64}", item["package_sha256"])
        for item in additional
    ):
        raise ContractError(f"{path}: invalid report additional skills")
    if not isinstance(summary, dict):
        raise ContractError(f"{path}: invalid report results")
    if set(summary) != RESULT_STATUSES or any(
        type(summary.get(status)) is not int or summary[status] < 0
        for status in RESULT_STATUSES
    ):
        raise ContractError(f"{path}: invalid report summary")
    validate_report_case_results(path, cases, run["repeat"], summary)
    return document


def inspect_run_report(document):
    skill = document["skill"]
    target = document["target"]
    run = document["run"]
    summary = document["summary"]
    print(
        f"RUN skill={skill['name']} sha256={skill['package_sha256']} "
        f"target={target['name']} model={target['model']} "
        f"effort={target['reasoning_effort']} scope={run['scope']}"
    )
    for case in document["cases"]:
        print(f"CASE {case['case_id']} status={case['status']}")
        for iteration in case["iterations"]:
            print(
                f"  ITERATION {iteration['iteration']} status={iteration['status']} "
                f"reason={iteration['reason_code']}"
            )
            for phase, record in iteration["phases"].items():
                print(
                    f"    PHASE {phase} status={record['status']} "
                    f"elapsed_ms={record['wall_duration_ms']} {record['summary']}"
                )
    print(
        f"SUMMARY pass={summary['pass']} fail={summary['fail']} "
        f"unknown={summary['unknown']}"
    )


def rerun_from_report(document):
    target = document["target"]
    if target["name"] not in TARGETS:
        raise ContractError("report uses an external adapter and cannot be rerun")
    run = document["run"]
    additional = run["additional_skills"]
    return run_evaluations(
        document["skill"]["source_path"],
        [],
        target["name"],
        target["model"],
        target["reasoning_effort"],
        [f"{item['name']}={item['source_path']}" for item in additional],
        run["repeat"],
        run["timeout_seconds"],
        run["selected_case_ids"],
        None,
        run["fail_fast"],
        report_scope=run["scope"],
        expected_package_digest=document["skill"]["package_sha256"],
        expected_additional_digests={
            item["name"]: item["package_sha256"] for item in additional
        },
    )


def write_case_result_metadata(destination, case, iteration, result):
    destination.joinpath("eval-result.json").write_text(
        json.dumps(
            {
                "schema_version": SCHEMA_VERSION,
                "case_id": case["id"],
                "iteration": iteration,
                "status": result[0],
                "detail": result[1],
                "evidence": result[2],
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def write_phase_artifacts(destination, phase_records):
    if not phase_records:
        return
    observation = destination / "observation"
    observation.mkdir()
    for phase, record in sorted(phase_records.items()):
        observation.joinpath(f"{phase}-events.jsonl").write_text(
            record["stdout"], encoding="utf-8"
        )
        observation.joinpath(f"{phase}-stderr.txt").write_text(
            record["stderr"], encoding="utf-8"
        )
        metrics = dict(record["metrics"])
        timing = {
            "schema_version": SCHEMA_VERSION,
            "status": record["status"],
            "wall_duration_ms": record["elapsed_ms"],
            "stdout_bytes": len(record["stdout"].encode()),
            "stderr_bytes": len(record["stderr"].encode()),
            "summary": record["summary"],
            **metrics,
        }
        observation.joinpath(f"{phase}-timing.json").write_text(
            json.dumps(timing, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def save_case_artifacts(
    workspace, artifacts_root, case, iteration, result, phase_records
):
    destination = artifacts_root / case["id"] / f"iteration-{iteration}"
    excluded_roots = {".agents", ".claude", ".git", ".grok"}
    workspace_state(workspace, excluded_roots)
    destination.parent.mkdir(parents=True, exist_ok=True)
    copy_candidate_snapshot(workspace, destination, excluded_roots)
    write_case_result_metadata(destination, case, iteration, result)
    write_phase_artifacts(destination, phase_records)
    print(
        f"OBSERVE case={case['id']} iteration={iteration} "
        f"phase=artifacts status=saved path={json.dumps(str(destination))}",
        file=sys.stderr,
        flush=True,
    )


def grading_schema(case):
    assertion_ids = [assertion["id"] for assertion in case["assertions"]]
    return {
        "type": "object",
        "properties": {
            "assertions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "enum": assertion_ids},
                        "status": {
                            "type": "string",
                            "enum": sorted(RESULT_STATUSES),
                        },
                        "evidence": {"type": "string", "minLength": 1},
                    },
                    "required": ["id", "status", "evidence"],
                    "additionalProperties": False,
                },
            }
        },
        "required": ["assertions"],
        "additionalProperties": False,
    }


def build_grader_prompt(case):
    rubric = json.dumps(case["assertions"], indent=2, ensure_ascii=False)
    assertion_ids = ", ".join(
        assertion["id"] for assertion in case["assertions"]
    )
    return (
        "You are the independent grader for one completed skill evaluation. "
        "Do not modify any file and do not invoke any skill. Inspect the read-only "
        "candidate/ snapshot, before.json, after.json, target-events.jsonl, "
        "target-stderr.txt, and final-response.txt. Grade only the assertions below. "
        "Complete every inspection before emitting the structured object. Do not "
        "return a progress update, plan, or statement of intent as a verdict. "
        f"The assertions array must contain exactly {len(case['assertions'])} "
        f"results in this order: {assertion_ids}. Do not omit or combine results. "
        "Use pass only for direct evidence, fail for contradictory evidence, and "
        "unknown when the available artifacts cannot decide the assertion. Return "
        "exactly the requested structured object with one result per assertion.\n\n"
        f"Case id: {case['id']}\n"
        f"Original task: {case['prompt']}\n\n"
        f"Assertions:\n{rubric}\n"
    )


def parse_grader_output(target, completed, output_path=None):
    if target == "codex":
        candidate = parse_candidate_output(target, completed)
        try:
            structured = json.loads(Path(output_path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as error:
            raise TargetError(f"codex grader output is invalid: {error}") from error
        return candidate["session_id"], structured
    if target == "grok":
        candidate = parse_candidate_output(target, completed)
        final_text = candidate["final_text"]
        if not isinstance(final_text, str):
            raise TargetError("grok grader final response must be text")
        document = final_text.strip()
        fenced = re.fullmatch(
            r"```json[ \t]*\r?\n(?P<body>.*)\r?\n```",
            document,
            re.DOTALL | re.IGNORECASE,
        )
        if fenced is not None:
            document = fenced.group("body")
        try:
            structured = json.loads(document)
        except json.JSONDecodeError as error:
            raise TargetError(
                f"grok grader final response is invalid JSON: {error}"
            ) from error
        if not isinstance(structured, dict):
            raise TargetError("grok grader final response must be a JSON object")
        return candidate["session_id"], structured
    try:
        document = json.loads(completed.stdout)
    except json.JSONDecodeError as error:
        raise TargetError(f"{target} grader emitted invalid JSON: {error}") from error
    if not isinstance(document, dict):
        raise TargetError(f"{target} grader output must be an object")
    if document.get("is_error") is True:
        raise TargetError(f"{target} grader reported an error")
    session_id = document.get("session_id") or document.get("sessionId")
    if not isinstance(session_id, str) or not session_id.strip():
        raise TargetError(f"{target} grader did not include a session id")
    structured = document.get("structured_output")
    if not isinstance(structured, dict):
        raise TargetError(f"{target} grader omitted structured output")
    return session_id, structured


def grade_functional_case(
    target,
    model,
    reasoning_effort,
    case,
    workspace,
    candidate,
    before_state,
    after_state,
    deadline,
    iteration,
    phase_records,
    source_skills=(),
):
    excluded_roots = {".agents", ".claude", ".git", ".grok"}
    with tempfile.TemporaryDirectory(
        prefix=f"skill-eval-grader-{case['id']}-"
    ) as temp_dir:
        grader_workspace = Path(temp_dir)
        copy_candidate_snapshot(
            workspace, grader_workspace / "candidate", excluded_roots
        )
        grader_workspace.joinpath("before.json").write_text(
            json.dumps(before_state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        grader_workspace.joinpath("after.json").write_text(
            json.dumps(after_state, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        grader_workspace.joinpath("target-events.jsonl").write_text(
            candidate["stdout"], encoding="utf-8"
        )
        grader_workspace.joinpath("target-stderr.txt").write_text(
            candidate["stderr"], encoding="utf-8"
        )
        grader_workspace.joinpath("final-response.txt").write_text(
            str(candidate["final_text"]), encoding="utf-8"
        )
        schema = grading_schema(case)
        schema_path = grader_workspace / "grading-schema.json"
        output_path = grader_workspace / "grading-result.json"
        schema_path.write_text(
            json.dumps(schema, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if target == "grok":
            write_grok_eval_sandbox(grader_workspace, source_skills)
        command = build_target_command(
            target,
            build_grader_prompt(case),
            grader_workspace,
            model,
            False,
            reasoning_effort=reasoning_effort,
            grader=True,
            schema=schema,
            schema_path=schema_path,
            output_path=output_path,
            disable_skills=True,
        )
        completed, _ = run_observed_target_phase(
            target,
            "grader",
            case["id"],
            iteration,
            command,
            grader_workspace,
            deadline - time.monotonic(),
            phase_records=phase_records,
        )
        try:
            grader_session_id, structured = parse_grader_output(
                target, completed, output_path=output_path
            )
        except TargetError as error:
            print(
                f"OBSERVE case={case['id']} iteration={iteration} "
                f"target={target} phase=grader status=protocol_error",
                file=sys.stderr,
                flush=True,
            )
            raise TargetError(f"grader protocol: {error}") from error
    if grader_session_id == candidate["session_id"]:
        raise TargetError("target reused the candidate session for grading")
    return structured, grader_session_id


def run_builtin_target_case(
    request,
    target,
    model,
    reasoning_effort,
    workspace,
    timeout,
    additional_skill_paths,
    denied_source_skill_paths,
    phase_records,
):
    case = request["case"]
    iteration = request["run"]["iteration"]
    session_id = None
    try:
        if (
            "should_trigger" not in case
            and case.get("category") in {"baseline", "isolation"}
            and target == "codex"
        ):
            raise TargetError(
                f"{target} built-in mode cannot suppress ambient user skills for "
                f"{case['category']} evidence"
            )
        if "should_trigger" in case and target == "codex":
            raise TargetError(
                f"{target} exposes no attributable automatic skill activation event"
            )
        stage_target_skills(
            request,
            target,
            workspace,
            additional_skill_paths,
            denied_source_skill_paths,
        )
        excluded_roots = {".agents", ".claude", ".git", ".grok"}
        before_state = workspace_state(workspace, excluded_roots)
        writable = case.get("side_effects") == "fixture"
        command = build_target_command(
            target,
            build_candidate_prompt(target, request),
            workspace,
            model,
            writable,
            reasoning_effort=reasoning_effort,
            disable_skills=not request["skill"]["enabled"],
        )
        stop_when = None
        if "should_trigger" in case and target in {"claude", "grok"}:
            def stop_when(stdout, stderr):
                try:
                    observed = parse_target_observation(target, stdout, stderr)
                except TargetError:
                    return False
                activated, _ = observe_target_activation(
                    target,
                    observed,
                    request["skill"]["name"],
                    workspace,
                )
                # Only a matching activation is attributable mid-run. Its
                # absence proves nothing until the turn ends: the model may
                # read or search first and invoke the skill on a later turn,
                # so non-activation is judged on the completed event stream.
                return activated is True

        completed, stopped_early = run_observed_target_phase(
            target,
            "candidate",
            case["id"],
            iteration,
            command,
            workspace,
            timeout,
            stop_when=stop_when,
            phase_records=phase_records,
        )
        try:
            if stopped_early:
                candidate = parse_target_observation(
                    target, completed.stdout, completed.stderr
                )
            else:
                candidate = parse_candidate_output(target, completed)
        except TargetError as error:
            print(
                f"OBSERVE case={case['id']} iteration={iteration} "
                f"target={target} phase=candidate status=protocol_error",
                file=sys.stderr,
                flush=True,
            )
            raise TargetError(f"candidate protocol: {error}") from error
        session_id = candidate["session_id"]
        if "should_trigger" in case:
            activated, evidence = observe_target_activation(
                target, candidate, request["skill"]["name"], workspace
            )
            if activated is None:
                return (
                    "unknown",
                    evidence,
                    [f"  UNKNOWN activation: {evidence}"],
                    [session_id],
                )
            response = {
                "protocol_version": SCHEMA_VERSION,
                "case_id": case["id"],
                "session_id": session_id,
                "fresh_session": True,
                "activated": activated,
                "evidence": evidence,
            }
            result = validate_adapter_response(case, response)
            return result[0], result[1], result[2], [session_id]

        after_state = workspace_state(workspace, excluded_roots)
        structured, grader_session_id = grade_functional_case(
            target,
            model,
            reasoning_effort,
            case,
            workspace,
            candidate,
            before_state,
            after_state,
            time.monotonic() + timeout,
            iteration,
            phase_records,
            grok_sandbox_sources(
                request, additional_skill_paths, denied_source_skill_paths
            ),
        )
        response = {
            "protocol_version": SCHEMA_VERSION,
            "case_id": case["id"],
            "session_id": session_id,
            "fresh_session": True,
            "assertions": structured.get("assertions"),
        }
        result = validate_adapter_response(case, response)
        return (
            result[0],
            result[1],
            result[2],
            [session_id, grader_session_id],
        )
    except (OSError, UnicodeError, ContractError, TargetError) as error:
        detail = str(error)
        return (
            "unknown",
            detail,
            [f"  UNKNOWN {target}: {detail}"],
            [session_id] if session_id is not None else [],
        )


def run_external_adapter_case(case, request, adapter, workspace, timeout):
    try:
        completed = subprocess.run(
            adapter,
            input=json.dumps(request),
            capture_output=True,
            text=True,
            cwd=workspace,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        detail = f"adapter timed out after {timeout:g} seconds"
        return "unknown", detail, [f"  UNKNOWN adapter: {detail}"], []
    except OSError as error:
        detail = f"adapter could not start: {error}"
        return "unknown", detail, [f"  UNKNOWN adapter: {detail}"], []
    if completed.returncode != 0:
        detail = completed.stderr.strip() or f"exit {completed.returncode}"
        detail = f"adapter failed: {detail}"
        return "unknown", detail, [f"  UNKNOWN adapter: {detail}"], []
    try:
        response = json.loads(completed.stdout)
        result = validate_adapter_response(case, response)
        return result[0], result[1], result[2], [result[3]]
    except (json.JSONDecodeError, ContractError) as error:
        detail = f"invalid adapter response: {error}"
        return "unknown", detail, [f"  UNKNOWN adapter: {detail}"], []


def run_case(
    skill_dir,
    skill_name,
    case,
    adapter,
    target,
    model,
    reasoning_effort,
    additional_skill_paths,
    denied_source_skill_paths,
    iteration,
    timeout,
    artifacts_root,
):
    with tempfile.TemporaryDirectory(prefix=f"skill-eval-{case['id']}-") as temp_dir:
        workspace = Path(temp_dir)
        phase_records = {} if target else None
        request = stage_request(
            skill_dir,
            skill_name,
            case,
            workspace,
            iteration,
            copy_skill=not target,
        )
        if target:
            result = run_builtin_target_case(
                request,
                target,
                model,
                reasoning_effort,
                workspace,
                timeout,
                additional_skill_paths,
                denied_source_skill_paths,
                phase_records,
            )
        else:
            result = run_external_adapter_case(
                case, request, adapter, workspace, timeout
            )
        if artifacts_root is not None:
            try:
                save_case_artifacts(
                    workspace,
                    artifacts_root,
                    case,
                    iteration,
                    result,
                    phase_records,
                )
            except (OSError, UnicodeError, ContractError, TargetError) as error:
                detail = (
                    f"artifact capture failed after {result[0]} result: {error}"
                )
                print(
                    f"OBSERVE case={case['id']} iteration={iteration} "
                    "phase=artifacts status=error",
                    file=sys.stderr,
                    flush=True,
                )
                result = (
                    "unknown",
                    detail,
                    [f"  UNKNOWN artifacts: {detail}"],
                    result[3],
                )
        return result, sanitized_phase_records(phase_records)


def select_cases(functional, trigger, selected_case_ids):
    cases = functional + trigger
    if selected_case_ids:
        if len(selected_case_ids) != len(set(selected_case_ids)):
            raise ContractError("--case values must be unique")
        known_case_ids = {case["id"] for case in cases}
        missing_case_ids = sorted(set(selected_case_ids) - known_case_ids)
        if missing_case_ids:
            raise ContractError(
                "--case not found: " + ", ".join(missing_case_ids)
            )
        selected_case_ids = set(selected_case_ids)
        cases = [case for case in cases if case["id"] in selected_case_ids]
    return cases


def execute_cases(
    skill_dir,
    skill_name,
    cases,
    adapter,
    target,
    model,
    reasoning_effort,
    additional_skill_paths,
    denied_source_skill_paths,
    repeat,
    timeout,
    artifacts_root,
    fail_fast,
):
    counts = {status: 0 for status in RESULT_STATUSES}
    case_reports = []
    session_ids = set()
    required_correct = repeat // 2 + 1
    for case in cases:
        trigger_outcomes = (
            {status: 0 for status in RESULT_STATUSES}
            if "should_trigger" in case
            else None
        )
        stop_after_case = False
        iteration_reports = []
        for iteration in range(1, repeat + 1):
            result, phases = run_case(
                skill_dir,
                skill_name,
                case,
                adapter,
                target,
                model,
                reasoning_effort,
                additional_skill_paths,
                denied_source_skill_paths,
                iteration,
                timeout,
                artifacts_root,
            )
            status, detail, evidence_lines, observed_session_ids = result
            duplicates = {
                session_id
                for session_id in observed_session_ids
                if observed_session_ids.count(session_id) > 1
                or session_id in session_ids
            }
            if duplicates:
                session_id = sorted(duplicates)[0]
                status = "unknown"
                detail = f"adapter reused target session id {session_id!r}"
                evidence_lines = [f"  UNKNOWN session: {detail}"]
            if artifacts_root is not None:
                destination = (
                    artifacts_root / case["id"] / f"iteration-{iteration}"
                )
                if destination.is_dir():
                    try:
                        write_case_result_metadata(
                            destination,
                            case,
                            iteration,
                            (status, detail, evidence_lines, observed_session_ids),
                        )
                    except (OSError, UnicodeError) as error:
                        status = "unknown"
                        detail = f"artifact metadata finalization failed: {error}"
                        evidence_lines = [f"  UNKNOWN artifacts: {detail}"]
            session_ids.update(observed_session_ids)
            iteration_reports.append(
                {
                    "iteration": iteration,
                    "status": status,
                    "reason_code": result_reason_code(case, status, phases),
                    "phases": phases,
                }
            )
            if trigger_outcomes is not None:
                trigger_outcomes[status] += 1
            else:
                counts[status] += 1
                if fail_fast and status != "pass":
                    stop_after_case = True
            suffix = "" if status == "pass" else f" reason={detail}"
            print(f"{status.upper()} {case['id']} iteration={iteration}{suffix}")
            for line in evidence_lines:
                print(line)
            if stop_after_case:
                break
        if trigger_outcomes is not None:
            if trigger_outcomes["pass"] >= required_correct:
                aggregate_status = "pass"
            elif trigger_outcomes["fail"] >= required_correct:
                aggregate_status = "fail"
            else:
                aggregate_status = "unknown"
            counts[aggregate_status] += 1
            if fail_fast and aggregate_status != "pass":
                stop_after_case = True
        else:
            iteration_statuses = {
                iteration["status"] for iteration in iteration_reports
            }
            if "fail" in iteration_statuses:
                aggregate_status = "fail"
            elif "unknown" in iteration_statuses:
                aggregate_status = "unknown"
            else:
                aggregate_status = "pass"
        case_reports.append(
            {
                "case_id": case["id"],
                "kind": (
                    "trigger" if "should_trigger" in case else "functional"
                ),
                "status": aggregate_status,
                "iterations": iteration_reports,
            }
        )
        if trigger_outcomes is not None and repeat > 1:
            triggered = (
                trigger_outcomes["pass"]
                if case["should_trigger"]
                else trigger_outcomes["fail"]
            )
            if trigger_outcomes["unknown"]:
                rate = (
                    f"{triggered / repeat:.3f}.."
                    f"{(triggered + trigger_outcomes['unknown']) / repeat:.3f}"
                )
            else:
                rate = f"{triggered / repeat:.3f}"
            print(
                f"TRIGGER_RATE {case['id']} triggered={triggered}/{repeat} "
                f"rate={rate} expected={str(case['should_trigger']).lower()} "
                f"threshold=0.5 status={aggregate_status}"
            )
        if stop_after_case:
            break
    print(
        f"SUMMARY pass={counts['pass']} fail={counts['fail']} "
        f"unknown={counts['unknown']}"
    )
    return counts, case_reports


def run_evaluations(
    skill_path,
    adapter,
    target,
    model,
    reasoning_effort,
    additional_skill_values,
    repeat,
    timeout,
    selected_case_ids,
    artifacts_dir,
    fail_fast=False,
    report_path=None,
    report_scope=None,
    expected_package_digest=None,
    expected_additional_digests=None,
):
    skill_name, source_functional, source_trigger = inspect_skill(skill_path)
    select_cases(source_functional, source_trigger, selected_case_ids)
    source_skill_dir = Path(skill_path).resolve()
    if adapter[:1] == ["--"]:
        adapter = adapter[1:]
    if target and adapter:
        raise ContractError("choose either --target or an adapter after --")
    if model and not target:
        raise ContractError("--model requires --target")
    if reasoning_effort and not target:
        raise ContractError("--reasoning-effort requires --target")
    if target:
        target_config = TARGET_CONFIGS[target]
        if model is None:
            model = target_config["model"]
        if reasoning_effort is None:
            reasoning_effort = target_config["reasoning_effort"]
        supported_efforts = target_config["canonical_reasoning_efforts"]
        if reasoning_effort not in supported_efforts:
            raise ContractError(
                f"--reasoning-effort {reasoning_effort!r} is not supported for "
                f"--target {target}"
            )
    if additional_skill_values and not target:
        raise ContractError("--additional-skill requires --target")
    if not target and not adapter:
        raise ContractError("run requires --target or an adapter command after --")
    source_additional_skill_paths = parse_additional_skill_paths(
        additional_skill_values, skill_name
    )
    if repeat < 1:
        raise ContractError("--repeat must be at least 1")
    if timeout <= 0:
        raise ContractError("--timeout must be greater than 0")
    report_destination = validate_report_destination(report_path, source_skill_dir)
    with tempfile.TemporaryDirectory(prefix="skill-eval-snapshot-") as temp_dir:
        snapshot_root = Path(temp_dir)
        snapshot_skill_dir = snapshot_root / skill_name
        skill_digest = copy_stable_package(source_skill_dir, snapshot_skill_dir)
        if (
            expected_package_digest is not None
            and skill_digest != expected_package_digest
        ):
            raise ContractError("package changed since the recorded run")
        snapshot_name, functional, trigger = inspect_skill(snapshot_skill_dir)
        if snapshot_name != skill_name:
            raise ContractError("skill package identity changed while snapshotting")
        cases = select_cases(functional, trigger, selected_case_ids)

        snapshot_additional_skill_paths = {}
        additional_report = []
        for name, source in sorted(source_additional_skill_paths.items()):
            destination = snapshot_root / "additional-skills" / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            additional_digest = copy_stable_package(source, destination)
            snapshot_additional_skill_paths[name] = destination
            additional_report.append(
                {
                    "name": name,
                    "source_path": str(source),
                    "package_sha256": additional_digest,
                }
            )
        expected_additional_digests = expected_additional_digests or {}
        observed_additional_digests = {
            item["name"]: item["package_sha256"] for item in additional_report
        }
        if (
            expected_additional_digests
            and observed_additional_digests != expected_additional_digests
        ):
            raise ContractError("additional skill package changed since the recorded run")
        snapshot_additional_skill_paths = add_package_fixture_skill_paths(
            snapshot_additional_skill_paths, snapshot_skill_dir, cases
        )
        artifacts_root = prepare_artifacts_root(artifacts_dir, source_skill_dir)
        counts, case_reports = execute_cases(
            snapshot_skill_dir,
            skill_name,
            cases,
            adapter,
            target,
            model,
            reasoning_effort,
            snapshot_additional_skill_paths,
            [source_skill_dir, *source_additional_skill_paths.values()],
            repeat,
            timeout,
            artifacts_root,
            fail_fast,
        )

    if report_scope is not None or report_destination is not None:
        target_report = {
            "name": target or "external-adapter",
            "model": model or "n/a",
            "reasoning_effort": reasoning_effort or "n/a",
        }
        report = {
            "schema_version": SCHEMA_VERSION,
            "kind": "skill-eval-run",
            "skill": {
                "name": skill_name,
                "source_path": str(source_skill_dir),
                "package_sha256": skill_digest,
            },
            "target": target_report,
            "run": {
                "scope": report_scope or "run",
                "selected_case_ids": (
                    list(selected_case_ids) if selected_case_ids else None
                ),
                "repeat": repeat,
                "timeout_seconds": timeout,
                "fail_fast": fail_fast,
                "additional_skills": additional_report,
            },
            "cases": case_reports,
            "summary": counts,
        }
        write_run_report(report, report_destination)
    return 0 if counts["fail"] == 0 and counts["unknown"] == 0 else 1


def add_run_arguments(parser, model_defaults, effort_defaults, canonical_efforts):
    parser.add_argument("skill_dir", help="skill package containing evals/")
    parser.add_argument(
        "--repeat", type=int, default=1, help="fresh runs per selected case"
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=900,
        help=(
            "timeout in seconds per built-in candidate or grader phase, or per "
            "external-adapter case (default: 900)"
        ),
    )
    parser.add_argument(
        "--target",
        choices=sorted(TARGETS),
        help="run with a bundled Claude, Codex, or Grok adapter",
    )
    parser.add_argument(
        "--model",
        help=(
            f"target model override; valid only with --target; defaults: "
            f"{model_defaults}"
        ),
    )
    parser.add_argument(
        "--reasoning-effort",
        choices=sorted(REASONING_EFFORTS),
        help=(
            "target reasoning effort override; canonical target CLI values: "
            f"{canonical_efforts}; defaults: {effort_defaults}"
        ),
    )
    parser.add_argument(
        "--additional-skill",
        action="append",
        default=[],
        metavar="NAME=PATH",
        help="stage a declared coexistence skill; repeat for additional skills",
    )
    parser.add_argument(
        "--artifacts-dir",
        metavar="NEW_DIR",
        help=(
            "preserve each sanitized case workspace and result metadata in a new "
            "directory"
        ),
    )
    parser.add_argument(
        "--report",
        metavar="NEW_FILE",
        help=(
            "write the sanitized run report to a new file; run-one and run-all "
            "create a temporary report automatically when omitted"
        ),
    )


def build_parser():
    model_defaults = ", ".join(
        f"{target}={TARGET_CONFIGS[target]['model']}" for target in sorted(TARGETS)
    )
    effort_defaults = ", ".join(
        f"{target}={TARGET_CONFIGS[target]['reasoning_effort']}"
        for target in sorted(TARGETS)
    )
    canonical_efforts = ", ".join(
        f"{target}={'/'.join(TARGET_CONFIGS[target]['canonical_reasoning_efforts'])}"
        for target in sorted(TARGETS)
    )
    parser = argparse.ArgumentParser(
        description="Validate and run portable skill evaluation cases."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="validate a skill and its evals")
    check.add_argument("skill_dir", help="skill package containing evals/")
    list_cases = subparsers.add_parser(
        "list", help="list validated functional and trigger case ids"
    )
    list_cases.add_argument("skill_dir", help="skill package containing evals/")
    inspect = subparsers.add_parser(
        "inspect", help="summarize a sanitized eval run report"
    )
    inspect.add_argument("report", help="report emitted by run-one or run-all")
    rerun = subparsers.add_parser(
        "rerun", help="rerun a recorded built-in target configuration"
    )
    rerun.add_argument("report", help="report emitted by run-one or run-all")
    run = subparsers.add_parser(
        "run",
        help="run evals through a built-in target or external adapter",
        description=(
            "Validate and run skill evals. Select --target claude, codex, or "
            "grok, or put an external adapter command and its arguments after --."
        ),
    )
    add_run_arguments(run, model_defaults, effort_defaults, canonical_efforts)
    run.add_argument(
        "--case",
        action="append",
        dest="case_ids",
        metavar="CASE_ID",
        help="run one affected case; repeat for additional cases",
    )
    run_one = subparsers.add_parser(
        "run-one",
        help="run exactly one case for focused debugging",
        description=(
            "Validate and run exactly one skill eval. Select --target claude, "
            "codex, or grok, or put an external adapter after --."
        ),
    )
    add_run_arguments(run_one, model_defaults, effort_defaults, canonical_efforts)
    run_one.add_argument("case_id", metavar="CASE_ID", help="case id to run")
    run_all = subparsers.add_parser(
        "run-all",
        help="run the full suite, stopping at the first non-green case",
        description=(
            "Validate and run every skill eval. The run stops after the first "
            "non-green case unless --keep-going is supplied."
        ),
    )
    add_run_arguments(run_all, model_defaults, effort_defaults, canonical_efforts)
    run_all.add_argument(
        "--keep-going",
        action="store_true",
        help="run remaining cases after a fail or unknown result",
    )
    return parser


def parse_arguments(argv):
    values = list(sys.argv[1:] if argv is None else argv)
    adapter = []
    run_commands = {"run", "run-one", "run-all"}
    if values[:1] and values[0] in run_commands and "--" in values:
        delimiter = values.index("--")
        adapter = values[delimiter + 1 :]
        values = values[:delimiter]
    arguments = build_parser().parse_args(values)
    if arguments.command in run_commands:
        arguments.adapter = adapter
    return arguments


def main(argv=None):
    arguments = parse_arguments(argv)
    try:
        if arguments.command in {"inspect", "rerun"}:
            report = load_run_report(arguments.report)
            if arguments.command == "inspect":
                inspect_run_report(report)
                return 0
            return rerun_from_report(report)
        if arguments.command in {"run", "run-one", "run-all"}:
            if arguments.command == "run-one":
                selected_case_ids = [arguments.case_id]
                fail_fast = True
                report_scope = "run-one"
            elif arguments.command == "run-all":
                selected_case_ids = None
                fail_fast = not arguments.keep_going
                report_scope = "run-all"
            else:
                selected_case_ids = arguments.case_ids
                fail_fast = False
                report_scope = "run" if arguments.report else None
            return run_evaluations(
                arguments.skill_dir,
                arguments.adapter,
                arguments.target,
                arguments.model,
                arguments.reasoning_effort,
                arguments.additional_skill,
                arguments.repeat,
                arguments.timeout,
                selected_case_ids,
                arguments.artifacts_dir,
                fail_fast,
                arguments.report,
                report_scope,
            )
        skill_name, functional, trigger = inspect_skill(arguments.skill_dir)
    except ContractError as error:
        print(f"ERROR {error}", file=sys.stderr)
        return 2
    if arguments.command == "list":
        for case in functional:
            print(f"functional\t{case['id']}")
        for case in trigger:
            expected = str(case["should_trigger"]).lower()
            print(f"trigger\t{case['id']}\tshould_trigger={expected}")
    else:
        print(
            f"OK {skill_name}: eval_contract=valid "
            f"functional={len(functional)} trigger={len(trigger)}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
