---
name: git-hook
description: "Adopt or harden reusable Git-hook automation in a repository. Use when setting up or standardizing project Git hooks, migrating a hook-manager setup, reusing hook configuration or scripts, or bootstrapping hooks for fresh clones. The current automated tool branch is Lefthook."
---

# Git Hook

When modifying or reviewing this skill, read [SPEC.md](SPEC.md) first. It holds the
user-owned requirements that must survive tool branches and rewrites; ordinary Git-hook
adoption does not need it.

The automated workflow below currently supports Lefthook. For another hook manager,
identify its ownership in Step 1 and stop before materializing the bundled runner; a
generic Git-hook request does not authorize migration to Lefthook.

The Lefthook branch avoids adding a hook manager to a language package manifest or
changing global Git configuration. A tracked runner bootstraps one trusted version into
the clone's Git common directory; installed hooks call the same runner. Setup may
provision the binary, while ordinary hook execution is offline and fail-closed.

The runner requires Git 2.31 or newer and a POSIX shell. Its direct bootstrap recognizes
Linux, macOS, and Git for Windows on x86_64 or arm64.

`<SKILL_PATH>` means the loaded base directory of this skill. The bundled runner is
`<SKILL_PATH>/scripts/lefthook`; copy it into the target repository rather than linking
back to the installed skill.

## Ownership

- The repository's one YAML Lefthook config owns `min_version`, hook jobs, remotes,
  and script references.
- The copied runner owns trusted release assets, checksums, platform mapping, and the
  Git-private binary location.
- The agent owns the contextual destination of that runner and its integration with an
  existing project setup entry.
- Git owns clone-local hooks under its resolved hooks directory. CI or server-side
  checks remain the enforcement owner because a fresh clone has no installed hooks.

The portable tracked result is normally one runner, one existing-or-new Lefthook YAML
config, and a small addition to an existing onboarding surface. The binary and generated
hooks stay under Git's private directory.

## Workflow

### Step 1: Inspect the repository

Read repository guidance and check the worktree before choosing files. Locate:

- existing Lefthook configs, including YAML, TOML, JSON, and `.config/` variants;
- existing Git-hook managers, executable non-sample files in the resolved hooks
  directory, and every configured `core.hooksPath` scope;
- tracked script or executable directories and their naming conventions;
- `.gitattributes` rules that control shell-script checkout line endings;
- existing `setup`, `bootstrap`, devcontainer, or onboarding entry points;
- existing hook commands and repo-owned lint, format, test, or validation commands.

Preserve unrelated dirty files. Use one of Lefthook's supported YAML main-config names:
`lefthook.yml`, `lefthook.yaml`, `.lefthook.yml`, `.lefthook.yaml`,
`.config/lefthook.yml`, or `.config/lefthook.yaml`. If the repository already has
multiple main configs, or only a TOML/JSON config, stop and surface that ownership
decision instead of creating a competing YAML file.

Treat an existing hook manager, `core.hooksPath`, or hand-written hook as a migration
boundary. Report the current owner and obtain an explicit migration decision before
replacing it; keep the runner's normal `install` path force-free. That flag choice is
not automatic protection: Lefthook 2.1.10 may rename an existing target hook to `.old`
and install its own wrapper without chaining the old hook, so inspect hook files before
every first adoption.

**Done when:** repository rules, dirty state, the one config owner, current hook owner,
available project commands, runner-path conventions, and onboarding entry are each
known or explicitly absent.

### Step 2: Choose the runner destination

Choose from evidence in the repository, not a universal directory preference. Reuse an
established tracked location such as `scripts/`, `bin/`, `tools/`, or `.bin/` only when
that directory is repo-owned rather than generated. Exclude dependency bins, ignored
paths, build output, and directories whose existing purpose conflicts with a source
script.

The selected path must:

- stay inside the Git root and use a repository-relative reference;
- be suitable for a tracked source file;
- contain no whitespace, `..`, or shell metacharacters;
- be able to receive a path-specific `text eol=lf` attribute without conflicting with
  repository policy;
- avoid overwriting an unrelated file.

Use `scripts/lefthook` only as the fallback when the repository has no stronger
convention. State the selected path and the evidence for it before editing.

**Done when:** one collision-free, non-ignored, repo-relative destination is selected,
and its choice follows an observed convention or the documented fallback.

### Step 3: Materialize the runner and configuration

Copy `<SKILL_PATH>/scripts/lefthook` byte-for-byte to the selected destination and make
the copied file executable. Do not reimplement its download or dispatch logic in a
package script, task runner, or second launcher.

Run `git check-attr text eol -- ./<runner-path>`. If existing attributes do not report
both `text: set` and `eol: lf`, add the narrow root-relative rule below to the existing
root `.gitattributes`, or create that one file when absent:

```gitattributes
/<runner-path> text eol=lf
```

Do not normalize unrelated paths. Re-copy the LF resource when the current worktree file
contains CRLF, then run `sh -n ./<runner-path>`. The attribute protects later Windows
checkouts; the syntax check verifies the bytes being adopted now.

Read the manifest version from the copied runner:

```sh
sed -n 's/^trusted_release_version=//p' ./<runner-path>
```

Require exactly one `x.y.z` result. In the repository's one YAML config, preserve all
existing hooks and add or reconcile this bootstrap stanza:

```yaml
min_version: "<trusted-release-version>"
assert_lefthook_installed: true
no_auto_install: true
lefthook: sh ./<runner-path>
```

`min_version` is the only project version source. This adoption contract strengthens
it from Lefthook's normal minimum into the exact version provisioned by the runner.
Use the official field directly: arbitrary top-level `x-*` keys are custom-hook space,
and `templates` is command-replacement space rather than private metadata.

When an existing `min_version` differs from the runner's trusted manifest, preserve the
current repository state and surface the version migration. The safe outcomes are an
approved config migration or an updated, independently verified runner manifest; an
unverified dynamic checksum is not a version-update path.

Keep hook jobs grounded in commands the repository already owns. Reuse existing task
entry points and extract a script only when several hooks need the same real logic.
Place that script according to the repository's conventions; the bootstrap runner does
not own linting, formatting, commit-message, or test policy.

**Done when:** the tracked runner matches the bundled resource, its attributes resolve
to `text: set` and `eol: lf`, `sh -n` passes, the YAML config has one exact supported
version and the selected runner command, existing hook behavior is preserved, and each
configured job resolves to a real repo-owned command or script.

### Step 4: Wire fresh-clone onboarding

The canonical direct setup command is:

```sh
sh ./<runner-path> install
```

If the repository already has a setup or bootstrap entry, make that entry delegate to
the canonical command. Keep the direct command discoverable in the existing README,
CONTRIBUTING guide, or equivalent onboarding document so it works without the optional
task runner. Do not create Make, just, mise, npm, or another task system solely for Git
hooks, and do not use a package lifecycle script as the universal entry.

Keep required checks in CI independently of local hooks. Clone cannot safely execute a
tracked repository script automatically, and `assert_lefthook_installed` only applies
after a hook wrapper exists.

**Done when:** a new contributor has one documented direct command, any existing
bootstrap entry delegates to it without duplicating logic, and merge enforcement does
not depend on local hook installation.

### Step 5: Install and verify

Run the canonical setup command from the Git worktree. This is the only runner mode
allowed to provision a binary:

```sh
sh ./<runner-path> install
```

The runner performs these observable operations:

1. Resolves the repository and Git common directory, including linked worktrees.
2. Rejects multiple YAML configs, a non-exact/unsupported version, an unknown platform,
   or any configured `core.hooksPath` before provisioning.
3. Uses `mise install-into` only when a standard project-root mise config is tracked,
   mise is on `PATH`, and that command is supported. It changes mise's working directory
   to the isolated install directory so fresh-clone trust state is not mutated. A failed
   mise installation stops; it does not silently switch supply chains.
4. Otherwise downloads the fixed official release asset, verifies the bundled SHA-256,
   and installs it under the Git common directory.
5. Runs `lefthook validate`, `lefthook install`, and `lefthook check-install` in order.

The mise path writes neither project nor global mise configuration and never runs
`mise trust`; changing to the isolated install directory keeps the repository config
outside mise's active hierarchy. The direct path requires `curl`, `gzip`, and either
`sha256sum` or `shasum`.

After setup, run this read-only smoke check:

```sh
sh ./<runner-path> version
```

Inspect the target repository's status and diff. Exercise a real hook only when its
commands and possible file mutations are safe for the current task; otherwise report
that live hook execution remains untested.

**Done when:** setup and the version smoke check exit zero, `check-install` passed, no
global Git or mise config changed, tracked diffs contain only the approved adoption,
and every unrun hook/platform behavior is reported as unknown rather than passed.

## Failure Contract

- Runtime commands execute only the exact Git-private binary. A missing binary exits
  nonzero with the canonical setup command; PATH binaries, mise, and network are not
  runtime fallbacks.
- Setup promotes a candidate only after its supply-chain and version checks pass. A
  failure before final placement leaves no new or staged binary. Later config or hook
  installation failure may retain that verified Git-private cache for a safe retry.
- If repair of a mismatched old cache fails, runtime continues to reject that cache;
  it never executes a reported version that differs from `min_version`.
- Existing `core.hooksPath` configuration remains untouched. Resolve ownership instead
  of adding `--force` or resetting a local/global value.
- A copied runner supports only versions in its bundled trust manifest. Updating
  `min_version` alone cannot authorize a new release.

## Maintaining This Skill

When changing the bundled runner, keep its public seams as
`sh <runner> install` and `sh <runner> <lefthook-argv...>`. Add one black-box RED case
for the changed behavior, implement the smallest GREEN, then run:

```sh
sh -n <SKILL_PATH>/scripts/lefthook
python3 -B <SKILL_PATH>/scripts/lefthook_test.py
```

Update release hashes only from a verified official Lefthook release and retain a real
asset smoke test on every platform claimed by the change. Schema validation, simulated
platform mapping, and fake installers do not prove that a real target binary executes.
