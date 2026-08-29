# Git Hook Specification

## General Git-Hook Boundary

The skill remains named, discovered, and organized around reusable Git-hook automation.
Each hook manager is an explicit implementation branch; no current manager becomes the
identity or complete trigger surface of the skill. A generic Git-hook request preserves
the repository's existing manager until migration is explicitly chosen.

**Why:** The user expects other Git-hook tools to be supported over time. Coupling the
skill's identity to one manager could turn a generic request into an unintended
migration.

## Assessment and User Decision

Generic setup first inspects the repository, recommends one manager from observable
fit, explains the alternative, and waits for the user's selection before mutation. An
explicit manager named in the request already supplies that selection unless it
conflicts with an existing owner. Selection uses existing ownership, the natural hook
expression model, available project tooling, and explicit operating or supply-chain
constraints; it does not use a score.

Lefthook is the ordinary-project recommendation when its configuration model fits and
the project or current environment already makes it low-friction. git-hook-pure is the
recommendation for repository-owned executable composition, explicit offline or
self-contained operation, auditable vendoring, or minimum manager supply-chain surface.
Current-machine availability is disclosed separately from reproducible fresh-clone
provisioning.

**Why:** The user wants a small, understandable assessment and retains the final choice.
Separating facts, recommendation, and selection prevents setup from silently encoding
the agent's risk tolerance or replacing an existing owner.

## Reusable Default, Contextual Materialization

Provide reusable adoption paths aimed at ordinary Git-hook needs across arbitrary
repositories. Reuse hook configuration and supporting scripts where policy is shared,
while leaving project-specific jobs and commands with the repository that owns them.

The agent chooses tracked runner, manager, and handler locations from existing
repo-owned conventions and uses a branch-specific documented fallback only when no
convention exists.

**Why:** Repositories use different native layouts such as `scripts/`, `bin/`, or
`tools/`. One universal path would reduce reuse and create unnecessary structure.

## Clean Repository-Local Adoption

Adoption stays repository-local, avoids changing global Git or tool configuration, and
adds only the smallest justified tracked surface. It does not introduce or modify an
unrelated language package manager, lifecycle hook, or task system solely to install
Git hooks. Downloaded installation artifacts and installed hook state under Git-private
paths remain clone-private. Reusable source configuration, vendored managers, and hook
scripts may be tracked according to the selected manager's native model.

**Why:** Installation should neither pollute the host environment nor spread setup
across unnecessary files and ecosystems.

## Lefthook Project Version Owner

In the Lefthook branch, the repository's YAML `min_version` field is the single
project-facing owner of the selected Lefthook version. Bootstrap trust data is not a
second user-configurable version source.

**Why:** One visible project owner prevents setup commands, hidden metadata, and
external manifests from drifting independently.

## Lefthook Copied Bootstrap Runner

The Lefthook branch copies deterministic bootstrap mechanics from the skill into the
target repository rather than linking back to the installed skill. Explicit setup
obtains the selected binary without requiring a globally installed manager: it prefers
a compatible project-adopted mise setup when available and otherwise uses a verified
official release path. Neither path changes global configuration or silently trusts
new release material.

**Why:** Lefthook remains reproducible for fresh clones while honoring an existing mise
choice without making a language package or global installation universal.

## git-hook-pure Upstream-Owned Adoption

The git-hook-pure branch owns only selection and adoption guidance. The official
repository remains the source of its executable, tests, license, release checksums, and
detailed operating documentation. This skill does not redistribute those upstream
artifacts or become a second version and release owner.

When a target repository selects git-hook-pure, it pins an exact upstream version and
vendors the standalone executable through that tag's upstream `install-standalone.sh`.
npm and Node.js are not installation prerequisites. The committed executable's
embedded version is that repository's project-facing version owner; ordinary hook
execution then needs no package manager, network, or external hook-manager binary.

**Why:** Keeping implementation and release evidence with upstream avoids stale copies
and avoids assuming a language toolchain merely to adopt a shell hook manager, while
target-repository vendoring still provides repository-owned executable composition and
a smaller runtime supply-chain surface. It does not remove trust in the publisher,
bootstrap, or repository hook code.

## Explicit Fresh-Clone Activation

Every manager branch gives a newly cloned worktree one documented repository-local
activation path and does not assume clone will execute repository code. Reuse an
existing onboarding or bootstrap surface when present, while keeping a direct command
available without introducing a new task system. Required checks remain independently
enforced outside local hooks.

**Why:** Git does not activate tracked hook configuration during clone. Explicit setup
makes fresh clones predictable without executing repository code during checkout or
treating optional local hooks as enforcement.
