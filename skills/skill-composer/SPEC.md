# Skill Composer Specification

## Cross-Harness by Default

A skill is cross-harness by default. Its required behavior must remain executable
without host-only enhancements. Every enhancement names its host, has a tested portable
fallback, and is not the sole owner of required state or input.

A skill may depend on host-only behavior when it explicitly declares that host as a
requirement and makes no broader compatibility claim.

## Proportionate Context Footprint

A skill sizes both the text exposed for discovery and the instructions loaded after
invocation in proportion to the behavior they enable. Discovery text gives each
distinct trigger branch one discriminating pointer. `SKILL.md` keeps instructions
shared across its branches in place and reaches branch-specific detail through explicit
pointers.

Reasonable size is a behavioral property rather than a universal line or token limit.
Every retained passage materially improves invocation or execution; pruning preserves
every required branch, invariant, and completion criterion.

## Package-Local Maintenance Context

Most skills have no `SPEC.md`. The file exists only when explicit, stable requirements
must constrain future rewrites but ordinary execution does not need them. It records
those current requirements and why each must survive. Runtime principles and workflows
remain in `SKILL.md`; this rare separation keeps maintainer-only context available
without loading it on ordinary invocations or duplicating the runtime contract.

A skill with releases of its own or independent distribution carries an evidence-backed
`CHANGELOG.md` recording what changed and why. It stays outside `SKILL.md` because
history is not a runtime instruction, and inside the package because repository history,
a multi-skill commit, or one platform's version identifier may not travel with the
skill. An unpublished, single-use skill carries neither an empty changelog nor a release
record it does not have.
