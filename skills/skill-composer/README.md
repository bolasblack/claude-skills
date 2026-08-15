# Skill Composer

Primary policy for creating, updating, reviewing, and packaging agent skills. Based on the current [Agent Skills specification](https://agentskills.io/specification), target-platform documentation, and community patterns.

## Features

- Three-level progressive disclosure model (frontmatter > body > linked files)
- On-demand primary-source research for target-specific harness claims, with a portable SOP and optional provenance-bearing fetcher
- Environment-native automation that scripts repeatable mechanics with public-seam TDD and context-appropriate runtimes and dependencies
- Exceptional `SPEC.md` convention for stable maintainer-only requirements, with Skill Composer itself as a qualifying case
- Explicit authority over harness-injected authoring helpers such as `skill-creator`
- Portable-core plus harness-enhancement architecture for cross-agent skills
- Explicit create, update, review, and package/release workflows
- Optional composition with Matt Pocock's [writing-for-agents](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents)
- Five workflow patterns (sequential, multi-MCP, iterative, context-aware, domain-specific)
- Automatic- and explicit-invocation guidance balancing context load, cognitive load, and side-effect safety
- Portable frontmatter and durable decision guidance for target-specific validation and tool pre-approval
- Evidence-first evaluations covering triggering, function, isolation, and coexistence
- MCP + Skills integration guidance
- Cross-harness distribution decisions with exact target paths and behavior researched on demand
- Portable, evidence-backed skill-local changelogs with optional causal examples for independently distributed releases

## Files

- `SKILL.md` - Main skill definition and create/update/review/package workflows
- `SPEC.md` - Skill Composer's rare maintainer-only contract; generated skills omit it unless they pass the admission test
- [HARNESS-RESEARCH.md](HARNESS-RESEARCH.md) - On-demand primary-source research SOP and portable fallback for target-specific claims
- `REFERENCE.md` - Portable schemas, branch-only decision tables and review ledger, testing, troubleshooting, and durable distribution decisions
- `CHANGELOG.md` - Portable release history for Skill Composer
- `LICENSE.md` - Package-local copy of the repository's applicable use notice
- `scripts/fetch-harness-docs.py` - Optional standard-library fetcher for validated, provenance-bearing temporary evidence bundles
- `package_test.py` and `scripts/fetch-harness-docs_test.py` - Package-contract and black-box fetcher tests

## Validation

Run the bundled structural and transport suites from the Skill Composer directory:

```bash
python3 package_test.py
python3 scripts/fetch-harness-docs_test.py
```

These suites are necessary, not sufficient: they check the packaged contract and
fetcher failure paths, but they cannot prove that a target harness discovers, invokes,
or correctly executes the skill. Before a release, run the current portable Agent
Skills validator and every named target's validator, then keep this behavior ledger for
each claimed harness, surface, and model:

| Workflow or gate | Required evidence |
|---|---|
| Create | fresh-context activation and a functional creation scenario |
| Update | A regression scenario that changes the requested branch and preserves unrelated behavior |
| Review | A fresh read-only full-package review that does not mutate the target |
| Package/release | The exact artifact passes a clean installation and exercises every supported workflow branch |
| Trigger boundary | Intended trigger, paraphrase, realistic near-miss, and ambiguity cases when model invocation is claimed |
| Portability | The portable fallback completes without each host-only enhancement |
| Composition | isolation and coexistence cases pass alongside likely overlapping skills |

Record every unavailable or unrun validator, target, surface, model, or behavior case as
`unknown`; it does not support the corresponding release claim.

The fetcher runtime uses only Python's standard library. Its black-box suite uses
`openssl` to generate a temporary certificate. One write-failure cleanup check uses POSIX
file-size limits and is skipped where that facility is unavailable.

## Provenance and License

Earlier release history attributes the original version to
[caoer](https://github.com/caoer), but the exact upstream artifact and its license have
not been verified. This package therefore does not infer upstream redistribution
rights. Its applicable repository notice travels in [LICENSE.md](LICENSE.md). v3.0.0
was rewritten using Anthropic's official guide; current work tracks the open
specification and researches target-specific facts on demand.
