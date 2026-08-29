# git-hook-pure

Read this file only after the user selects git-hook-pure.

## Fit

git-hook-pure is a small dispatcher for executable, repository-owned handlers under
`.githooks`. Prefer it when the project wants ordered custom scripts, a readable
standalone manager committed with the repository, offline hook execution, or a smaller
runtime dependency and supply-chain surface.

Prefer Lefthook when conventional jobs fit a declarative configuration and the project
already provisions Lefthook through Nix, mise, asdf, or another established tool path.

## Project-owned orchestration

git-hook-pure runs matching handlers in filename order; it is a dispatcher, not a task
graph. Do not create several handlers expecting them to run in parallel. When one hook
needs parallel work, make one hook-specific handler delegate to repository-owned
orchestration.

Prefer the parallel primitive of a task runner the repository already uses. Otherwise
implement the small amount of parallel logic in a script written in a language the
project already supports. That script must:

- start only independent jobs concurrently;
- forward the hook arguments or input each job actually needs;
- wait for every started job and return nonzero if any job fails;
- propagate cancellation and terminate its remaining child processes.

A bare `command & ...; wait` is incomplete when it loses a failure or leaves work
running after the hook is cancelled. If the script grows dependency ordering,
concurrency limits, retries, or structured output, use the repository's existing task
runner or revisit Lefthook instead of rebuilding a scheduler in hook code.

## Upstream owner

- Repository: <https://github.com/bolasblack/git-hook-pure>
- Installation and usage: <https://github.com/bolasblack/git-hook-pure#install>
- Releases and checksums: <https://github.com/bolasblack/git-hook-pure/releases>
- License: <https://github.com/bolasblack/git-hook-pure/blob/develop/LICENSE>

Upstream owns the executable, tests, license, checksums, and detailed behavior. Consult
those sources at adoption time. Pin an exact release rather than `latest`, review its
provenance, and follow the upstream license when the target repository vendors the
standalone file. Vendoring narrows runtime exposure; it does not remove bootstrap,
publisher, or repository-hook risk.

## Adopt it

1. Reconfirm that no existing manager or `core.hooksPath` owns the repository. If one
   does, stop and get an explicit migration or composition decision.
2. Choose an exact upstream release and a manager path that follows an existing
   repository convention. Use `tools/git-hook-pure` only when no stronger convention
   exists.
3. Download and review the installer from the selected release tag, then run it from a
   temporary path:

   ```sh
   version="<exact-version>"
   manager_path="./<manager-path>"
   installer="$(mktemp "${TMPDIR:-/tmp}/git-hook-pure-install.XXXXXX")"

   curl -fsSL \
     "https://raw.githubusercontent.com/bolasblack/git-hook-pure/v${version}/install-standalone.sh" \
     -o "$installer"

   # Review the pinned installer before running it.
   GIT_HOOK_PURE_VERSION="$version" \
     INSTALL_PATH="$manager_path" \
     sh "$installer"
   ```

   The installer downloads the matching release executable and `SHA256SUMS`, verifies
   its checksum and embedded version, installs the local hooks, and only then publishes
   the executable at `manager_path`. It requires `curl` plus `sha256sum` or `shasum`,
   but not npm or Node.js. Remove the temporary installer after success and do not
   commit it; commit the standalone manager with the approved project files.
4. Commit the standalone manager and add executable project handlers in one of the two
   native locations:

   ```text
   .githooks/<handler>             # every supported hook
   .githooks/<hook-name>/<handler> # one hook
   ```

   Reuse repository-owned lint, format, test, or validation commands; keep project
   policy out of the manager.
5. Make the existing setup or onboarding path run the committed manager after every
   fresh clone:

   ```sh
   ./<manager-path> install
   ```

   Do not create a task system or language dependency solely for this delegation.
6. Verify `./<manager-path> --version`, rerun `./<manager-path> install`, inspect Git's
   resolved hooks directory, and inspect the tracked diff. Exercise a real hook only
   when its command and possible mutations are safe; otherwise report live hook
   behavior as `unknown`.

**Done when:** the target repository owns one pinned standalone manager and its
executable handlers, fresh clones have one documented activation command, existing
hook ownership was preserved or explicitly resolved, and every performed or unrun
verification is reported accurately.
