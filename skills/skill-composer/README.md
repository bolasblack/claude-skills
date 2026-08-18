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
- `REFERENCE.md` - Portable schemas, branch-only decision tables and review ledger, testing, troubleshooting, and durable distribution decisions
- `CHANGELOG.md` - Portable release history for Skill Composer
- `LICENSE.md` - Package-local copy of the repository's applicable use notice
- `scripts/fetch-harness-docs.py` - Optional standard-library fetcher for validated, provenance-bearing temporary evidence bundles
- `scripts/eval-skill.py` - Shared standard-library eval checker and Claude/Codex/Grok or external-adapter runner
- `evals/evals.json` and `evals/trigger-eval.json` - Skill Composer's functional and activation regression cases
- `package_test.py`, `scripts/eval-skill_test.py`, and `scripts/fetch-harness-docs_test.py` - Package-contract and black-box helper tests

## Validation

Run the bundled structural and transport suites from the Skill Composer directory:

```bash
python3 package_test.py
python3 scripts/eval-skill_test.py
python3 scripts/eval-skill.py check .
python3 scripts/fetch-harness-docs_test.py
```

A skill with an admitted suite keeps its own `evals/` and calls this shared runner
rather than copying it. Skill Composer itself owns such a suite. With explicit
authorization for target credentials, quota, and paid calls, run affected behavior
cases through a built-in target:

```bash
python3 scripts/eval-skill.py run /path/to/skill --case CASE_ID --target claude
python3 scripts/eval-skill.py run /path/to/skill --case CASE_ID --target codex
python3 scripts/eval-skill.py run /path/to/skill --case CASE_ID --target grok
```

Add `--model MODEL` when a specific model is part of the contract and
`--additional-skill NAME=/path/to/skill` for declared coexistence cases. Use
`-- ADAPTER [ARG ...]` when a clean external host can provide stronger activation,
baseline, or isolation evidence than a built-in target exposes. Candidate and grader
each receive the full `--timeout` bound, 900 seconds by default; an external adapter
receives that bound once per case. Built-in runs write safe `OBSERVE` phase records to standard error with
candidate/grader timing, periodic structural progress, output sizes, and
process-versus-protocol failure status; timeout summaries report event structure and stop
reason without printing prompts, rubrics, or model text.

For a slow or failed case, add `--artifacts-dir NEW_DIR` to preserve each sanitized
candidate workspace, `eval-result.json`, `candidate-events.jsonl`,
`candidate-timing.json`, stderr, and matching grader observations. This is opt-in because
fixtures and raw transcripts can be sensitive. Timing records retain provider tokens,
cost, turns, and duration when reported. The runner refuses an existing path and excludes
`.agents`, `.claude`, `.git`, and `.grok` target context from the saved workspace copy.

For trigger suites, `--repeat 3` reports a trigger rate and a strict-majority verdict at
the 0.5 threshold. Grok activation is attributable when its `system/init` catalog offers
the skill and the stream contains a matching `read_file` of the staged `SKILL.md`; its
fail-closed workspace profile also supports baseline and isolation. Codex trigger,
baseline, and isolation evidence remains `unknown` in built-in mode because its current
stream cannot prove those boundaries.

These suites are necessary, not sufficient: they check the packaged contract, eval
manifests and orchestration, and fetcher failure paths, but they cannot prove that a
target harness discovers, invokes, or correctly executes the skill. Run behavior cases
through a verified built-in target or external adapter, selecting affected case IDs after focused changes
and repeating stochastic trigger cases, or execute the same cases manually in fresh
sessions. Before a release, run the full owned suite when present, plus the current portable Agent
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

Follow the official [output-quality evaluation
loop](https://agentskills.io/skill-creation/evaluating-skills): compare the same prompt
with no skill or the previous skill version, grade observable assertions with concrete
evidence, review timing/tokens/cost and transcripts, and include human feedback. The
runner records case evidence and trigger aggregation, but does not yet generate
`benchmark.json`, blind comparison, human-feedback artifacts, or a trigger
train/validation split automatically.

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
