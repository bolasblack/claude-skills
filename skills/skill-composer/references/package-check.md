# Fixing Package-Check Findings

Read this file in full when the package check reports a finding, before fixing it. Each section is named after one check: it states its requirement and why it exists (or links the file that explains why), then how to choose the fix when the fix is a choice. Every finding fails the check: you choose the fix, not whether to comply.

## entry-point

The skill root holds a file named exactly `SKILL.md`. **Why:** hosts discover a skill by the `SKILL.md` at its root.

## entry-point-size

`SKILL.md`, frontmatter included, is at most 15,000 UTF-8 bytes ([why](bounded-entry-point.md)).

Work in this order: cut what a script checks, what the model does by default, and anything said twice; then move one branch's workflow or lookup material into a reference with a read condition. Standing rules, gates, routing between branches, and completion criteria stay in `SKILL.md`. The largest sections in the output show where to start.

## frontmatter

`SKILL.md` opens with a frontmatter block whose `name` and `description` are YAML strings. `name` is lowercase letters, digits, and single hyphens, at most 64 characters, and equals the skill's directory name; `description` is at most 1,024 characters. **Why:** hosts route by `name` and `description`, and a host may skip a skill whose fields are invalid or whose name differs from its directory.

## local-links

Every local Markdown link, inline or a reference definition, and every anchor resolves inside the skill. **Why:** a broken link, or one that leaves the skill, points at nothing once the skill is installed on its own.

For a link that leaves the skill, use a full repository URL, which works on GitHub and when the skill is installed alone, or name the sibling skill in prose.

## whole-file-pointers

A link into another Markdown file targets the whole file, not a section anchor; anchors into `SKILL.md` and within the same file are allowed. **Why:** a file tool cannot jump to an anchor, so the agent searches, reads one fragment, and misses the prerequisites and gates around it.

Choose:

- Link the whole file, tell the agent to read it in full, and name the section in prose, when the section needs the rest of the file to make sense and the file is cheap to read.
- Split the section into its own reference when it stands alone, or when the file is large next to what this branch needs, such as a 1 KB section inside a 16 KB file.
- Move it into `SKILL.md` when several branches share it, such as a prerequisite or setup step.
- When the target is a human-facing file such as `README.md`, move what the agent needs into a reference; the README can then link that reference instead of repeating it.

## cross-skill-links

A file the agent reads (`SKILL.md` or a file it links) does not link another skill's `SKILL.md`, by path or URL. **Why:** an agent reading another skill's file tends to take only part of it, and a file read is not re-attached after compaction; invoking the skill loads it whole.

Tell the agent to invoke the skill by name through the host's skill mechanism. For a skill that is not installed, link its repository or directory page, not its `SKILL.md`.

## nested-entry-points

No file named `SKILL.md` sits below the skill root. **Why:** discovery can match any file named `SKILL.md`, so a nested one can be published as a separate skill.

Rename a fixture or example to another name, such as `SKILL.md.fixture`, and have whatever uses it restore the name in a temporary copy; move a real second skill out of the package.

## reachable-references

Every Markdown file under `references/` is linked from `SKILL.md`, directly or through a linked file. **Why:** a reference that no pointer reaches is never read.

Choose: add a pointer with a read condition from `SKILL.md` or a file it links (a backticked path counts); move a file that only a script reads to `assets/`; or delete a file nothing needs.

## spec-pointer

A root `SPEC.md` is linked from `SKILL.md`. **Why:** an unlinked `SPEC.md` is never read by the agent maintaining the skill.

Link `SPEC.md` from `SKILL.md` with the condition that loads it: before modifying or reviewing this skill.
