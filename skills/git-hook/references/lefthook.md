# Lefthook Branch

Read this file only after the user selects Lefthook.

The bundled runner avoids adding Lefthook to a language package manifest or changing
global Git configuration. A tracked runner bootstraps one trusted version into the
clone's Git common directory; installed hooks call that same runner. Setup may
provision the binary, while ordinary hook execution is offline and fail-closed.

The runner directly recognizes Linux, macOS, and Git for Windows on x86_64 or arm64.
Its source is `<SKILL_PATH>/scripts/lefthook`; copy it into the target repository rather
than linking back to the installed skill. A Lefthook executable found on `PATH` is not
the runtime owner of this branch.

## Branch Ownership

- The repository's one YAML Lefthook config owns `min_version`, hook jobs, remotes,
  and script references.
- The copied runner owns trusted release assets, checksums, platform mapping, and the
  Git-private binary location.
- The repository's existing setup surface owns fresh-clone activation.

The normal tracked result is one runner, one existing-or-new Lefthook YAML config, and
a small addition to an existing onboarding surface. The binary and generated hooks
stay under Git's private directory.

## Workflow

### Step 1: Resolve the config owner

Use one of Lefthook's supported YAML main-config names:

- `lefthook.yml`
- `lefthook.yaml`
- `.lefthook.yml`
- `.lefthook.yaml`
- `.config/lefthook.yml`
- `.config/lefthook.yaml`

Preserve an existing config and all existing jobs. If the repository has multiple main
configs, or only a TOML/JSON config, stop and surface the ownership decision instead of
creating a competing YAML file. When no config exists, follow an observed repository
convention or use `lefthook.yml` as the fallback.

Reconfirm that every existing non-sample hook and every visible `core.hooksPath` value
was disclosed before the user selected Lefthook. Lefthook 2.1.10 may rename an
existing target hook to `.old` and install its own wrapper without chaining the old
hook, so a force-free install is not automatic migration protection.

**Done when:** exactly one YAML config owner is selected, every existing job and hook
owner is preserved or covered by the user's migration decision, and no incompatible
`core.hooksPath` remains unresolved.

### Step 2: Choose the runner destination

Choose from repository evidence, not a universal directory preference. Reuse an
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

Use `scripts/lefthook` only when the repository has no stronger convention. State the
selected path and its evidence before editing.

**Done when:** one collision-free, non-ignored, repo-relative destination follows an
observed convention or the documented fallback.

### Step 3: Materialize the runner and configuration

Copy `<SKILL_PATH>/scripts/lefthook` byte-for-byte to the selected destination and make
the copied file executable. Do not reimplement its download or dispatch logic in a
package script, task runner, or second launcher.

Run `git check-attr text eol -- ./<runner-path>`. If existing attributes do not report
both `text: set` and `eol: lf`, add this narrow root-relative rule to the root
`.gitattributes`, creating that one file only when absent:

```gitattributes
/<runner-path> text eol=lf
```

Do not normalize unrelated paths. Re-copy the LF resource if the worktree copy contains
CRLF, then run `sh -n ./<runner-path>`.

Read the trusted manifest version from the copied runner:

```sh
sed -n 's/^trusted_release_version=//p' ./<runner-path>
```

Require exactly one `x.y.z` result. In the selected YAML config, preserve all existing
hooks and add or reconcile:

```yaml
min_version: "<trusted-release-version>"
assert_lefthook_installed: true
no_auto_install: true
lefthook: sh ./<runner-path>
```

`min_version` is the only project-facing version source. This branch strengthens it
from Lefthook's ordinary minimum into the exact version provisioned by the runner. Use
the official fields directly; arbitrary top-level `x-*` keys are custom-hook space and
`templates` replaces commands rather than storing private metadata.

When an existing `min_version` differs from the runner manifest, stop and surface the
version migration. Valid outcomes are an approved config migration or an independently
verified runner update; changing `min_version` alone cannot authorize a new release.

Keep jobs grounded in commands the repository already owns. Reuse existing task entry
points and extract a script only when several hooks need the same real logic. The
runner does not own lint, format, commit-message, or test policy.

**Done when:** the copied runner matches the bundled resource, attributes resolve to
`text: set` and `eol: lf`, shell syntax passes, the YAML has one exact supported
version and runner command, existing jobs remain, and every job resolves to a real
repository command or script.

### Step 4: Wire fresh-clone onboarding

The canonical setup command is:

```sh
sh ./<runner-path> install
```

Make an existing setup or bootstrap entry delegate to that command. Keep the direct
command discoverable in the existing README, CONTRIBUTING guide, or equivalent. Do not
create Make, just, mise, npm, or another task system solely for Git hooks, and do not
use a package lifecycle script as the universal entry.

**Done when:** a new contributor has one documented direct command and any existing
bootstrap entry delegates without duplicating setup logic.

### Step 5: Install and verify

Run the canonical setup command from the worktree. This is the only runner mode allowed
to provision a binary:

```sh
sh ./<runner-path> install
```

The runner:

1. Resolves the repository and Git common directory, including linked worktrees.
2. Rejects multiple YAML configs, a non-exact or unsupported version, an unknown
   platform, or any configured `core.hooksPath` before provisioning.
3. Uses `mise install-into` only when a standard project-root mise config is tracked,
   mise is on `PATH`, and that command is supported. It runs mise from an isolated
   install directory so fresh-clone trust state is not mutated. A failed mise install
   stops rather than switching supply chains.
4. Otherwise downloads the fixed official release asset, verifies the bundled
   SHA-256, and installs it under the Git common directory.
5. Runs `lefthook validate`, `lefthook install`, and `lefthook check-install` in order.

The direct download path requires `curl`, `gzip`, and either `sha256sum` or `shasum`.
Neither provisioning path writes project or global mise configuration or runs
`mise trust`.

After setup, run:

```sh
sh ./<runner-path> version
```

Inspect repository status and diff. Exercise a real hook only when its commands and
possible file mutations are safe for the task; otherwise report live hook behavior as
`unknown`.

**Done when:** setup and the version smoke check exit zero, `check-install` passed, no
global Git or mise config changed, tracked diffs contain only the approved adoption,
and every unrun hook or platform behavior remains explicit.

## Failure Contract

- Runtime executes only the exact Git-private binary. A missing binary exits nonzero
  with the canonical setup command; `PATH`, mise, and network are not runtime fallbacks.
- Setup promotes a candidate only after supply-chain and version checks pass. Failure
  before final placement leaves no candidate binary. A later validation or hook-install
  failure may retain the verified Git-private cache for safe retry.
- A mismatched cache is never executed.
- Existing `core.hooksPath` remains untouched; resolve its owner instead of forcing or
  resetting it.
- The copied runner supports only releases in its bundled trust manifest.

## Maintaining the Bundled Runner

Keep the public seams as `sh <runner> install` and
`sh <runner> <lefthook-argv...>`. For behavior changes, add one black-box RED case,
implement the minimum GREEN, then run:

```sh
sh -n <SKILL_PATH>/scripts/lefthook
python3 -B <SKILL_PATH>/scripts/lefthook_test.py
```

Update release hashes only from a verified official Lefthook release and retain a real
asset smoke test on every platform claimed by the update. Simulated mapping does not
prove that a real target binary executes.
