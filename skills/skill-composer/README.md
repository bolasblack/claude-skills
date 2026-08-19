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
- Evidence-first behavioral validation, with packaged evals added on request or maintained when already present
- One-owner repeatable eval infrastructure with isolated fixtures, built-in Claude/Codex/Grok runs, and an external-adapter seam
- MCP + Skills integration guidance
- Cross-harness distribution decisions with exact target paths and behavior researched on demand
- Portable, evidence-backed skill-local changelogs with optional causal examples for independently distributed releases

## Files

- `SKILL.md` - Main skill definition and create/update/review/package workflows
- `SPEC.md` - Skill Composer's rare maintainer-only contract; generated skills omit it unless they pass the admission test
- [HARNESS-RESEARCH.md](HARNESS-RESEARCH.md) - On-demand primary-source research SOP and portable fallback for target-specific claims
- `REFERENCE.md` - Portable schemas, branch-only authoring decisions, review ledger, troubleshooting, and durable distribution guidance
- [references/evaluation.md](references/evaluation.md) - Conditionally loaded eval-suite contract, target evidence boundaries, and tuning methodology
- `CHANGELOG.md` - Portable release history for Skill Composer
- `LICENSE.md` - Package-local copy of the repository's applicable use notice
- `scripts/fetch-harness-docs.py` - Optional standard-library fetcher for validated, provenance-bearing temporary evidence bundles
- `scripts/eval-skill.py` - Shared standard-library eval checker and Claude/Codex/Grok or external-adapter runner
- `evals/evals.json` and `evals/trigger-eval.json` - Skill Composer's functional and activation regression cases
- `package_test.py`, `scripts/eval-skill_test.py`, and `scripts/fetch-harness-docs_test.py` - Package-contract and black-box helper tests

## Validation

Run the bundled local suites from the Skill Composer directory:

```bash
python3 package_test.py
python3 scripts/eval-skill_test.py
python3 scripts/eval-skill.py check .
python3 scripts/fetch-harness-docs_test.py
```

These checks are necessary, not sufficient evidence of target behavior. Skill Composer
owns an admitted suite, while a skill without an admitted suite remains valid and uses
the applicable validators and manual scenarios.

For suite admission, manifests, the shared runner, Claude/Codex/Grok target commands,
observability, artifact handling, acceptance evidence, and tuning, read the
[Evaluation Reference](references/evaluation.md). Live target runs require explicit
authorization for credentials, quota, paid calls, and any real external effect.

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
