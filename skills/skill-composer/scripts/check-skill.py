#!/usr/bin/env python3
"""Check one skill package against Skill Composer's mechanical package rules.

Checks: entry-point (SKILL.md exists), entry-point-size (at most 15,000 UTF-8
bytes), frontmatter (name and description are YAML strings per the Agent Skills
specification, name equal to the directory), local-links (every local Markdown
link, inline or a reference definition, and anchor resolves inside the skill), whole-file-pointers (no section anchor into a Markdown file other than SKILL.md
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
"FAIL <check>: <detail>" line per finding and any "INFO <check>: <fact>"
lines. Then one "FIX:" line names the guide, whose section named after each
check states its requirement, why it exists, and how to choose the fix; the
output prints no reason of its own. A "RESULT <skill>: <n> findings" line ends
the run. Blocks are separated by one blank line. A passing run prints only
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
# A link reference definition, "[label]: destination"; a footnote label starts with ^.
LINK_DEFINITION_PATTERN = re.compile(r"^ {0,3}\[(?!\^)[^\]]+\]:[ \t]*(<[^>]*>|\S+)", re.MULTILINE)
SCHEME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
FENCE_PATTERN = re.compile(r"^\s*(`{3,}|~{3,})")
GUIDE = Path(__file__).resolve().parent.parent / "references" / "package-check.md"
HEADING_PATTERN = re.compile(r"^#{1,6}\s+\S")
INLINE_CODE_PATTERN = re.compile(r"(`+).*?\1")
CODE_SPAN_PATTERN = re.compile(r"(`+)\s*([^`\s]+?)\s*\1")
QUOTED_PATTERNS = {"'": re.compile(r"'((?:[^']|'')*)'"), '"': re.compile(r'"((?:[^"\\]|\\.)*)"')}
COMMENT_PATTERN = re.compile(r"(?:\s+#.*)?\s*")
# YAML 1.2 core-schema plain scalars that decode to null, a boolean, or a number.
NON_STRING_PATTERN = re.compile(
    r"null|Null|NULL|~|true|True|TRUE|false|False|FALSE"
    r"|[-+]?[0-9]+|0o[0-7]+|0x[0-9a-fA-F]+"
    r"|[-+]?(?:\.[0-9]+|[0-9]+(?:\.[0-9]*)?)(?:[eE][-+]?[0-9]+)?"
    r"|[-+]?\.(?:inf|Inf|INF)|\.(?:nan|NaN|NAN)"
)


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
    return fields


def scalar(parts):
    """Decode a field's source lines as a YAML string; raise ValueError naming the problem."""
    first, rest = parts[0], [part for part in parts[1:] if part]
    if first[:1] in (">", "|"):
        return " ".join(rest)
    if first[:1] in ("'", '"'):
        source = " ".join([first] + rest)
        quoted = QUOTED_PATTERNS[first[0]].match(source)
        if not quoted or not COMMENT_PATTERN.fullmatch(source[quoted.end():]):
            raise ValueError("is not valid YAML")
        return quoted.group(1).replace("''", "'") if first[0] == "'" else quoted.group(1)
    lines = (re.split(r"(?:^|\s)#", line, maxsplit=1)[0].strip() for line in [first] + rest)
    value = " ".join(line for line in lines if line)
    if ": " in value or value.endswith(":"):
        raise ValueError("is not valid YAML; quote the value")
    if NON_STRING_PATTERN.fullmatch(value):
        raise ValueError("must be a string; quote the value")
    return value


def check_frontmatter(root, text):
    fields = parse_frontmatter(text)
    if fields is None:
        return ["SKILL.md must start with --- and close its frontmatter with ---"]

    findings = []
    values = {}
    for field in ("name", "description"):
        try:
            values[field] = scalar(fields[field]) if field in fields else ""
        except ValueError as problem:
            findings.append(f"{field} {problem}")
            values[field] = None

    name = values["name"]
    if name == "":
        findings.append("name is missing")
    elif name is not None:
        if not NAME_PATTERN.fullmatch(name) or len(name) > MAX_NAME_LENGTH:
            findings.append(
                f"name '{name}' must be lowercase letters, digits, and single "
                f"hyphens, at most {MAX_NAME_LENGTH} characters"
            )
        if name != root.name:
            findings.append(f"name '{name}' does not match directory '{root.name}'")

    description = values["description"]
    if description == "":
        findings.append("description is missing")
    elif description is not None and len(description) > MAX_DESCRIPTION_LENGTH:
        findings.append(
            f"description is {len(description)} characters; "
            f"the limit is {MAX_DESCRIPTION_LENGTH}"
        )
    return findings


def heading_anchors(text):
    """GitHub-style heading anchors."""
    anchors = set()
    seen = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", strip_fences(text), re.MULTILINE):
        heading = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", heading)
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        count = seen.get(slug, 0)
        seen[slug] = count + 1
        anchors.add(slug if count == 0 else f"{slug}-{count}")
    return anchors


def fenced(lines):
    """Yield (line, inside) pairs, inside being True for fence lines and their contents.

    A fence closes only on a line of the same character, at least as long as
    the opening fence, with nothing after it."""
    fence = None
    for line in lines:
        match = FENCE_PATTERN.match(line)
        if fence is None:
            if match:
                fence = match.group(1)
            yield line, fence is not None
            continue
        if match and match.group(1)[0] == fence[0] and len(match.group(1)) >= len(fence) \
                and not line.strip().lstrip(fence[0]):
            fence = None
        yield line, True


def strip_fences(text):
    return "\n".join(line for line, inside in fenced(text.splitlines()) if not inside)


def strip_code(text):
    return INLINE_CODE_PATTERN.sub("", strip_fences(text))


def largest_sections(text, count=3):
    """The largest heading-delimited sections of a Markdown file, by UTF-8 bytes."""
    sections = [["(frontmatter and text before the first heading)", 0]]
    for line, inside in fenced(text.splitlines(keepends=True)):
        if not inside and HEADING_PATTERN.match(line):
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
        prose = strip_code(text)
        for raw in LINK_PATTERN.findall(prose) + LINK_DEFINITION_PATTERN.findall(prose):
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
        print()
    if findings:
        print(
            f"FIX: read {GUIDE} in full before changing anything; the section named after each "
            "check states its requirement, why it exists, and how to choose the fix."
        )
        print()
        noun = "finding" if len(findings) == 1 else "findings"
        print(f"RESULT {root.name}: {len(findings)} {noun}")
        return 1
    print(f"OK {root.name}: {CHECK_COUNT} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
