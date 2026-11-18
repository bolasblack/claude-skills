#!/usr/bin/env python3
"""Check one skill package against Skill Composer's mechanical package rules.

Checks: entry-point (SKILL.md exists), entry-point-size (at most 15,000 UTF-8
bytes), frontmatter (name and description per the Agent Skills specification,
name equal to the directory), local-links (every local Markdown link and anchor
resolves inside the skill), whole-file-pointers (no section anchor into a Markdown file other than SKILL.md
or the linking file), cross-skill-links (no link or URL to another skill's
SKILL.md in a file the agent reads), nested-entry-points (no SKILL.md below the
skill root),
reachable-references (every Markdown file under references/ is linked from
SKILL.md, directly or through a linked file), and spec-pointer (a root SPEC.md
is linked from SKILL.md).

A file the agent reads is SKILL.md or a file it links, directly or through a
linked file. For reachability, an inline code span that names an existing file
by its path from the linking file or the skill root also links it, and a
Markdown link to a directory links every file below it.

Prints one block per check that fired, in order of its first finding: a
"FAIL <check>: <detail>" line per finding, any "INFO <check>: <fact>" lines,
and one "WHY <check>: <reason>" line. Then one "FIX:" line names the guide
that says how to choose each fix, and a "RESULT <skill>: <n> findings" line
ends the run. Blocks are separated by one blank line. A passing run prints only
"OK <skill>: 9 checks passed".
Exit status: 0 when every check passes, 1 on findings, 2 on a usage error.
"""

import argparse
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


MAX_ENTRY_POINT_BYTES = 15000
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
CHECK_COUNT = 9
NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
SKIPPED_PARTS = {".git", "node_modules", "__pycache__"}
LINK_PATTERN = re.compile(r"!?\[[^\]]*\]\(\s*(<[^>]*>|[^)\s]+)(?:\s+\"[^\"]*\")?\s*\)")
SCHEME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
FENCE_PATTERN = re.compile(r"^\s*(`{3,}|~{3,})")
REASONS = {
    "entry-point": "hosts discover a skill by the SKILL.md at its root.",
    "entry-point-size": (
        "after compaction a host may keep only the start of a skill (Claude Code "
        "keeps the first 5,000 tokens), so text past the cap can be lost without warning."
    ),
    "frontmatter": (
        "hosts route by name and description, and a host may skip a skill whose "
        "fields are invalid or whose name differs from its directory."
    ),
    "local-links": (
        "a broken link, or one that leaves the skill, points at nothing once the "
        "skill is installed on its own."
    ),
    "whole-file-pointers": (
        "a file tool cannot jump to an anchor, so the agent searches, reads one "
        "fragment, and misses the prerequisites and gates around it."
    ),
    "cross-skill-links": (
        "an agent reading another skill's file tends to take only part of it, and a "
        "file read is not re-attached after compaction; invoking the skill loads it whole."
    ),
    "nested-entry-points": (
        "discovery can match any file named SKILL.md, so a nested one can be "
        "published as a separate skill."
    ),
    "reachable-references": "a reference that no pointer reaches is never read.",
    "spec-pointer": "an unlinked SPEC.md is never read by the agent maintaining the skill.",
}
GUIDE = Path(__file__).resolve().parent.parent / "references" / "package-check.md"
HEADING_PATTERN = re.compile(r"^#{1,6}\s+\S")
INLINE_CODE_PATTERN = re.compile(r"(`+).*?\1")
CODE_SPAN_PATTERN = re.compile(r"(`+)\s*([^`\s]+?)\s*\1")


def package_files(root, pattern):
    for path in sorted(root.rglob(pattern)):
        if not SKIPPED_PARTS.intersection(path.relative_to(root).parts):
            yield path


def parse_frontmatter(text):
    """Return top-level frontmatter fields, or None when no block opens the file."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration:
        return None

    fields = {}
    key = None
    for line in lines[1:end]:
        match = re.match(r"^([A-Za-z0-9_-]+):(.*)$", line)
        if match:
            key = match.group(1)
            fields[key] = [match.group(2).strip()]
        elif key is not None:
            fields[key].append(line.strip())
    return {name: scalar(parts) for name, parts in fields.items()}


def scalar(parts):
    first, rest = parts[0], [part for part in parts[1:] if part]
    if first[:1] in (">", "|"):
        return " ".join(rest)
    value = " ".join([first] + rest).strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def check_frontmatter(root, text):
    fields = parse_frontmatter(text)
    if fields is None:
        return ["SKILL.md must start with --- and close its frontmatter with ---"]

    findings = []
    name = fields.get("name", "")
    if not name:
        findings.append("name is missing")
    else:
        if not NAME_PATTERN.fullmatch(name) or len(name) > MAX_NAME_LENGTH:
            findings.append(
                f"name '{name}' must be lowercase letters, digits, and single "
                f"hyphens, at most {MAX_NAME_LENGTH} characters"
            )
        if name != root.name:
            findings.append(f"name '{name}' does not match directory '{root.name}'")

    description = fields.get("description", "")
    if not description:
        findings.append("description is missing")
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        findings.append(
            f"description is {len(description)} characters; "
            f"the limit is {MAX_DESCRIPTION_LENGTH}"
        )
    return findings


def heading_anchors(text):
    """GitHub-style heading anchors."""
    anchors = set()
    seen = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", strip_code(text), re.MULTILINE):
        heading = re.sub(r"`([^`]*)`", r"\1", heading)
        heading = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", heading)
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    return anchors


def strip_fences(text):
    kept = []
    fence = None
    for line in text.splitlines():
        match = FENCE_PATTERN.match(line)
        if fence is None and match:
            fence = match.group(1)[0] * 3
            continue
        if fence is not None:
            if line.strip().startswith(fence):
                fence = None
            continue
        kept.append(line)
    return "\n".join(kept)


def strip_code(text):
    return INLINE_CODE_PATTERN.sub("", strip_fences(text))


def largest_sections(text, count=3):
    """The largest heading-delimited sections of a Markdown file, by UTF-8 bytes."""
    sections = [["(frontmatter and text before the first heading)", 0]]
    fence = None
    for line in text.splitlines(keepends=True):
        match = FENCE_PATTERN.match(line)
        if fence is None and match:
            fence = match.group(1)[0] * 3
        elif fence is not None and line.strip().startswith(fence):
            fence = None
        elif fence is None and HEADING_PATTERN.match(line):
            sections.append([line.strip(), 0])
        sections[-1][1] += len(line.encode("utf-8"))
    return sorted(sections, key=lambda section: -section[1])[:count]


def code_span_files(root, document, text):
    """Existing files named by an inline code span outside fenced blocks."""
    for _, span in CODE_SPAN_PATTERN.findall(strip_fences(text)):
        path = span.partition("#")[0]
        for base in (document.parent, root):
            candidate = (base / path).resolve()
            if candidate.is_file():
                yield candidate
                break


def check_links(root, entry_point):
    """Return link findings, each document's resolved link targets, and
    (document, finding, finding if the agent never reads that document)."""
    findings = []
    links = {}
    agent_read = []
    package = root.resolve()
    entry = entry_point.resolve()
    for document in package_files(root, "*.md"):
        source = document.relative_to(root).as_posix()
        text = document.read_text(encoding="utf-8")
        targets = links.setdefault(document.resolve(), set())
        for raw in LINK_PATTERN.findall(strip_code(text)):
            target = raw[1:-1] if raw.startswith("<") else raw
            if SCHEME_PATTERN.match(target):
                url = urlsplit(target)
                if url.scheme in ("http", "https") and url.path.endswith("/SKILL.md"):
                    agent_read.append((
                        document.resolve(),
                        ("cross-skill-links", f"{source} -> {target}: links another skill's SKILL.md"),
                        None,
                    ))
                continue
            path, has_fragment, fragment = target.partition("#")
            resolved = document.resolve() if not path else (
                document.parent / unquote(path)
            ).resolve()

            outside = ("local-links", f"{source} -> {target}: outside the skill")
            inside = resolved == package or package in resolved.parents
            if resolved.name == "SKILL.md" and resolved != entry:
                agent_read.append((
                    document.resolve(),
                    ("cross-skill-links", f"{source} -> {target}: links another skill's SKILL.md"),
                    None if inside else outside,
                ))
                continue
            if not inside:
                findings.append(outside)
                continue
            if not resolved.exists():
                findings.append(("local-links", f"{source} -> {target}: not found"))
                continue
            targets.add(resolved)
            if resolved.is_dir():
                targets.update(child.resolve() for child in package_files(resolved, "*"))
            if not has_fragment or resolved.suffix.lower() != ".md":
                continue
            if path and resolved not in (entry, document.resolve()):
                findings.append((
                    "whole-file-pointers",
                    f"{source} -> {target}: points at a section ({unquote(path)} is "
                    f"{len(resolved.read_bytes()):,} bytes)",
                ))
                continue
            anchors = heading_anchors(resolved.read_text(encoding="utf-8"))
            if unquote(fragment).lower() not in anchors:
                findings.append(("local-links", f"{source} -> {target}: missing anchor"))
        targets.update(code_span_files(root, document, text))
    return findings, links, agent_read


def reachable(entry, links):
    seen = {entry}
    pending = [entry]
    while pending:
        for target in links.get(pending.pop(), ()):
            if target not in seen:
                seen.add(target)
                pending.append(target)
    return seen


def check(root):
    """Return (check, detail) findings and {check: [fact, ...]} extra facts."""
    entry_point = root / "SKILL.md"
    if not entry_point.is_file():
        return [("entry-point", "SKILL.md not found")], {}

    findings = []
    info = {}
    size = len(entry_point.read_bytes())
    text = entry_point.read_text(encoding="utf-8")
    if size > MAX_ENTRY_POINT_BYTES:
        findings.append((
            "entry-point-size",
            f"SKILL.md is {size:,} bytes; the cap is {MAX_ENTRY_POINT_BYTES:,}",
        ))
        info["entry-point-size"] = [
            f'section "{heading}" is {length:,} bytes'
            for heading, length in largest_sections(text)
        ]
    findings.extend(("frontmatter", detail) for detail in check_frontmatter(root, text))
    link_findings, links, agent_read = check_links(root, entry_point)
    findings.extend(link_findings)
    entry = entry_point.resolve()
    linked = reachable(entry, links)
    for document, finding, unread_finding in agent_read:
        if document in linked:
            findings.append(finding)
        elif unread_finding:
            findings.append(unread_finding)
    for nested in package_files(root, "SKILL.md"):
        if nested != entry_point:
            findings.append((
                "nested-entry-points",
                f"{nested.relative_to(root).as_posix()} is below the skill root",
            ))
    references = root / "references"
    if references.is_dir():
        for reference in package_files(references, "*.md"):
            if reference.resolve() not in linked:
                findings.append((
                    "reachable-references",
                    f"{reference.relative_to(root).as_posix()} is not linked from "
                    "SKILL.md, directly or through a linked file",
                ))
    spec = root / "SPEC.md"
    if spec.is_file() and spec.resolve() not in links.get(entry, ()):
        findings.append((
            "spec-pointer",
            "SPEC.md exists but SKILL.md does not link it",
        ))
    return findings, info


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("skill_dir", type=Path, help="the skill directory to check")
    args = parser.parse_args(argv)

    root = args.skill_dir.resolve()
    if not root.is_dir():
        print(f"check-skill.py: {args.skill_dir} is not a directory", file=sys.stderr)
        return 2

    findings, info = check(root)
    for check_name in dict.fromkeys(check_name for check_name, _ in findings):
        for kind, detail in findings:
            if kind == check_name:
                print(f"FAIL {check_name}: {detail}")
        for fact in info.get(check_name, ()):
            print(f"INFO {check_name}: {fact}")
        print(f"WHY {check_name}: {REASONS[check_name]}")
        print()
    if findings:
        print(
            f"FIX: read {GUIDE} in full before changing anything; "
            "it says how to choose the fix for each check."
        )
        print()
        noun = "finding" if len(findings) == 1 else "findings"
        print(f"RESULT {root.name}: {len(findings)} {noun}")
        return 1
    print(f"OK {root.name}: {CHECK_COUNT} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
