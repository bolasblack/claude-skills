# Changelog

This file records Skill Composer releases so the history travels with standalone distributions that do not include the source repository's Git history.

## [Unreleased]

### Keep release history on the published baseline

- **Changed:** Changelog authoring now establishes the last artifact actually published to its audience and records `Unreleased` as the net delta from that artifact. Pre-release revisions fold into the candidate's resulting contract, and a first release describes its resulting capability instead of transitions from unpublished drafts. The existing cross-harness release eval now locks this baseline behavior.
- **Why:** An unreleased skill draft briefly required a local tool before the first release finalized that tool as optional. Recording the draft-to-final correction as release history would tell users that a published requirement changed even though no artifact they received ever imposed it.

### Make focused eval debugging runner-owned

- **Changed:** Added explicit `list`, `run-one`, and fail-fast `run-all` scopes to the shared evaluator, with `--keep-going` as an opt-in diagnostic mode. Every command now evaluates one content-hashed package snapshot whose identity covers paths, content, and executable bits but not other permission bits; trigger probes stop as soon as Claude or Grok supplies an attributable positive activation and judge non-activation only on a completed turn; and ownerless deictic negative queries fail contract validation. Focused and full runs automatically emit a mode-`0600` sanitized phase report; `inspect` summarizes it, while `rerun` reproduces the recorded built-in configuration only when the source and explicit additional-skill hashes still match. Black-box coverage locks single-case execution, fail-fast behavior, snapshot stability under a concurrent source edit, report redaction and validation, drift refusal, permission-bit tolerance, positive early termination, and a candidate that explores before invoking the skill on a later turn.
- **Why:** Writing “run one case,” “freeze the tree,” or “inspect before increasing the timeout” in agent instructions left the most useful debugging behavior dependent on the evaluator remembering and following prose. Earlier live tuning spent long calls completing work after trigger activation, mixed protocol symptoms with skill failures, and exposed how an ownerless “this skill” negative measures an empty exam room rather than the description boundary. A first assistant event is not a verdict either: a model that reads or searches before invoking the skill on a later turn would fail every positive probe and pass every negative one, so the absence of the call counts only once the turn has ended. Permission bits follow the checkout umask rather than the package, so hashing them made identical content refuse to rerun. Moving deterministic scope, identity, observability, and stop behavior behind the public CLI makes the shortest diagnostic path the default and leaves the document responsible only for case-design judgment that code cannot establish.
- **Migration:** Existing negative trigger cases that use `this`, `that`, or `the` before `skill`, `project`, `script`, or `package` must add a referenced fixture or competing skill, or replace the deictic phrase with an explicit owner. Existing `run` invocations remain supported; adopt `run-one` and `run-all` when the caller should make focused versus complete scope explicit.

### Keep target claims inside their evidence boundary

- **Changed:** Applied the validation ledger to package frontmatter, body text, changelog, and final reporting: a named target may be called verified, supported, or tested only when its matching target-behavior row passes. Static schema checks, manual walkthroughs, portable-by-construction design, and evidence from another target require narrower wording and leave unrun targets unknown.
- **Why:** A Claude Sonnet 5 high creation eval correctly marked Codex and Claude Code invocation as unknown in its final ledger, but the generated skill simultaneously claimed both were verified in frontmatter. A truthful report cannot compensate for an unsupported compatibility claim shipped inside the artifact itself.

### Keep read-only findings decision-complete

- **Changed:** Defined each review finding as one complete record containing severity, file and line evidence, impact, the smallest adequate fix, and an objective completion criterion. A request for only findings and evidence narrows narration and forbids mutation; it does not remove the fix proposal or its acceptance criterion.
- **Why:** In a Claude Sonnet 5 high read-only review eval, the agent found and reproduced the target contract violation but interpreted "only findings and evidence" as a reason to omit the smallest fix and completion criterion. The review therefore had evidence but was not actionable or objectively closable.

### Give every built-in eval target reproducible defaults

- **Changed:** Added runner-owned default model and reasoning-effort pairs for Claude (`claude-sonnet-5`, `high`), Codex (`gpt-5.6-terra`, `high`), and Grok (`grok-4.6`, `high`). The public override now recognizes each current harness's stable canonical CLI vocabulary: five values for Claude, eight for Codex, and seven for Grok. Every resolved model and effort is passed to both candidate and grader sessions. Black-box tests lock the defaults, all three complete canonical transports, explicit overrides, incompatible-value rejection, and CLI help.
- **Why:** Claude and Codex previously left omitted choices to target behavior while Grok silently forced `low`, so otherwise identical eval commands did not own a comparable or reproducible model configuration. Fresh harness research also showed that API effort enums, harness-level canonical input, and a model's advertised menu are different contracts. One target configuration owner now makes the implicit case explicit without treating one of those contracts as another.
- **Migration:** A built-in run that intentionally relied on target-local model or effort selection must pass `--model` and `--reasoning-effort` explicitly; omitted values now use the runner-owned pairs above.

### Keep shared eval validation on its public seam

- **Changed:** Distinguished the shared eval runner's documented public CLI from its maintainer-only implementation and from Skill Composer's own manifests, fixtures, and package tests. The update router now opens the Evaluation Reference before target edits only when inventory finds `evals/evals.json` or `evals/trigger-eval.json`, or the user explicitly requests eval work; other update branches keep it closed and neither search nor invoke the reference or runner as a generic schema validator. An admitted branch invokes the validator from the installed Skill Composer package instead of searching the target for a runner copy. Package-contract regressions lock the public boundary, observable admission inputs, disclosure location, and runner ownership.
- **Why:** A Claude Sonnet 5 high update eval read the evaluation reference and found the shared runner, but the always-loaded introduction classified the entire runner as maintainer evidence and told the agent not to use it. After that ownership conflict was removed, the same live case listed the reference without reading it and searched only the target package for a copied runner; moving a direct reference link into the introduction fixed that case but then caused a no-eval update to open branch-only guidance merely while looking for validators. A later no-suite run still treated `eval-skill.py check` as a possible package validator and loaded the reference to learn its CLI. The final inventory-driven router satisfies both sides of Step 8: admitted suites reach `eval-skill.py check`, while absent and unrequested suites use their actual package and target validators without spending context on eval infrastructure.

### Keep Claude live evals strict under root

- **Changed:** Pass an empty MCP set to Claude with its current `{"mcpServers":{}}` configuration shape. On Linux root runs, launch only a writable Claude candidate through a `bwrap` user-namespace identity translation so Claude starts as non-root while its own fail-closed filesystem, network, and Unix-socket sandbox remains enabled. Black-box tests lock both the MCP shape and the candidate/grader identity boundary.
- **Why:** A Sonnet 5 live eval first stopped before inference because `{}` no longer satisfied Claude's MCP schema, then reached the candidate but every Bash call failed in Claude Code's root-only nested UID-mapping path. Disabling the sandbox, allowing all Unix sockets, or accepting manual reasoning as red-green evidence would have hidden the failure by weakening the eval contract.

### Make live eval effort explicit

- **Changed:** Added a target-aware `--reasoning-effort` runner option and pass its validated value to both the candidate and independent grader through Claude's `--effort` flag or Codex's `model_reasoning_effort` configuration. Black-box coverage observes all four target invocations and rejects target-incompatible values or unsupported targets before a provider call.
- **Why:** A model override alone could not prove that an authorized live run used the requested reasoning effort, especially while the runner isolated or ignored ambient user configuration. One public option now makes Claude and Codex eval configurations reproducible without mutating either target's global settings.

### Disclose evaluation guidance only for admitted suites

- **Changed:** Consolidated eval manifests, shared-runner behavior, target evidence limits, observability, acceptance gates, tuning, and testing methodology in `references/evaluation.md`. Step 8 retains the opt-in admission decision, universal validation ledger, live-effect authorization boundary, and one conditional pointer; the README now provides only the local validation quick start and that pointer. The evaluation reference explicitly attributes the portions of its case-design and iteration method adapted from the official Agent Skills evaluation guide.
- **Why:** Eval maintenance is a real but infrequent branch. Keeping its full runner and methodology contract in the always-loaded authoring reference and repeating operational details in the README spent context on skills without evals and created multiple places where the same behavior could drift.

### Align evaluation iteration with the official method

- **Changed:** Expanded the testing methodology around realistic 2-3-case pilots, same-prompt no-skill or previous-version baselines, fresh isolated workspaces, objectively checkable assertions, evidence-bearing grading, per-phase time/token/cost capture, repeated-run aggregation, transcript outlier analysis, blind comparison, human feedback, and trigger train/validation splits. A diagnostic tuning loop now freezes one case, classifies each non-green result as skill behavior, eval design, runner/adapter, or provider/environment, changes one responsible owner per iteration, reruns the same case before neighboring regressions, and accepts only a full-suite result from one frozen final tree. The documentation distinguishes the runner's implemented case evidence and trigger aggregation from `benchmark.json`, blind comparison, human-feedback, and train/validation orchestration that still require a manual or separately verified path.
- **Why:** The official Agent Skills evaluation guide treats evals as an iteration loop rather than a collection of prompt files. Live evaluation also showed that skill defects, ambiguous fixtures, runner lifecycle or protocol faults, and target limitations can surface as the same non-green verdict; changing several owners or combining passes from intermediate trees would hide causality. Without the baseline, owner classification, single-hypothesis retry, evidence, cost, aggregation, transcript, final-tree rerun, and human-review stages, a passing assertion set cannot show whether a skill improved over default behavior, generalized beyond tuned prompts, or merely spent more time reaching the same result.

### Keep migration claims on the public contract

- **Changed:** A changelog `Migration` now requires evidence that a supported public invocation, input, output, installation, or configuration contract changed. Replacing an internal implementation behind an unchanged public seam has no migration entry, and an unevidenced private wrapper does not become a supported compatibility promise.
- **Why:** A live Grok update eval preserved a fixture skill's documented `scripts/run.sh PROJECT` entry point but invented migration advice for hypothetical callers wrapping a removed internal `claude --print` detail. That advice would turn speculation into durable release history and make users act when the supported contract had not changed.

### Keep packaged evals opt-in

- **Changed:** Packaged eval manifests, fixtures, and runner copies are added only when the user requests eval work. An existing suite remains part of its skill's package contract and gains or revises cases only for behavior or real risks affected by the change. A skill without evals uses proportionate validators and manual behavior checks; when repeatable evals would materially address an activation, regression, side-effect, or release risk, Skill Composer recommends the smallest useful suite and asks before creating it.
- **Why:** The user clarified that not every skill needs packaged evals. Creating them by default would add maintenance work without consent, while ignoring an existing suite could let established regression coverage drift after a skill change.

### Make live evaluation verdicts complete and bounded

- **Changed:** Made one validation ledger the status owner for every applicable package, test, behavior, fallback, and clean-install gate, with every row reported as `pass`, `fail`, or `unknown`. The ledger is derived from the locked package inventory so every discovered test entry point and executable remains accounted for even when replaced or removed, while a branch-to-case table maps normal, edge, stop, failure, and unknown-handling paths to functional regressions. The eval runner gives candidate and grader independent 900-second default phase bounds; requires graders to finish inspecting and return exactly the listed assertion count and order; accepts Grok grading only from a completed streaming `end_turn`; emits safe periodic structural observations; and can preserve an explicitly requested sanitized workspace plus candidate/grader event, stderr, timing, token, and cost evidence without overwriting user data. Repeated trigger cases now produce strict-majority rates. Grok trigger activation is attributable through its initialization catalog and exact staged `SKILL.md` read, and its fail-closed custom sandbox denies ambient skill roots and original source packages while collapsing redundant nested denials. The candidate boundary hides this outer suite's rubric but treats the task package's own existing evals as legitimate inputs. The per-phase output bound is 32 MiB because verbose event streams embed every tool result, and the grader's workspace snapshot no longer hides a top-level directory that merely shares the evaluated skill's name.
- **Why:** Authorized live Codex runs produced otherwise-correct artifacts but omitted unavailable behavior, bundled-test, or clean-install gates; later runs encoded an untested stop branch and removed an executable without retaining its baseline status. Live Grok runs exceeded the former deadline, left descendants behind, returned progress-shaped or partial grader output, hid a final response in a terminal assistant event, held pipes open after timeout, and provided no intermediate evidence while slow. Subsequent coexistence runs exposed two further infrastructure faults: redundant parent-and-child sandbox denials prevented `bwrap` from starting, and an ambiguous anti-rubric prompt caused the candidate to skip the target package's own eval contract. Independent phase bounds, attributable events, bounded process cleanup, opt-in raw evidence, fail-closed staging, and a precise evaluation boundary make those failures diagnosable without converting them into behavior verdicts. A bound sized for protocol chatter rather than embedded tool results would turn a long but legitimate session into `unknown` after its cost was spent, and a name-based exclusion could hide exactly the artifact a creation case asks for.

### Make skill evaluations executable

- **Changed:** Added a shared standard-library eval helper with separate `check` and `run` contracts. It validates non-empty package-local functional and trigger manifests, rejects schema drift, symlinks, unsafe side-effect declarations, and escaping fixtures, stages an eval-free skill snapshot per case, and supports repeatable affected-case selection. `run` now offers built-in Claude, Codex, and Grok execution as well as the external JSON-adapter seam: functional cases keep the rubric away from the candidate and grade afterward in a second fresh session, while activation passes only on attributable target events. The runner has one repository owner, sibling skills own only their eval cases, and a standalone distribution vendors a pinned runner only with its black-box tests and provenance. Claude sessions load only project-scoped settings, skills, and commands, so the staged copy is the only one a candidate can activate; the harness ledger records that evidence. Skill Composer dogfoods the contract with four functional scenarios spanning create, update, review, and package workflows, each assertion checking one behavior, plus twenty balanced trigger-boundary queries in which both labels stage realistic competing skills.
- **Why:** The user observed that evaluation guidance and case files alone do not ensure tests run after a skill changes, then asked for one reusable facility that can exercise Claude, Codex, and Grok without copying an independently drifting runner into every skill. A structural validator alone could turn a green schema check into a false behavior claim, while model self-grading or inferred activation could leak expected answers and manufacture passes. The split contract makes deterministic validation available after every edit and fresh target behavior repeatable; unavailable sandboxes, missing skills, malformed output, reused sessions, unobservable activation, and uncontrolled isolation remain `unknown`. Bundled multi-clause assertions hid which behavior regressed behind one verdict, and positive queries that never faced a competitor could not show the description winning a real boundary.

### Research harness facts on demand

- **Changed:** Added a conditional primary-source research SOP for target-specific authoring claims and a tested optional fetcher that captures one current Agent Skills, Codex, Claude Code, or Grok document as a temporary payload plus provenance. The fetcher permits only reviewed built-in HTTPS destinations without redirects; ignores ambient proxy and CA overrides; accepts an explicitly selected credential-free HTTP CONNECT proxy and CA bundle; classifies certificate verification as a trust failure; and requires a bounded, complete HTTP 200 UTF-8 Markdown response whose reviewed identity preamble and heading match line-for-line within a 30-second retrieval-phase deadline. It never overwrites caller-owned output, attempts to remove partial publication, and reports the exact residual path if cleanup also fails. The SOP remains executable with isolated read-only host retrieval when the script is unavailable, and unverifiable claims remain unknown.
- **Why:** The user wanted a repeatable way to consult the agent manuals without maintaining a static documentation cache. A persistent cache would become stale, while making the Python helper mandatory would exclude supported environments without Python. Review also found that ambient transport state was absent from provenance, a marker anywhere in the body could authenticate an unrelated login document, a per-socket timeout did not bound total retrieval time, TLS trust failures were reported as connectivity, and deletion itself could fail. The final contract keeps source authority and transport choices explicit, rejects incomplete responses and wrong-heading substitutions, preserves a portable fallback, and reports partial state without presenting cleanup as certain.

### Make mechanical work environment-native and tested

- **Changed:** Added a stable environment-native automation requirement and matching authoring guidance. Repeated deterministic mechanics should become scripts when that reduces variance or repeated work; executable behavior uses public-seam red-green TDD with the observed failing run preserved before implementation, while language and dependency choices minimize total installation, implementation, maintenance, and supply-chain cost in the supported environment.
- **Why:** The user first requested Python, TDD, and few external dependencies, then clarified that these are defaults rather than absolute constraints: a Ruby-project skill may be better served by Ruby, a Windows-only skill by PowerShell, and a runtime such as Bun may be proper when its built-in capabilities eliminate substantial custom machinery. A blanket language or zero-dependency rule would therefore increase complexity in the environments Skill Composer is supposed to support.

### Keep branch processes intact

- **Changed:** Clarified the proportionate-context requirement: discovery gives each invocation branch one discriminating trigger, `SKILL.md` keeps shared instructions and branch-critical process state in place, and only branch-only lookup material moves behind an explicit read condition when the context reduction justifies the added navigation.
- **Why:** The former wording could be read as requiring every branch-specific detail to move behind a pointer. During review, the user questioned whether that interpretation reinstated a previously rejected requirement and authorized clarifying the specification. Mandatory splitting would add navigation and hide process state without evidence that it reduces context cost.

### Route every declared authoring operation

- **Changed:** Added an explicit create, update, review, and package/release router. Updates lock the existing package contract and regression baseline before using the shared authoring steps; every authoring and release step now has a local observable completion criterion. Invocation now chooses automatic versus explicit entry by context load, cognitive load, and side-effect safety instead of treating dual host support as a third strategy. Evaluations use disposable fixtures by default and require explicit user authorization plus cleanup for real external effects.
- **Why:** The discovery description promised all four operations, but the runtime body explicitly routed only creation and review, and its own create/update and release steps violated its requirement that every step say how to finish. The former invocation labels did not decide when automatic loading was worth its context cost or safe, while live evaluation guidance could cause writes, messages, charges, or publication without an authorization boundary.

### Give each document one information owner

- **Changed:** Kept branch-critical runtime process in `SKILL.md`; made `REFERENCE.md` the sole owner of frontmatter, directory, workflow-pattern, changelog-format, and review-ledger lookup; and made each `SPEC.md` invariant own its enduring reason. Removed the duplicate admission ledger, frontmatter and directory copies, full pattern examples, and end-of-file quick checklist.
- **Why:** Review found several synchronized copies of the same rules in invoked and branch-only context. They increased every invocation's context cost and could drift, while a separate admission ledger left the normative specification unable to explain its own requirements.

### Carry standalone terms without inventing provenance

- **Changed:** Added the repository's existing `Personal use` notice as a package-local license file and frontmatter reference. The README now distinguishes recorded historical attribution from verified exact upstream provenance and does not claim an unestablished upstream license.
- **Why:** Skill Composer's changelog is designed to travel with standalone distributions, but the applicable repository notice previously stayed outside the artifact and the acknowledgment linked only to a profile. Copying the existing notice preserves the known distribution term; labeling the precise upstream artifact and rights as unknown avoids manufacturing legal provenance.

### Make cross-harness release claims testable

- **Changed:** Replaced cached target paths, UI flows, plugin layouts, and API or SDK behavior with a durable distribution decision map whose current facts come from the harness-research branch. Package tests now validate that ownership boundary, portable frontmatter, local anchors, workflow routes, removed-content residue, and the release ledger for activation, function, fallback, coexistence, and clean-install evidence.
- **Why:** The previous automated gate checked keywords and named platform sections, while the same fast-changing target facts also belonged to harness research. The user questioned why exact Codex skill paths were kept in `REFERENCE.md` when that research branch already supplies them. One research owner avoids stale duplicate guidance without weakening the decisions or behavior evidence required for a release.

### Remove stale pattern snapshots

- **Changed:** Removed all seven bundled historical example files, their indexes, and the derived snapshot guide.
- **Why:** Full-package review found dead source links, citations pinned to mutable branches, and no established redistribution-license evidence for the copied snapshots. The user chose deletion instead of carrying and continuously revalidating non-authoritative copies.

## [3.2.1] - 2026-08-14

### Preserve only user-owned maintenance invariants

- **Changed:** Reduced `SPEC.md` to the three requirement groups the user identified as non-negotiable: cross-harness behavior, a proportionate context footprint, and package-local maintenance context. Authoring authority, evidence policy, and the creation/review distinction remain operational Skill Composer rules rather than self-specification requirements.
- **Why:** The user requires generated skills to remain cross-harness, avoid consuming excessive agent context through oversized discovery text or `SKILL.md` bodies, and preserve the distinct purposes and reasons for `SPEC.md` and `CHANGELOG.md`. Promoting other current policies into the self-specification would turn implementation choices into permanent product constraints and duplicate rules already enforced by the skill itself.

### Keep maintenance artifacts conditional

- **Changed:** Skill Composer now treats `SPEC.md` as an exceptional optional file for explicit, stable requirements that constrain future rewrites but are unnecessary during ordinary execution. Creation and review apply a four-part admission test and require a conditional maintenance pointer. `CHANGELOG.md` remains independently conditional on a skill having releases of its own or independent distribution.
- **Why:** The user clarified that most skills, including principle-driven and workflow-routing skills, keep their enduring rules in the runtime `SKILL.md` and gain nothing from a separate specification. A routine `SPEC.md` would duplicate or hide required instructions; the rare separate file preserves maintainer-only constraints without loading them during normal runs. Release history addresses a different failure mode: its causal context can disappear when a skill leaves its repository or shares commits with other skills.

## [3.2.0] - 2026-08-14

### Make Skill Composer the authoring owner

- **Changed:** Front-loaded Skill Composer's ownership and helper-conflict trigger in its description. Harness-injected authoring helpers now act as platform adapters rather than replacing Composer's scope, packaging, release-history, or quality decisions.
- **Why:** The installed generic helper told authors not to include `CHANGELOG.md`, while this release explicitly required a portable, skill-local changelog. The user therefore required the helper to remain subordinate to Skill Composer rather than overwrite its packaging decisions.

### Make release history portable and causal

- **Changed:** Moved Skill Composer's history into a skill-local `CHANGELOG.md` and required each new logical change to record `Changed` and `Why`, with `Example` only when it adds material understanding and `Migration` only when downstream action is required. Changelog reviews now re-test every retained example, not only examples added by the current diff.
- **Why:** A repository commit may combine several skills, an installed skill may contain no Git metadata, and a what-only entry does not preserve the decision that future maintainers need to evaluate. Making `Example` mandatory would instead encourage redundant filler or unsupported reconstruction.

### Require evidence-backed release explanations

- **Changed:** Required every changelog claim to trace to an explicit user explanation in the current or a retrievable earlier conversation, a requirement or spec, observed diff or code, test or log output, or an existing release record. De-identification may transform supported details but may not add a missing cause.
- **Why:** A plausible explanation can turn an agent's guess into durable false history, while an earlier user conversation may contain the real reason even when the current request only names the change.

### Compose optionally with writing-for-agents

- **Changed:** Documented `writing-for-agents` as an optional editorial pass while Skill Composer retains ownership of skill mechanics, packaging, validation, and release records.
- **Why:** The user explicitly wanted Skill Composer to point authors to `writing-for-agents` for a stronger combined result. Inspection showed complementary coverage without changing which skill owns authoring and packaging policy.

### Add a full-package review workflow

- **Changed:** Added a separate, default-read-only workflow for reviewing an existing skill. It locks the review contract, inventories the entire package and its trust boundaries, reconstructs every usage branch, audits the agent-facing contract, validates real behavior, and reports evidence-backed findings with completion criteria.
- **Why:** Skill Composer's description claimed review support, but its body only provided a creation workflow, a mixed development checklist, and a changelog-specific review rule. That structure could validate the current diff while missing stale content elsewhere in the installed skill.

### Make cross-agent portability structural

- **Changed:** Split cross-agent skills into a portable core and optional harness enhancements. Host-only features such as hooks, dynamic context, subagent configuration, UI metadata, and permission conveniences now require a portable fallback unless the skill explicitly declares itself single-harness.
- **Why:** The user required skills to work across agents without forbidding useful Claude Code-only capabilities. Treating those capabilities as enhancements preserves cross-agent core behavior while still allowing a deliberately Claude Code-only skill to depend on them.

### Add a normative self-specification

- **Changed:** Added `SPEC.md` as the normative current-state contract for Skill Composer itself, with explicit document responsibilities and change-acceptance criteria. Normal skill-authoring tasks do not load it; modifying or reviewing Skill Composer does.
- **Why:** The user wanted high-level expectations such as cross-harness support to survive future rewrites without being scattered across runtime procedures or earlier conversations. A separate specification preserves those expectations without turning `SKILL.md` into a second maintenance history.

### Refresh current platform guidance

- **Changed:** Aligned size and name checks, `allowed-tools` semantics, invocation modes, evaluations, upload navigation, organization provisioning, Skills API versioning, Agent SDK behavior, and security review with current primary documentation. Target-specific rules are now labeled instead of presented as portable requirements.
- **Why:** Review against current sources found several old universal rules that were no longer accurate, including word-based size limits, a universal 10-20-query release gate, an arbitrary skill-count consolidation threshold, mandatory metadata versioning, unrelated negative tests, the former slash-command split, and obsolete UI paths. Those rules could reject valid cross-agent skills or falsely pass weak ones.

Versions before 3.2.0 were migrated from the former in-file history. Their entries preserve the facts recorded at the time; missing rationales and examples are not reconstructed.

## [3.1.0] - 2026-03-03

- Aligned the guide with Anthropic's Complete Guide to Building Skills PDF.

## [3.0.0] - 2026-03-02

- Rewrote the guide from Anthropic's official material and merged the existing community patterns and examples.
- The former `REFERENCE.md` history separately recorded its initial standalone reference document as v3.0.0 on 2026-03-03. The two legacy files therefore did not record one shared date, and this consolidation does not infer one.

## [2.0.0] - 2025-11-15

- Renamed `write-skills` to `skill-composer` and restructured its documentation.

## [1.0.0] - 2025-11-03

- Published the initial version.
