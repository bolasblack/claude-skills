---
name: git-hook
description: "Assess, adopt, or harden repository-local Git-hook automation. Use when setting up or standardizing project hooks, choosing between Lefthook and git-hook-pure, migrating an existing hook manager, reusing hook configuration or scripts, or bootstrapping hooks for fresh clones."
---

# Git Hook

When modifying or reviewing this skill, read [SPEC.md](SPEC.md) first. It holds the
user-owned requirements that must survive tool branches and rewrites; ordinary Git-hook
adoption does not need it.

This skill automates two explicit manager branches: Lefthook and git-hook-pure. A
generic setup request starts with assessment and recommendation, not installation. The
user owns the manager choice. If the request already names a manager, that choice gate
is satisfied unless it conflicts with an existing hook owner.

Both documented branches require Git 2.31 or newer and a POSIX/Bourne-compatible
shell. Their supported Windows surface is Git Bash.

`<SKILL_PATH>` means the loaded base directory of this skill. Copy a resource only when
the selected branch explicitly identifies it as bundled; never link a repository back
to the installed skill. The Lefthook runner is bundled here. git-hook-pure remains
upstream-owned and is obtained from an exact upstream version by the target repository.

## Ownership

- The user owns the manager selection and every migration decision.
- An existing hook manager, `core.hooksPath`, or hand-written hook remains the current
  owner until the user explicitly chooses replacement or composition.
- The selected manager branch owns its installation and runtime model.
- The repository owns hook policy, commands, tracked configuration, and handler
  scripts.
- Git owns clone-local hooks under its resolved hooks directory. CI or server-side
  checks remain the enforcement owner because fresh clones have no installed hooks.

## Workflow

### Step 1: Inspect without mutation

Read repository guidance and inspect the worktree before recommending a manager. Find:

- unrelated dirty or staged files that must be preserved;
- existing hook-manager configs, executable non-sample files in Git's resolved hooks
  directory, and every visible `core.hooksPath` scope;
- repository-owned commands and the hooks that should run them;
- tracked script or executable directories and their naming conventions;
- the existing setup, bootstrap, devcontainer, or onboarding entry point;
- an active project tool owner such as a Nix flake/dev shell, mise config, or asdf
  `.tool-versions`, and whether it already supplies or can naturally pin Lefthook;
- whether `lefthook` is available on the current `PATH`;
- explicit requirements for custom executable handlers, offline or self-contained
  operation, auditable vendoring, minimum hook-manager supply-chain surface, or code
  provenance.

Do not treat the mere presence of a Nix, mise, or asdf file as project adoption; check
repository guidance and actual usage. A `lefthook` executable found only on the current
machine is local convenience evidence, not fresh-clone provisioning.
git-hook-pure v4's upstream documentation discloses substantial AI assistance; when a
repository has a provenance policy, surface that compatibility fact before recommending
the branch.

**Done when:** repository rules, dirty state, current hook owner, available commands,
onboarding owner, Lefthook supply evidence, and any custom or supply-chain constraint
are each known or explicitly absent, with no repository mutation performed.

### Step 2: Recommend one manager and wait

Apply these rules in order; do not score the repository or build a comparison matrix:

1. When a hook manager already owns the repository, recommend preserving it. Migration
   requires an explicit user decision.
2. Otherwise recommend **git-hook-pure** when the hooks are best expressed as ordered,
   repository-owned executables, or when the user or repository explicitly requires
   offline/self-contained operation, reviewable vendoring, or minimum manager
   supply-chain surface.
3. Otherwise recommend **Lefthook** when ordinary hook jobs fit its configuration model
   and an active Nix/mise/asdf setup can supply it, or Lefthook is already available in
   the current environment.
4. When neither manager has an existing supply advantage, recommend
   **git-hook-pure** because its manager is vendored with the repository; explain that
   Lefthook remains the simpler configuration model for conventional jobs if the user
   prefers to add its binary supply path.

Explicit custom or supply-chain requirements outweigh Lefthook installation
convenience. Lefthook availability never overrides an existing hook owner. When only a
current-machine Lefthook binary exists, disclose that other contributors and fresh
clones still need repository-local setup.

Report exactly:

- the current hook owner, if any;
- the recommendation and the observed facts supporting it;
- the alternative and when it would fit better;
- the fresh-clone and supply-chain consequence of each option;
- any migration or compatibility decision still required.

Then stop. Do not add configuration, copy a bundled resource, install hooks, alter a
toolchain file, or change Git configuration until the user selects a manager. If the
user's original request explicitly selected a manager, report the assessment and
continue without asking them to repeat that selection.

**Done when:** one recommendation and its alternative are explained from repository
evidence, and the user has either explicitly selected a manager or the workflow is
waiting without mutation.

### Step 3: Run only the selected branch

- For **Lefthook**, read [references/lefthook.md](references/lefthook.md) completely,
  then follow it.
- For **git-hook-pure**, read
  [references/git-hook-pure.md](references/git-hook-pure.md) completely, then follow it.
- For another manager, identify its native repository owner and stop before using
  either documented branch's installation path. This skill does not automate that
  branch yet.

Perform the selected branch's compatibility checks before mutation. A failed check is
a blocker to report, not permission to switch managers silently.

**Done when:** exactly one selected branch has completed its own installation and
verification contract, or the branch has stopped with an evidence-backed blocker and
no unapproved fallback.

### Step 4: Report the resulting repository

Report the selected manager, tracked files changed, the direct fresh-clone activation
command, and every verification result. Distinguish a tested hook from configuration
or installation checks; unsafe or unrun hook behavior remains `unknown`. Confirm that
no global Git or tool configuration changed and that required checks remain enforced
outside local hooks.

**Done when:** the user can see what owns hook policy, how a fresh clone activates it,
what was actually tested, and any remaining unknown without relying on earlier status
updates.

## Failure Contract

- Never reset, override, or silently follow an existing `core.hooksPath`.
- Never replace or compose with an existing hook owner without the user's explicit
  decision.
- Never use a different manager because the selected branch fails installation.
- Preserve unrelated dirty and staged files throughout adoption.
- Local hooks are convenience and feedback; they are not the sole enforcement path.
