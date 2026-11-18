# Skill Composer

Create and maintain skills that work across agent harnesses, with opt-in infrastructure for repeatable evals. Skill Composer is based on the current [Agent Skills specification](https://agentskills.io/specification), target-platform documentation, and community patterns.

## Beyond Scaffolding

Skill Composer owns the whole skill package, not merely the generation of a plausible `SKILL.md`. Harness-provided helpers such as `skill-creator` can still contribute platform-specific scaffolding, schema validation, or evaluation capabilities, but their defaults are advisory inputs. Skill Composer retains the decisions about scope, structure, portability, validation, packaging, release history, and quality.

| Dimension | Scaffolding-focused composer/helper | Skill Composer |
|---|---|---|
| Lifecycle | Generate an initial skill | Create, update, read-only review, package, and release |
| Portability | Optimize for one agent harness | Start with a portable core; name each host-only enhancement and require a fallback |
| Evidence | Treat plausible instructions or schema validation as completion | Separate schema from behavior, maintain a validation ledger, and leave unsupported target claims `unknown` |
| Evals | Outside the scaffolding task | Provide opt-in manifests and fixtures plus a shared runner for repeatable functional, activation, isolation, and coexistence checks |
| Maintenance | Hand off the generated files | Own the package references, tested automation, and evidence-backed release history |
| Context | Add guidance until the prompt looks complete | Cap `SKILL.md` at 15,000 bytes with standing rules first, and move only one branch's workflow or lookup material behind explicit read conditions |

Use Skill Composer when a skill must remain maintainable across agent harnesses, future updates, independent review, and standalone distribution. Use a scaffolding helper alone when a one-off first draft is the whole job.

## Features

- A 15,000-byte `SKILL.md` cap with standing rules first, references read in full, and cross-skill pointers that invoke by name, so a skill survives hosts that keep only its start after context compaction
- Terse `SKILL.md` requirements: what a script can check is left to the package check, and detailed reasons sit in a reference or `SPEC.md` behind a link
- On-demand primary-source research for target-specific harness claims, with a portable SOP and optional provenance-bearing fetcher
- Environment-native automation that scripts repeatable mechanics with public-seam TDD and context-appropriate runtimes and dependencies
- Exceptional `SPEC.md` convention for stable maintainer-only requirements, with Skill Composer itself as a qualifying case
- Explicit authority over harness-injected authoring helpers such as `skill-creator`
- Portable-core plus harness-enhancement architecture for cross-agent skills
- Explicit create, update, review, and package/release workflows
- Bundled core writing rules in `references/writing.md`, drawing on Matt Pocock's [writing-for-agents](https://github.com/mattpocock/skills/tree/main/skills/productivity/writing-for-agents), which replaces them when installed
- A bundled package check, `scripts/check-skill.py`, run on every skill Skill Composer creates, updates, or reviews
- Five workflow patterns (sequential, multi-MCP, iterative, context-aware, domain-specific)
- Automatic- and explicit-invocation guidance balancing context load, cognitive load, and side-effect safety
- Portable frontmatter and durable decision guidance for target-specific validation and tool pre-approval
- Evidence-first behavioral validation, with packaged evals added on request or maintained when already present
- One-owner repeatable eval infrastructure with isolated fixtures, built-in Claude/Codex/Grok runs, and an external-adapter seam
- MCP + Skills integration guidance
- Cross-harness distribution decisions with exact target paths and behavior researched on demand
- Portable, evidence-backed skill-local changelogs with optional causal examples, dated by default and versioned when a skill ships under a version

## Files

- `SKILL.md` - Main skill definition, standing rules, workflow router, and create/update workflow
- [references/review.md](references/review.md) and [references/release.md](references/release.md) - Review and package/release workflows, read in full when their branch is selected
- `SPEC.md` - Skill Composer's rare maintainer-only contract; generated skills omit it unless they pass the admission test
- [HARNESS-RESEARCH.md](HARNESS-RESEARCH.md) - On-demand primary-source research SOP and portable fallback for target-specific claims
- `references/frontmatter.md`, `package-layout.md`, `portability.md`, `distribution.md`, `workflow-patterns.md`, `authoring-examples.md`, `writing.md`, `changelog.md`, and `troubleshooting.md` - Portable lookup material, one file per concern, each read in full when its `SKILL.md` pointer fires
- [references/evaluation.md](references/evaluation.md) - Conditionally loaded eval-suite contract, target evidence boundaries, and tuning methodology
- `CHANGELOG.md` - Portable release history for Skill Composer
- `LICENSE.md` - Package-local copy of the repository's applicable use notice
- `scripts/fetch-harness-docs.py` - Optional standard-library fetcher for validated, provenance-bearing temporary evidence bundles
- `scripts/check-skill.py` - Shared standard-library package check: entry-point byte cap, frontmatter, local links, whole-file pointers, cross-skill links and URLs, nested entry points, reachable references, and the `SPEC.md` pointer
- `scripts/eval-skill.py` - Shared standard-library eval checker and Claude/Codex/Grok or external-adapter runner
- `evals/evals.json` and `evals/trigger-eval.json` - Skill Composer's functional and activation regression cases
- `package_test.py`, `scripts/check-skill_test.py`, `scripts/eval-skill_test.py`, and `scripts/fetch-harness-docs_test.py` - Package-contract and black-box helper tests

## Validation

Run the bundled local suites from the Skill Composer directory:

```bash
python3 package_test.py
python3 scripts/check-skill_test.py
python3 scripts/check-skill.py .
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

## Resources and Community

If you're building your first skill, start with the portable rules in this package. Use [Harness Research](HARNESS-RESEARCH.md) to locate fresh target guidance only when a target-specific branch requires it.

### Current Documentation

Use the trust anchors and source-selection procedure in [Harness
Research](HARNESS-RESEARCH.md). This reference deliberately does not cache current
target instructions or remembered vendor URLs.

### Background

- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — the original architecture discussion and later open-standard update

### Public Skills Repository

GitHub: [anthropics/skills](https://github.com/anthropics/skills) — Contains Anthropic-created skills you can browse and customize. Use these as reference implementations when building your own.

### Auxiliary Skill-Authoring Helpers

A harness may inject `skill-creator` or an analogous helper. Use a helper for capabilities tied to that harness, such as scaffolding, schema validation, or isolated evaluation. Treat its general authoring advice as advisory and apply the [Authoring Authority](SKILL.md#authoring-authority) rule before accepting it.

In particular, do not let a helper's generic packaging preference erase an explicit portable-release requirement. Verify which statements are real target-platform constraints; keep the rest subordinate to Skill Composer's design policy.

### Getting Support

**For technical questions:**
- Community forums at the [Claude Developers Discord](https://discord.gg/claudedev) — general questions, best practices, sharing skills

**For bug reports:**
- GitHub Issues: [anthropics/skills/issues](https://github.com/anthropics/skills/issues)
- Include: skill name, error message, steps to reproduce
