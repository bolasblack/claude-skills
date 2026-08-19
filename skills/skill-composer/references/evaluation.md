# Skill Evaluation Reference

This branch-only reference owns admitted eval-suite design, execution, observability,
and tuning. Reach it through the conditional pointer in
[Step 8](../SKILL.md#step-8-validate-behavior-and-maintain-admitted-evals); validation
for a skill without an admitted suite does not load it.

The case-design and iteration methodology adapts parts of the official Agent Skills
guide, [Evaluating skill output
quality](https://agentskills.io/skill-creation/evaluating-skills). Skill Composer's
manifest schema, runner protocol, target adapters, and evidence limits remain the
package-local contract documented here.

## Repeatable Evaluation Contract

The admission decision lives in [Step 8](../SKILL.md#step-8-validate-behavior-and-maintain-admitted-evals).
Use the bundled standard-library helper as a package-local evaluation seam when the
target owns an admitted suite. A package without evals is valid when neither admission
condition applies:

```bash
python3 /path/to/skill-composer/scripts/eval-skill.py check /path/to/skill
python3 /path/to/skill-composer/scripts/eval-skill.py run /path/to/skill \
  [--case CASE_ID] [--repeat 3] [--model MODEL] \
  [--reasoning-effort EFFORT] --target claude|codex|grok
python3 /path/to/skill-composer/scripts/eval-skill.py run /path/to/skill \
  --additional-skill NAME=/path/to/skill --target TARGET
python3 /path/to/skill-composer/scripts/eval-skill.py run /path/to/skill \
  [--case CASE_ID] [--repeat 3] -- ADAPTER [ARG ...]
```

Give the runner one repository owner and let each evaluated skill own only its manifests
and fixtures. Do not copy the helper into every sibling package. A standalone
self-validating distribution may vendor a pinned copy only when it cannot call a shared
repository owner; include the matching black-box test and record the Skill Composer
release or artifact hash that identifies the copy.

`check` validates the skill's package identity, rejects symlinks before staging, and
checks eval manifests, identifiers, safe side-effect declarations, assertions, and
fixture paths. It is not the portable Agent Skills schema validator or a target
validator, and it supplies no activation or functional evidence.

Keep domain truth with the evaluated skill:

- `evals/evals.json` owns functional, baseline, isolation, and coexistence cases. Each
  case declares a hyphen-case `id`, `category`, realistic `prompt`, `side_effects` as
  `none` or `fixture`, and one or more independently checkable `assertions`. Optional
  `files` resolve beneath `evals/fixtures`; `skill_mode` is `enabled` or `disabled`;
  `additional_skills` contains unique skill names. Baseline cases disable the evaluated
  skill, other categories keep it enabled, coexistence names at least one additional
  skill, and isolation names none.
- `evals/trigger-eval.json` owns model-invocation boundaries. Each query declares an
  `id`, realistic `query`, and boolean `should_trigger`; optional `files` stage trigger
  context from `evals/fixtures`, and optional `additional_skills` stage realistic
  competitors. A package-local competitor can live at
  `evals/fixtures/skills/<name>`; an explicitly supplied `--additional-skill` mapping
  takes precedence. A present trigger suite must contain both positive and negative
  cases.
- Both documents use `schema_version: 1` and a `skill_name` matching `SKILL.md` and the
  package directory. Unknown fields fail closed so misspellings cannot silently weaken
  a gate. At least one case must exist across the two manifests; an empty package is
  not a valid eval contract.

`run` validates first, then creates a new temporary workspace for every case and
iteration. It copies the skill without `evals/` and stages only declared fixture inputs.
Repeat `--case` to run affected IDs after a focused change; omitted `--case` runs the
whole suite, while an unknown or duplicate ID is a command-contract error. `--model`
overrides the selected target's model. `--reasoning-effort` supports target-specific
values for Claude and Codex. Claude accepts `low`, `medium`, `high`, `xhigh`, or `max`
through Claude's `--effort` flag; Codex accepts `minimal`, `low`, `medium`, `high`, or
`xhigh` through Codex's `model_reasoning_effort` configuration. The runner rejects
values outside the selected target's set and rejects the option for other targets before
a provider call. It passes the selected effort explicitly to both the candidate and
independent grader instead of relying on ambient target configuration. Whether a
particular model supports the selected value remains target-runtime evidence.
A case that declares `additional_skills` needs one package-local fixture or
`--additional-skill NAME=PATH` mapping per named package in built-in mode; a missing
mapping becomes `unknown`, while a malformed or mismatched package is a command-contract
error. With `--repeat`, functional iterations retain their individual verdicts. Trigger
iterations are aggregated by strict-majority at the fixed 0.5 threshold and emit a
`TRIGGER_RATE` record; an undecidable result containing too many `unknown` observations
remains `unknown`.

Built-in mode supports Claude, Codex, and Grok behind the same interface. It stages only
the selected project-local skill copies and never passes assertions or expected trigger
answers to the candidate session. For a functional case, it then starts a separate
grader session with no candidate skill loaded, a read-only copy of the resulting
workspace, before-and-after hashes, the target event stream, the final response, and the
assertions. The grader must return schema-conforming results for every assertion; Claude
and Codex use their structured-output controls, while Grok completes a no-plan streaming
tool session. A Grok response is complete only when its result reports `end_turn`; the
runner reads a non-blank terminal result or, when that field is empty, the unique textual
`end_turn` assistant message, then validates that final text as JSON. It accepts either a
bare JSON object or one whole-response `json` code fence; it never extracts an object from
surrounding prose. Tool-use and thinking blocks are never verdicts. A missing, malformed,
partial, or reused grader session becomes `unknown`. The candidate and grader never
share conversation state and each receive the full `--timeout` bound; the default is
900 seconds per built-in phase. An external adapter receives that bound once for the
whole case. The assertion count and ID order are stated explicitly; a progress update
or stated intent is not completion evidence.

Built-in runs emit `OBSERVE` records to standard error for candidate and grader starts,
periodic progress, completed process timings and byte counts, process failures, and
protocol failures. Progress and timeout records report only structural output
diagnostics—byte counts, JSON-event counts, event types, tool-call names and counts,
tool-result success/error counts, and the last stop reason—so a run is debuggable without
printing tool arguments, prompts, rubrics, model text, session IDs, or credentials. Tool
targets are reported only as sanitized workspace-relative paths and counts; any external
target is collapsed to `<outside-workspace>`. On POSIX, timeout cleanup signals the target
process group, bounds the final pipe-drain interval, and closes this run's capture pipes
rather than waiting indefinitely on a detached process that inherited them.

Use `--artifacts-dir NEW_DIR` when a slow or failed run needs filesystem-level debugging.
The option is explicit because fixture state can be sensitive: it refuses to overwrite an
existing path or write inside the evaluated skill package, then stores one sanitized
workspace and `eval-result.json` under `CASE_ID/iteration-N/`. Its `observation/`
directory stores `candidate-events.jsonl`, `candidate-stderr.txt`, and
`candidate-timing.json`, plus the matching grader files when grading starts. Timing
records include wall duration, structural output summary, and provider-reported tokens,
cost, turns, and provider duration when the terminal event supplies them. Raw event and
stderr artifacts can contain model text, tool arguments, fixture contents, or target
identifiers, so treat the whole explicit artifact directory as sensitive evidence. The
saved workspace omits `.agents`, `.claude`, `.git`, and `.grok`, so staged target context
and additional skill copies are not persisted. Without this option, every case workspace
remains temporary.

Built-in target support deliberately stops where the current structured evidence stops:

- **Claude:** a matching structured `Skill` call proves activation. A negative result
  additionally requires the initialization catalog to prove the skill was offered.
  Fixture-writing functional runs require Claude's native sandbox to start in strict
  fail-closed mode. When the Linux process is UID 0 and `bwrap` is available, the runner
  starts only the writable candidate through a user namespace that maps it to a non-root
  UID before Claude starts. This avoids the root-only nested UID-mapping failure without
  disabling Claude's native sandbox or its Unix-socket filter. If either the identity
  translation or native sandbox is unavailable, the result is `unknown`.
- **Codex:** ephemeral structured runs support functional candidate and grader sessions.
  Its current event stream has no attributable automatic skill activation event, so
  trigger results remain `unknown` without spending a target call.
- **Grok:** fresh no-memory streaming tool sessions support functional candidates and
  graders under a fail-closed custom sandbox profile that extends strict mode, denies
  known ambient user-skill roots and the original source packages, disables network
  access, and stages only the selected project-local copies. The profile collapses
  redundant descendant denials so nested package-local competitor fixtures remain
  mountable. A `system/init` catalog advertising the evaluated skill plus a matching
  `read_file` call for its staged `SKILL.md` proves positive activation. For a negative
  case, the same catalog plus a decisive assistant event without that matching read
  proves non-activation; the runner may stop at that point to reduce cost. Completed
  `end_turn` responses provide functional text. This controlled workspace also supports
  Grok baseline and isolation cases; if the profile is unavailable or does not start
  fail closed, the result is `unknown`.

The built-in Codex command cannot prove that ambient user skills were absent, so Codex
baseline and isolation categories remain `unknown`. Use an external adapter in a clean
host when those claims matter. A built-in target executable that is missing, times out,
fails, emits malformed or oversized output, mixes session IDs, or cannot supply required
evidence also produces `unknown`, never pass.

External-adapter mode starts the adapter as an argument vector without a shell. The
adapter receives one JSON request on standard input containing protocol version 1, the
staged skill path, the case and rubric, the staged input paths, and the iteration number.
It runs with the temporary workspace as its current directory, so use a command available
on `PATH` and absolute paths for adapter files.

Treat the adapter as a target-specific trust boundary. It must start a fresh target
session, keep assertions and expected activation away from the evaluated agent, run the
task, grade only afterward, and return exactly one JSON object. Every response includes
`protocol_version`, matching `case_id`, non-empty `session_id`, and
`fresh_session: true`. Functional responses return every assertion as `id`, `status`
(`pass`, `fail`, or `unknown`), and non-empty `evidence`; trigger responses return
boolean `activated` and non-empty activation `evidence`. Missing assertions, malformed
output, adapter failure, timeout, or a reused or unattested session becomes `unknown`,
never pass.

The helper exits 0 only when every repeated case passes, 1 when any case fails or is
unknown, and 2 when the package, manifest, or command contract is invalid. Its temporary
working directory is contamination control, not authority to use credentials, quota,
paid tokens, networks, or real external side effects. Built-in mode adds the target's
native filesystem and tool restrictions where supported, but the target process still
needs its own authentication. Keep live target calls and effects on the authorization
path from Step 8; when a verified mode is unavailable, run the same cases manually or
through an external adapter and leave the gate `unknown` until evidence exists.

## Evaluation Tuning Loop

Use this loop after a suite is admitted and a case is non-green or flaky. Its purpose is
to locate the responsible contract and improve general behavior, not to make the score
green by weakening the case.

1. **Freeze the comparison.** Lock one case ID, prompt, files, assertions, target,
   model, configuration, and no-skill or previous-version baseline. A changed case
   starts a new baseline; do not compare its result with scores from the old prompt,
   fixture, or rubric.
2. **Run the smallest observable slice.** Run the deterministic contract first, then
   one affected case once in a fresh session. When the runner or adapter changed, prove
   its public seam with a fake target before spending a live call. Preserve artifacts
   only through an explicitly authorized new directory. Set phase bounds from observed
   timing and progress; a diagnostic timeout is not an acceptance threshold.
3. **Classify before editing.** Classify the result as skill behavior, eval design,
   runner or adapter, or provider or environment. A valid case exposing wrong task
   behavior belongs to the skill. An ambiguous prompt, missing input, unrealistic
   context, or assertion that cannot be decided from supplied evidence belongs to eval
   design. Process cleanup, timeout accounting, event parsing, grading transport, or
   sandbox enforcement belongs to the runner or adapter. Authentication, service
   latency, missing target evidence, or an unavailable platform capability belongs to
   the provider or environment.
   Record the last two classes as `unknown`: unknown is not a skill failure.
4. **Test one hypothesis.** State one explicit hypothesis and change exactly one owner
   per iteration: the skill, the case or rubric, the runner or adapter, or the selected
   target configuration. Do not edit skill instructions and the case that judges them
   in the same iteration. A retry without a new hypothesis or new evidence is not an
   evaluation step.
5. **Prove locally, then widen.** Rerun the same case in a fresh session. After it
   demonstrates the intended change, run the closest affected positive, negative, and
   edge cases. Trigger cases use realistic files and competing skills; tune wording only
   from the fixed training split, then judge it on the untouched validation split.
   Repeat a flaky case and report its rate rather than selecting the favorable run.
6. **Accept one exact result.** Freeze the final tree, rerun the full owned suite on
   every claimed model and surface, and perform independent acceptance only after that
   freeze. Do not combine passes from different intermediate trees. Report the exact
   tree, target configuration, case and repeat counts, `pass`/`fail`/`unknown`, timing,
   cost when known, and every unrun gate.

**Done when:** the failure class and owner are evidenced, each retry tests one explicit
hypothesis, the same case and its affected neighbors demonstrate the result, and the
complete acceptance ledger belongs to one frozen final tree.

## Testing Methodology

The portable specification supplies no built-in evaluation runner. The official Agent
Skills guide on [evaluating output
quality](https://agentskills.io/skill-creation/evaluating-skills) supplies the iteration
method; the package-local contract above makes the parts Skill Composer currently owns
repeatable. Keep evals opt-in under Step 8, keep a manual target-host path for every
skill, and test every deployed model and surface that the release claims.

Local package and eval-contract suites are necessary, not sufficient evidence of target
behavior. Before release, keep this behavior ledger for each claimed harness, surface,
and model:

| Workflow or gate | Required evidence |
|---|---|
| Create | Fresh-context activation and a functional creation scenario |
| Update | A regression scenario that changes the requested branch and preserves unrelated behavior |
| Review | A fresh read-only full-package review that does not mutate the target |
| Package/release | The exact artifact passes a clean installation and exercises every supported workflow branch |
| Trigger boundary | Intended trigger, paraphrase, realistic near-miss, and ambiguity cases when model invocation is claimed |
| Portability | The portable fallback completes without each host-only enhancement |
| Composition | Isolation and coexistence cases pass alongside likely overlapping skills |

Record every unavailable or unrun validator, target, surface, model, or behavior case as
`unknown`; it does not support the corresponding release claim.

### 1. Design Cases and Lock a Baseline

Start with 2-3 realistic cases tied to observed gaps. Vary phrasing and detail, include
an edge or ambiguous case, and name the expected output in human-readable terms before
writing narrow pass/fail checks. Run each representative task once without the skill;
when improving an existing skill, snapshot and run the previous skill version instead.
Use the same prompt, files, output boundary, target, and model for both configurations.
The bundled runner represents these comparisons as explicit baseline cases; it does not
automatically create the paired run or old-skill snapshot.

After a pilot run reveals what is objectively checkable, write assertions that are
specific and observable without requiring exact incidental wording. Once admitted to
this runner, every functional case must carry at least one assertion.

### 2. Run Fresh, Isolated Iterations

Give every run a clean workspace and session. Keep candidate assertions and expected
trigger labels hidden until grading, and save each new round under a new iteration
rather than overwriting earlier evidence. Run the same cases after each instruction
change so the comparison measures the skill rather than leftover conversation or files.

### 3. Grade with Concrete Evidence

Use deterministic scripts for mechanical facts such as JSON validity, file existence,
counts, hashes, or dimensions. Use an independent model grader for semantic assertions,
and require every pass, fail, or unknown verdict to cite concrete output or execution
evidence. Review assertion quality too: an assertion that always passes both baseline
and skill, always fails both, or cannot be decided from the supplied evidence needs to
be removed or repaired.

For holistic qualities that resist binary assertions, add a blind comparison: show the
two outputs without revealing which came from the skill and score both on the same
rubric. Blind comparison complements assertion grading; it does not replace mechanical
checks.

### 4. Capture Cost, Aggregate, and Inspect Outliers

Record duration, tokens, and cost where the target supplies them, but compare efficiency
only after correctness. With repeated runs, aggregate pass rate, time, and tokens for
each configuration and their delta in `benchmark.json`; standard deviation is meaningful
only with multiple observations. Inspect the full execution transcript for slow, costly,
flaky, or surprising cases instead of diagnosing from the final answer alone.

The bundled runner currently records per-phase transcript and timing artifacts and
aggregates trigger rates. It does not yet generate `benchmark.json`, blind comparisons,
or human feedback artifacts; perform those steps manually or with a separately verified
orchestrator and keep them out of automated claims until evidence exists.

### 5. Test Trigger Boundaries without Overfitting

For model-invoked skills, test whether the host loads the skill at the right boundary. Negative cases must be realistic near-misses, not unrelated topics that test nothing.

```
Should trigger:
- "Initialize a ProjectHub workspace for Q4 planning"

Realistic near-miss:
- "Summarize the existing ProjectHub workspace" (when the skill only creates workspaces)

Ambiguous boundary:
- "Help me organize Q4 in ProjectHub"
```

State the expected activation or clarification behavior before running each case. Include paraphrases for every real branch.

For focused description tuning, aim for about 20 balanced trigger/non-trigger queries and
run each multiple times; three runs and a 0.5 threshold are reasonable starting points.
Use a fixed train/validation split with proportional positive and negative cases. Change
the description only from train failures, select the best iteration by validation
performance, then sanity-check it with fresh queries that influenced neither set. Avoid
copying failed-query keywords into the description; repair the general intent boundary.

### 6. Test Isolation, Coexistence, and Functional Branches

Run the skill alone, then alongside the skills most likely to overlap. Verify the new skill does not steal unrelated triggers, suppress another skill, or depend on another installed skill unless that dependency is explicit. For a cross-agent skill, disable host enhancements and verify the portable fallback preserves the core result.

Build a **branch-to-case coverage table** for the admitted scope. Treat normal, edge,
stop, failure, and unknown-handling paths affected by the change as real branches, and
map each one to at least one functional case before the suite is complete. Case totals
and one happy path do not prove coverage of distinct branches.

Exercise every admitted normal, edge, stop, failure, and unknown-handling branch. Test
tool and API errors, side-effect boundaries, output contracts, user corrections, and the
portable fallback. For enterprise release, include 3-5 representative trigger,
non-trigger, and ambiguous queries in addition to the functional branch coverage.

### 7. Review with a Human and Iterate

Review actual outputs alongside assertion grades. Record specific human feedback per
case; an empty feedback value means no issue was found, while comments such as “the
months are sorted alphabetically instead of chronologically” are actionable. Combine
failed assertions, human feedback, and transcript evidence to make the smallest general
instruction or script change. Rerun all cases into the next iteration, grade, aggregate,
and repeat until feedback is consistently empty or improvement is no longer meaningful.

Useful iteration signals include:

**Undertriggering** (skill doesn't load when it should):
- Users manually enabling it
- Support questions about when to use it
- Fix: Identify the missing usage branch and add or sharpen one discriminating pointer using observed user language

**Overtriggering** (skill loads for unrelated queries):
- Users disabling it
- Confusion about purpose
- Fix: Narrow the positive context pointer and test the nearest competing branch; use an explicit prohibition only when a positive boundary cannot express the rule

#### Execution Issues

Symptoms: inconsistent results, API call failures, user corrections needed.
- Workflows produce different outputs for the same input
- MCP tool calls fail intermittently
- Users need to manually correct or retry

Fix the underlying missing decision, ambiguous instruction, or unstable mechanic. Bundle
repeated deterministic work into a tested script when transcripts show every run
recreating it; remove instructions that add cost without improving outcomes.
