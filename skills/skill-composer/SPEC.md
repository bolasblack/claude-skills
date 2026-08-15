# Skill Composer Specification

## Cross-Harness by Default

A skill is cross-harness by default. Its required behavior must remain executable
without host-only enhancements. Every enhancement names its host, has a tested portable
fallback, and is not the sole owner of required state or input.

A skill may depend on host-only behavior when it explicitly declares that host as a
requirement and makes no broader compatibility claim.

**Why:** The user owns the cross-harness distribution promise. Without this invariant,
a convenient host enhancement can silently become the sole owner of required behavior
while the package still appears portable.

## Proportionate Context Footprint

A skill sizes both the text exposed for discovery and the instructions loaded after
invocation in proportion to the behavior they enable. Discovery text gives each
distinct invocation branch one discriminating trigger. `SKILL.md` keeps shared
instructions and branch-critical process state in place. Branch-only lookup material
moves behind an explicit read condition only when the context reduction justifies the
added navigation.

Reasonable size is a behavioral property rather than a universal line or token limit.
Every retained passage materially improves invocation or execution; pruning preserves
every required branch, invariant, and completion criterion.

**Why:** Discovery and invoked text compete for finite context, but mandatory splitting
can hide branch state and add navigation. The user requires measured context cost
without sacrificing behavior to a universal size cap.

## Environment-Native Automation

Repeated, deterministic work with a stable public boundary belongs in tested executable
helpers when that reduces agent reinterpretation; judgment remains in instructions and
executable changes follow TDD.

Language and dependency choices follow the supported environment and minimize total
installation, implementation, maintenance, and supply-chain cost. Portability is not
defined by one language or zero dependencies; this preserves deterministic behavior
without making environment-specific skills less compatible or more complex.

**Why:** Manual reinterpretation lets stable mechanics drift, while a universal Python
or zero-dependency rule can add more machinery than it removes. The user requires the
automation decision to follow the actual environment and public behavior seam.

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

**Why:** The user requires maintainer constraints and release rationale to survive when
a skill is rewritten or leaves its repository, without making ordinary invocations pay
for maintenance-only context or duplicating the runtime contract.
