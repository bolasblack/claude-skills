# Git Hook Specification

## General Git-Hook Boundary

The skill remains named, discovered, and organized around reusable Git-hook automation.
Each hook manager is an explicit implementation branch; no current manager becomes the
identity or complete trigger surface of the skill. A generic Git-hook request preserves
the repository's existing manager until migration is explicitly chosen.

**Why:** The user expects other Git-hook tools to be supported over time. Coupling the
skill's identity to Lefthook would make future branches awkward and could turn a generic
request into an unintended migration.

## Reusable Default, Contextual Fit

Provide one reusable adoption default aimed at roughly 80–90% of ordinary Git-hook
needs across arbitrary repositories without rewriting the skill. Reuse hook
configuration and supporting scripts where their policy is shared, while leaving
project-specific jobs and commands with the repository that owns them.

The agent adapts materialization to repository evidence. In particular, it chooses the
tracked runner or script location from an existing repo-owned convention and uses a
documented fallback only when no convention exists.

**Why:** The user wants to maximize reuse, while repositories use different native
layouts such as `scripts/`, `.bin/`, or another suitable location. One universal path
such as `tools/lefthook` would reduce that fit.

## Clean Repository-Local Adoption

Adoption stays repository-local, avoids changing global Git or tool configuration, and
adds only the smallest justified tracked surface. It does not introduce or modify an
unrelated language package manager, lifecycle hook, or task system solely to install Git
hooks. Downloaded installation artifacts and installed hook state under Git-private
paths remain clone-private. Reusable source configuration and hook scripts may be
tracked according to the manager's native model.

**Why:** The user requires a clean installation that neither pollutes the host
environment nor spreads setup across unnecessary files and ecosystems.

## Lefthook Project Version Owner

In the Lefthook branch, the repository's YAML `min_version` field is the single
project-facing owner of the selected Lefthook version. Bootstrap trust data is not a
second user-configurable version source. Other manager branches follow their native
repository-local version model.

**Why:** The user wants the version to travel with the reusable hook configuration.
One visible project owner prevents setup commands, hidden metadata, and external
manifests from drifting independently.

## Lefthook Copied Bootstrap Runner

In the Lefthook branch, package deterministic bootstrap mechanics with the skill and
copy them into the target repository rather than linking the repository back to an
installed skill. Explicit setup obtains the selected binary without requiring a
globally installed hook manager: prefer a compatible project-adopted mise setup when
available, otherwise use a verified official release path. Neither provisioning path
changes global configuration or silently trusts new release material.

Other manager branches may use their native repository-local installation model and
are not required to copy a runner, use mise, or download a standalone release.

**Why:** The user wants reusable setup that can honor a project's existing mise choice
without making mise, a language package, or a global Lefthook installation a universal
prerequisite.

## Explicit Fresh-Clone Activation

Every manager branch gives a newly cloned worktree one documented repository-local
activation path and does not assume clone will execute repository code. Reuse an
existing onboarding or bootstrap surface when present, while keeping a direct command
available without introducing a new task system. In the Lefthook branch, provisioning
happens only during explicit setup; ordinary hook execution remains offline and fails
with setup guidance when its binary is missing. Required checks remain independently
enforced outside local hooks.

**Why:** Git does not activate tracked hook configuration during clone. An explicit,
discoverable setup makes fresh clones predictable without making checkout execute
repository code or treating optional local hooks as enforcement.
