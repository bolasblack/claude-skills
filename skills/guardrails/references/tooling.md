# Guardrail Tooling

Use this reference when running, documenting, or changing the guardrail CLI.

## Path Convention

`<SKILL_PATH>` means the loaded base directory of this skill.

Use `<SKILL_PATH>/scripts/guardrails.ts` in skill documentation and examples:

```bash
bun <SKILL_PATH>/scripts/guardrails.ts validate
```

Use a concrete installed path in repo-level executable files such as package scripts, Makefile targets, git hooks, or CI config. The concrete path depends on where the skill is installed, for example:

```bash
bun .claude/skills/guardrails/scripts/guardrails.ts validate
bun ~/.claude/skills/guardrails/scripts/guardrails.ts validate
```

A gate that must run in CI needs the skill committed inside the repository; see `<SKILL_PATH>/references/adoption.md`.

## Global Options

All commands accept `--root <dir>` or `--root=<dir>` to point at the repository root explicitly.

Otherwise the root is resolved in this order: `--root`, then the `GUARDRAILS_ROOT` environment variable, then the nearest ancestor of the current directory that contains `.agents/guardrails`, then `git rev-parse --show-toplevel`, then the current directory. Commands therefore work from any subdirectory of the repository.

## Commands

### validate

```bash
bun <SKILL_PATH>/scripts/guardrails.ts validate
```

`validate` is a structural gate. It checks rule file schema, reference paths, active/retired uniqueness, index coverage, and skip/index/lint-assist invariants.

Wire it into the repo's lint or CI gate so broken guardrail structure fails early rather than at review time; `<SKILL_PATH>/references/adoption.md` shows how. It does not replace manual guardrails review.

### render

```bash
bun <SKILL_PATH>/scripts/guardrails.ts render GRL-<id1> GRL-<id2>
bun <SKILL_PATH>/scripts/guardrails.ts render --detail GRL-<id1> GRL-<id2>
```

`render` accepts explicit GRL IDs only. It does not accept task names, router section names, glob patterns, or file paths.

`--detail` may appear in any argument position: before the IDs, after them, or between them.

Repeated IDs are de-duplicated while preserving first occurrence order. Unknown IDs are errors. Retired IDs are errors and report their `retire_reason`.

Default rendering outputs each selected rule number and `short` text.

Detailed rendering outputs each selected rule number, `short` text, Markdown body with headings shifted one level deeper, and `references` at the end of each rule section. Only headings shift: `#` lines inside fenced code blocks are left exactly as written, and a level-six heading stays at level six.

Rendered output intentionally omits `enforcement`, `skip_index_reason`, `lint_assist_reason`, and retirement metadata because those are authoring/review metadata, not ordinary reading content.

### review-metadata

```bash
bun <SKILL_PATH>/scripts/guardrails.ts review-metadata --base <ref>
```

`--base <ref>` and `--base=<ref>` are both accepted. When `--base` is omitted the base ref is resolved in this order: the `GUARDRAILS_BASE` environment variable, then `origin/HEAD` when the remote head is configured, then `HEAD` (with a note on stderr). A base ref that does not resolve fails with `Base ref not found: <ref>`. The command requires git, and requires the guardrails root to be the git repository root.

It detects changed active GRL files, retired GRL files, deleted active GRL files, and router changes relative to the base ref. Git rename detection is disabled, so a rule moved or renumbered in the same change set reports both the old and the new path; a deleted active GRL is reported as a removal unless the same GRL number appears as a retired file in that change set. When a changed GRL can be parsed in the working tree and at the base ref, it compares review-relevant fields, selects only the instruction sections relevant to changed categories, and lists every applicable file under each section. It does not print a separate upfront changed-file list.

The printed instruction prose is maintained in per-category files under `<SKILL_PATH>/references/review-metadata-instructions/`; the filename stem is the instruction key. The catalog fails closed when expected instruction files are missing, unknown, or malformed. The CLI owns change detection and file grouping. `review-metadata` does not decide whether metadata is sufficient. It is not part of lint. It is a review helper because its output requires human judgment.

### next-id

```bash
bun <SKILL_PATH>/scripts/guardrails.ts next-id
```

`next-id` scans active and retired GRLs and prints max ID + 1. It does not create files and does not reuse retired numbers.

## Runtime

The CLI runs on Bun (https://bun.sh); it uses Bun's YAML parser and has no npm dependencies. Running it under another runtime fails immediately with a message naming Bun rather than failing per rule file. `review-metadata` additionally shells out to `git`.

The review-metadata instruction catalog is resolved relative to the script file, at `<SKILL_PATH>/references/review-metadata-instructions/`. Keep `scripts/` and `references/` siblings inside the skill directory; moving the script alone breaks the command.

## Exit Codes and Output

Every command exits 0 on success and 1 on any error. `validate` aggregates all structural errors into one `Guardrail validation failed:` list rather than stopping at the first. No command writes or mutates any file.

## Troubleshooting

**`guardrails requires the Bun runtime. Install Bun from https://bun.sh, then run: bun <skill-path>/scripts/guardrails.ts <command>`**

- Cause: the script was started by a runtime other than Bun, such as `node`, `tsx`, or `deno`.
- Solution: install Bun and invoke the script with `bun`. The CLI uses Bun's built-in YAML parser and has no npm dependencies, so no other runtime works. This guard fires before any rule file is read, so the message is about the runtime, not about your guardrail sources.

**`missing required file: .agents/guardrails/index.md`** (inside the `Guardrail validation failed:` list)

- Cause: `validate` resolved a root that has no router file — either the framework was never set up, or the resolved root is not the repository you meant.
- Solution: if the repository has no guardrails yet, create the layout per `<SKILL_PATH>/references/adoption.md`. If the layout does exist, the root resolved wrong: pass `--root <dir>`, or set `GUARDRAILS_ROOT`, and confirm the router really is at `.agents/guardrails/index.md`.

**`index.md references unknown GRL-<n>`**

- Cause: the router lists an ID with no active rule file. Common triggers: a rule was deleted or renumbered without a router edit, a rule was retired without removing its ID from the router, or the ID is a typo. Every `GRL-<number>` token in the router counts as listed, including prose, comments, and examples.
- Solution: create `.agents/guardrails/rules/GRL-<n>.md`, or remove the token from the router. Grep the whole file for the token — the stray mention is often outside the table.

**`Base ref not found: <ref>. Pass --base <ref> or set GUARDRAILS_BASE.`**

- Cause: `review-metadata` could not resolve the base ref to a commit. Usually the fallback chain landed on `origin/HEAD` in a clone where the remote head is not configured, or an explicit ref was misspelled or not fetched.
- Solution: pass an existing ref with `--base <ref>`, or set `GUARDRAILS_BASE`. To repair the default instead, run `git remote set-head origin --auto` and fetch the branch.

**`review-metadata requires running inside a git repository.`**

- Cause: `git rev-parse --show-toplevel` failed at the resolved guardrails root, so there is no history to diff against.
- Solution: run the command inside a git worktree. Only `review-metadata` needs git; `validate`, `render`, and `next-id` do not.

**`review-metadata requires the guardrails root to match the git repository root (guardrails root: ..., git root: ...)`**

- Cause: the resolved guardrails root is a subdirectory of the git repository (or a different repository), so file paths from git would not line up with guardrail paths. Typical in monorepos where `.agents/guardrails/` sits inside a package.
- Solution: run `review-metadata` with the guardrails layout at the git root, or pass `--root <git-root>` so the two match. Move `.agents/guardrails/` to the repository root if the split is permanent.

**`Unknown GRL ID: GRL-<n>`**

- Cause: `render` was given an ID with no active rule file — a typo, an ID copied from a stale list, or a rule that has since been renumbered.
- Solution: take IDs from `.agents/guardrails/index.md` at read time rather than from a transcribed list. Run `validate` to confirm the router and the rule files agree.

**`Cannot render retired GRL-<n>: <retire_reason>`**

- Cause: the requested ID resolves to a file under `.agents/guardrails/retired-rules/`. Retired rules cannot be rendered as active guardrails.
- Solution: read the printed `retire_reason` — it should name the replacement rule or explain why the rule is gone — and render that rule instead. If the ID came from the router, the router is wrong: retired IDs must not appear there, and `validate` will flag it.
