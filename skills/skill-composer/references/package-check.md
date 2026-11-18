# Fixing Package-Check Findings

Read this file in full when the package check reports a finding, before fixing it. Every finding fails the check: you choose the fix, not whether to comply. A check with an obvious fix (a missing target or anchor, frontmatter, the entry point) has no section here.

## whole-file-pointers

Anchors into `SKILL.md` and within the same file are allowed. Otherwise choose:

- Link the whole file, tell the agent to read it in full, and name the section in prose, when the section needs the rest of the file to make sense and the file is cheap to read.
- Split the section into its own reference when it stands alone, or when the file is large next to what this branch needs, such as a 1 KB section inside a 16 KB file.
- Move it into `SKILL.md` when several branches share it, such as a prerequisite or setup step.
- When the target is a human-facing file such as `README.md`, move what the agent needs into a reference; the README can then link that reference instead of repeating it.

## entry-point-size

Work in this order: cut what a script checks, what the model does by default, and anything said twice; then move one branch's workflow or lookup material into a reference with a read condition. Standing rules, gates, routing between branches, and completion criteria stay in `SKILL.md`. The largest sections in the output show where to start.

## reachable-references

Choose: add a pointer with a read condition from `SKILL.md` or a file it links (a backticked path counts); move a file that only a script reads to `assets/`; or delete a file nothing needs.

## cross-skill-links

Tell the agent to invoke the skill by name through the host's skill mechanism. For a skill that is not installed, link its repository or directory page, not its `SKILL.md`.

## local-links

For a link that leaves the skill, use a full repository URL, which works on GitHub and when the skill is installed alone, or name the sibling skill in prose.

## nested-entry-points

Rename a fixture or example to another name, such as `SKILL.md.fixture`, and have whatever uses it restore the name in a temporary copy; move a real second skill out of the package.

## spec-pointer

Link `SPEC.md` from `SKILL.md` with the condition that loads it: before modifying or reviewing this skill.
