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

## Before Writing a Case

Make one case answer one question at one layer. A trigger case asks only whether the
target activates the skill; once Claude emits the matching `Skill` call or Grok reads
the staged `SKILL.md`, the runner has the required positive observation and terminates
that candidate instead of letting it complete the functional task. A functional case
starts from a valid, installable package and tests the requested behavior; do not
manufacture a red result by breaking its launcher, wrapper, or package shape unless
that breakage is itself the behavior under test.

Give every negative trigger query a more plausible owner than the evaluated skill.
Words such as “this skill,” “this project,” or “the script” are a deictic owner, not
realistic context. Supply a referenced fixture or competing skill that those words can
identify; the runner rejects a negative deictic owner with neither. This structural
check cannot prove that an arbitrary fixture is semantically plausible, so fix the
fixture before tuning the description. If two description-only revisions leave the
same failure distribution, stop editing wording and reclassify the case or environment.

Assert observable evidence, not response shape or grader confidence. Valid JSON is
transport evidence, not completion evidence: a candidate or grader must perform the
tool work needed to establish its claim. Start with `check` and `list`, run one case
through `run-one`, inspect its report, and widen to `run-all` only after that smallest
slice behaves as intended.

## Repeatable Evaluation Contract

The admission decision lives in [Step 8](../SKILL.md#step-8-validate-behavior-and-maintain-admitted-evals).
Use the bundled standard-library helper as a package-local evaluation seam when the
target owns an admitted suite. A package without evals is valid when neither admission
condition applies:

```bash
python3 /path/to/skill-composer/scripts/eval-skill.py check /path/to/skill
python3 /path/to/skill-composer/scripts/eval-skill.py list /path/to/skill
python3 /path/to/skill-composer/scripts/eval-skill.py run-one \
  /path/to/skill CASE_ID [--repeat 3] [--model MODEL] \
  [--reasoning-effort EFFORT] --target claude|codex|grok
python3 /path/to/skill-composer/scripts/eval-skill.py inspect /path/to/report.json
python3 /path/to/skill-composer/scripts/eval-skill.py rerun /path/to/report.json
python3 /path/to/skill-composer/scripts/eval-skill.py run-all /path/to/skill \
  --additional-skill NAME=/path/to/skill --target TARGET
python3 /path/to/skill-composer/scripts/eval-skill.py run-all /path/to/skill \
  [--keep-going] [--repeat 3] -- ADAPTER [ARG ...]
```

Give the runner one repository owner and let each evaluated skill own only its manifests
and fixtures. Do not copy the helper into every sibling package. A standalone
self-validating distribution may vendor a pinned copy only when it cannot call a shared
repository owner; include the matching black-box test and record the Skill Composer
release or artifact hash that identifies the copy.

`check` validates the skill's package identity, rejects symlinks before staging, and
checks eval manifests, identifiers, safe side-effect declarations, assertions, fixture
paths, and ownerless deictic negative queries. `list` prints the validated functional
and trigger case IDs without starting a target. Neither command is the portable Agent
Skills schema validator or a target validator, and neither supplies activation or
functional evidence.

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
  cases. A negative query containing `this`, `that`, or `the` before `skill`, `project`,
  `script`, or `package` must also declare a fixture or competitor; authors still own
  whether that context gives the phrase a genuinely more plausible referent.
- Both documents use `schema_version: 1` and a `skill_name` matching `SKILL.md` and the
  package directory. Unknown fields fail closed so misspellings cannot silently weaken
  a gate. At least one case must exist across the two manifests; an empty package is
  not a valid eval contract.

Every execution validates first and copies the complete evaluated package into one
frozen package snapshot. The runner verifies that its content hash stayed stable while
copying, then creates a new temporary workspace for every case and iteration from that
snapshot. A source edit during a multi-case run therefore cannot mix package versions.
Each case workspace receives an eval-free skill copy and only its declared fixture
inputs.

`run-one` executes exactly one case and is the tuning and debugging entry point.
`run-all` runs the complete suite from the same snapshot and fails fast after the first
non-green case; pass `--keep-going` only when collecting all independent failures is
worth the additional calls. The older `run --case` surface remains compatible for
external callers, but new workflows use the explicit scopes so omission cannot turn a
focused probe into a full paid suite. An unknown or duplicate case ID is a
command-contract error. Built-in targets use these runner-owned defaults:

| Target | Model | Reasoning effort |
|---|---|---|
| Claude | `claude-sonnet-5` | `high` |
| Codex | `gpt-5.6-terra` | `high` |
| Grok | `grok-4.6` | `high` |

`--model` and `--reasoning-effort` override the selected target's defaults. The
runner's stable canonical CLI vocabulary is:

| Target | Canonical reasoning-effort values | Target surface |
|---|---|---|
| Claude | `low`, `medium`, `high`, `xhigh`, `max` | Claude's `--effort` flag |
| Codex | `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max`, `ultra` | Codex's `model_reasoning_effort` configuration |
| Grok | `none`, `minimal`, `low`, `medium`, `high`, `xhigh`, `max` | Grok's `--reasoning-effort` flag |

These values describe harness input vocabulary, not a claim that every model accepts
every value. A target may advertise a model-specific subset or additional menu IDs;
the runner keeps its public override contract to the canonical names above, and the
selected target runtime owns model compatibility. The runner rejects canonical values
outside the selected target's set and rejects either override without a built-in target
before a provider call. It passes the resolved model and effort explicitly to both the
candidate and independent grader instead of relying on ambient target configuration.
Whether a particular model supports the selected value remains target-runtime evidence.
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

`run-one` and `run-all` automatically write a mode-`0600` sanitized report and print its
path. Pass `--report NEW_FILE` to choose another new path. The report records the frozen
package hash, resolved target/model/effort, exact scope, case and iteration statuses,
reason codes, structural phase summaries, timing, and provider metrics. It does not
store prompts, rubrics, assertion evidence, model text, tool arguments, session IDs, or
raw stderr. Use the `inspect` command on `REPORT` to classify the failed phase before
increasing a timeout. Use the `rerun` command only to reproduce the same built-in target
configuration; it refuses to run when the source package hash has drifted, and emits a
new report instead of overwriting the old one. The hash covers paths, content, and
executable bits; other permission bits do not change package identity.
External-adapter reports remain
inspectable but are not rerunnable because persisting an arbitrary adapter command could
persist secrets.

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

- **Claude:** a matching structured `Skill` call proves activation, and the runner stops
  the candidate as soon as that call appears. A negative result requires the
  initialization catalog to prove the skill was offered and a completed turn—the
  terminal result event—without the matching call. The runner never judges
  non-activation from an intermediate assistant event, because the model may read or
  search first and invoke the skill on a later turn. The session loads only
  project-scoped settings, skills, and commands, so the staged copy is the only one the
  catalog can advertise or the `Skill` call can name; the [harness
  ledger](../HARNESS-RESEARCH.md#current-eval-target-evidence) records that evidence.
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
  `read_file` call for its staged `SKILL.md` proves positive activation and stops the
  candidate. For a negative case, the same catalog plus a completed `end_turn` turn
  without that matching read proves non-activation; an intermediate tool call is not a
  verdict. Completed `end_turn` responses provide functional text. This controlled
  workspace also supports Grok baseline and isolation cases; if the profile is
  unavailable or does not start fail closed, the result is `unknown`.

The built-in Codex command cannot prove that ambient user skills were absent, so Codex
baseline and isolation categories remain `unknown`. Use an external adapter in a clean
host when those claims matter. A built-in target executable that is missing, times out,
fails, emits malformed output or more than 32 MiB of output in one phase, mixes session
IDs, or cannot supply required evidence also produces `unknown`, never pass.

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
   fixture, or rubric. The runner freezes one package snapshot and records its hash;
   retain that report as the identity of the observed run.
2. **Run the smallest observable slice.** Run `check` and `list`, then invoke `run-one`
   for one affected case once in a fresh session. When the runner or adapter changed,
   prove its public seam with a fake target before spending a live call. A parser,
   grader-transport, or completion change also needs one authorized real probe showing
   that the model performed the required tool work; valid JSON alone is insufficient.
   Preserve raw artifacts only through an explicitly authorized new directory. Set
   phase bounds from observed timing and progress; a diagnostic timeout is not an
   acceptance threshold.
3. **Classify before editing.** Classify the result as skill behavior, eval design,
   runner or adapter, or provider or environment. A valid case exposing wrong task
   behavior belongs to the skill. An ambiguous prompt, missing input, unrealistic
   context, or assertion that cannot be decided from supplied evidence belongs to eval
   design. Process cleanup, timeout accounting, event parsing, grading transport, or
   sandbox enforcement belongs to the runner or adapter. Authentication, service
   latency, missing target evidence, or an unavailable platform capability belongs to
   the provider or environment. Start with `inspect REPORT`; for `unknown`, locate the
   candidate, grader, protocol, or environment phase before increasing a timeout.
   Record the last two classes as `unknown`: unknown is not a skill failure.
4. **Test one hypothesis.** State one explicit hypothesis and change exactly one owner
   per iteration: the skill, the case or rubric, the runner or adapter, or the selected
   target configuration. Do not edit skill instructions and the case that judges them
   in the same iteration. A retry without a new hypothesis or new evidence is not an
   evaluation step.
5. **Prove locally, then widen.** Rerun the same case in a fresh session with the same
   explicit configuration. Use `rerun REPORT` only when reproducing the unchanged
   package; after an intended edit, issue the same `run-one` scope and let it record the
   new hash. After the case demonstrates the intended change, run the closest affected
   positive, negative, and edge cases. Trigger cases use realistic files and competing
   skills; tune wording only from the fixed training split, then judge it on the
   untouched validation split. Repeat a flaky case and report its rate rather than
   selecting the favorable run.
6. **Accept one exact result.** Freeze the final tree, use `run-all` for the full owned
   suite on every claimed model and surface, and perform independent acceptance only
   after that freeze. The default fail-fast pass is the shortest acceptance probe;
   `--keep-going` is an explicit diagnostic choice. Do not combine passes from different
   intermediate trees. Report the exact tree, target configuration, case and repeat
   counts, `pass`/`fail`/`unknown`, timing, cost when known, and every unrun gate.

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

The runner gives every iteration a clean workspace and session while all cases in one
command share the same frozen source snapshot. Keep candidate assertions and expected
trigger labels hidden until grading, and save each new round under a new report rather
than overwriting earlier evidence. Run the same cases after each instruction change so
the comparison measures the skill rather than leftover conversation or files.

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

The bundled runner automatically records sanitized per-phase timing, metrics, and
structural summaries, can explicitly retain sensitive transcripts and workspace
artifacts, and aggregates trigger rates. It does not yet generate `benchmark.json`,
blind comparisons, or human feedback artifacts; perform those steps manually or with a
separately verified orchestrator and keep them out of automated claims until evidence
exists.

### 5. Test Trigger Boundaries without Overfitting

For model-invoked skills, test whether the host loads the skill at the right boundary.
Negative cases must be realistic near-misses, not unrelated topics that test nothing.
If a negative uses a deictic owner such as “this skill,” “this project,” or “the
script,” its fixture or competing skill must be a more plausible referent than the
evaluated skill; otherwise repair the case before editing the description.

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
