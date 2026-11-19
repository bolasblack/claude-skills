---
name: sunset-extension
description: "Sunset a public skill, command, or agent in this repo: take it out of install, mark it deprecated with a reason and a replacement, and later remove it for good. Use when asked to sunset, deprecate, or retire a public extension here, or to finally delete a sunset one."
metadata:
  # Repo-only skill: hides it from `npx skills add` listings (vercel-labs/skills skips internal skills).
  internal: "true"
---

# Sunset Extension

**Sunset** is the phased retirement of a public extension in this repo. The extension moves to `_sunset/<type>/<name>/`, which `scripts/install.sh` never scans, so it is no longer installable by name, `ALL`, or `__ALL`. `scripts/uninstall.sh <type> ALL` still scans `_sunset/<type>/`, so users can clean up old installs. It stays there, marked deprecated, until a later **final removal**. Sunset sets no removal date: notices say only that it "will be removed in the future".

## Inputs

For each extension, collect `<type>` (`skills`, `commands`, or `agents`), `<name>`, a one-line **reason**, and a **replacement** (an extension, a built-in host feature, or "none"). Reason and replacement come from the user; ask for any that is missing.

**Done when:** every extension has all four.

## Preconditions

- The extension lives at the public path `<type>/<name>/`. A private extension (`private/<type>/<name>/`) has no sunset phase: it is managed or deleted in the private repo, so stop and say so.
- Pi extensions are out of scope: `uninstall.sh pi-extensions <name>` needs the source file in `pi-extensions/`, so moving one would strand its installs. Stop and tell the user.

**Done when:** every extension is a public skill, command, or agent.

## Sunset Steps

Run from the repo root, in order.

### 1. Uninstall local installs

```bash
./scripts/uninstall.sh <type> <name>...
```

Run this before the move: a symlink-mode install points into `<type>/<name>/` and dangles once the source moves. Then check this repo's own tracked project installs with `git ls-files .claude`: `git rm` any entry named `<name>` or `<name>.md`.

**Done when:** the output ends with a `Done:` line, every `Skipped (not managed by us)` entry is reported to the user, and no tracked link into the extension remains.

### 2. Move it to `_sunset/`

```bash
mkdir -p _sunset/<type>
git mv <type>/<name> _sunset/<type>/<name>
t=$(mktemp -d); ./scripts/install.sh --project "$t" --tools claude <type> <name>; rm -rf "$t"
```

**Done when:** `git status` shows the renames and the install fails with `Extension directory not found`.

### 3. Mark it deprecated

In the main file (`SKILL.md`, `COMMAND.md`, or `AGENT.md`):

- Prefix the frontmatter `description` with `[SUNSET — use <replacement> instead] ` (or `[SUNSET] ` when there is none), so an agent that still loads it sees the status first. Name the replacement in a few words; the notice carries the detail. A YAML value starting with `[` is a flow sequence, so the description must be a quoted string.
- Insert this notice as the first body line after the frontmatter:

  ```markdown
  > **Sunset:** this <skill|command|agent> is no longer installable from this repository and will be removed in the future. <Reason>. Use <replacement> instead.
  ```

If the extension has its own `README.md`, put the same notice under its title.

**Done when:** the description prefix and the notice are in the main file (and README, if any), and the description is quoted.

### 4. Move the README row

In the repo `README.md`, delete the extension's row from its type table. Add a row to the `## Sunset` table, creating the section before `## Contributing` if it is missing:

```markdown
## Sunset

Sunset extensions are no longer installable and will be removed in the future. To remove an old install, run `./scripts/uninstall.sh <type> <name>`.

| Extension | Why | Use instead |
|-----------|-----|-------------|
| [<name>](./_sunset/<type>/<name>/) | <reason> | <replacement> |
```

**Done when:** the name appears in the README only in the Sunset table, linked to its `_sunset/` path.

### 5. Clean up references

```bash
git grep -n -e '<name>' -- ':(exclude)_sunset' ':(exclude)private'
```

The README Sunset row from step 4 is an expected hit. Decide every other hit by what it does:

- **Routes work to the extension** (instructions, install recommendations such as `llms.install.md`): point it at the replacement, keeping the passage's intent.
- **`.agents/config.json` tag** `<type>/<name>`: run `grep -rl '<type>/<name>' .agents/decisions`. With no hits, remove the tag. An AGD still tagged keeps the tag, since decision history outlives the extension. Leave `.agents/scripts/` alone (auto-managed).
- **Self-contained material** that carries its own copy of the extension (eval fixtures, examples) or records history: keep it.

**Done when:** every hit is changed or has a stated reason to stay, and the list goes into the report.

### 6. Verify

```bash
bash scripts/install.test.sh
t=$(mktemp -d); ./scripts/install.sh --project "$t" --tools claude <type> ALL | grep '<name>'; rm -rf "$t"
```

**Done when:** the test file prints `install tests passed` and the `grep` prints nothing.

### Report

Tell the user the uninstall output, the files changed, and each reference decision from step 5.

## Final Removal

When the user asks to delete a sunset extension for good:

1. `git rm -r _sunset/<type>/<name>`, and delete its row from the README Sunset table. When the table becomes empty, delete the whole section.
2. Re-run the step 5 grep and tag rule. A hit that links to `_sunset/<type>/<name>/` now points at the replacement or is deleted.

Old installs stay removable by name: `./scripts/uninstall.sh <type> <name>` needs no source directory for skills, commands, or agents; `ALL` no longer finds the extension.

**Done when:** `_sunset/<type>/<name>` is gone, the README no longer names it, and the grep finds no reference that routes work to it.
