# Changelog

This file records Skill Composer releases so the history travels with standalone distributions that do not include the source repository's Git history.

## [Unreleased]

### Align evaluation iteration with the official method

- **Changed:** Expanded the testing methodology around realistic 2-3-case pilots, same-prompt no-skill or previous-version baselines, fresh isolated workspaces, objectively checkable assertions, evidence-bearing grading, per-phase time/token/cost capture, repeated-run aggregation, transcript outlier analysis, blind comparison, human feedback, and trigger train/validation splits. The documentation distinguishes the runner's implemented case evidence and trigger aggregation from `benchmark.json`, blind comparison, human-feedback, and train/validation orchestration that still require a manual or separately verified path.
- **Why:** The official Agent Skills evaluation guide treats evals as an iteration loop rather than a collection of prompt files. Without the baseline, evidence, cost, aggregation, transcript, and human-review stages, a passing assertion set cannot show whether a skill improved over default behavior, generalized beyond tuned prompts, or merely spent more time reaching the same result.

### Keep migration claims on the public contract

- **Changed:** A changelog `Migration` now requires evidence that a supported public invocation, input, output, installation, or configuration contract changed. Replacing an internal implementation behind an unchanged public seam has no migration entry, and an unevidenced private wrapper does not become a supported compatibility promise.
- **Why:** A live Grok update eval preserved a fixture skill's documented `scripts/run.sh PROJECT` entry point but invented migration advice for hypothetical callers wrapping a removed internal `claude --print` detail. That advice would turn speculation into durable release history and make users act when the supported contract had not changed.

### Keep packaged evals opt-in

- **Changed:** Packaged eval manifests, fixtures, and runner copies are added only when the user requests eval work. An existing suite remains part of its skill's package contract and gains or revises cases only for behavior or real risks affected by the change. A skill without evals uses proportionate validators and manual behavior checks; when repeatable evals would materially address an activation, regression, side-effect, or release risk, Skill Composer recommends the smallest useful suite and asks before creating it.
- **Why:** The user clarified that not every skill needs packaged evals. Creating them by default would add maintenance work without consent, while ignoring an existing suite could let established regression coverage drift after a skill change.

### Make live evaluation verdicts complete and bounded

- **Changed:** Made one validation ledger the status owner for every applicable package, test, behavior, fallback, and clean-install gate, with every row reported as `pass`, `fail`, or `unknown`. The ledger is derived from the locked package inventory so every discovered test entry point and executable remains accounted for even when replaced or removed, while a branch-to-case table maps normal, edge, stop, failure, and unknown-handling paths to functional regressions. The eval runner gives candidate and grader independent 900-second default phase bounds; requires graders to finish inspecting and return exactly the listed assertion count and order; accepts Grok grading only from a completed streaming `end_turn`; emits safe periodic structural observations; and can preserve an explicitly requested sanitized workspace plus candidate/grader event, stderr, timing, token, and cost evidence without overwriting user data. Repeated trigger cases now produce strict-majority rates. Grok trigger activation is attributable through its initialization catalog and exact staged `SKILL.md` read, and its fail-closed custom sandbox denies ambient skill roots and original source packages while collapsing redundant nested denials. The candidate boundary hides this outer suite's rubric but treats the task package's own existing evals as legitimate inputs.
- **Why:** Authorized live Codex runs produced otherwise-correct artifacts but omitted unavailable behavior, bundled-test, or clean-install gates; later runs encoded an untested stop branch and removed an executable without retaining its baseline status. Live Grok runs exceeded the former deadline, left descendants behind, returned progress-shaped or partial grader output, hid a final response in a terminal assistant event, held pipes open after timeout, and provided no intermediate evidence while slow. Subsequent coexistence runs exposed two further infrastructure faults: redundant parent-and-child sandbox denials prevented `bwrap` from starting, and an ambiguous anti-rubric prompt caused the candidate to skip the target package's own eval contract. Independent phase bounds, attributable events, bounded process cleanup, opt-in raw evidence, fail-closed staging, and a precise evaluation boundary make those failures diagnosable without converting them into behavior verdicts.

### Make skill evaluations executable

- **Changed:** Added a shared standard-library eval helper with separate `check` and `run` contracts. It validates non-empty package-local functional and trigger manifests, rejects schema drift, symlinks, unsafe side-effect declarations, and escaping fixtures, stages an eval-free skill snapshot per case, and supports repeatable affected-case selection. `run` now offers built-in Claude, Codex, and Grok execution as well as the external JSON-adapter seam: functional cases keep the rubric away from the candidate and grade afterward in a second fresh session, while activation passes only on attributable target events. The runner has one repository owner, sibling skills own only their eval cases, and a standalone distribution vendors a pinned runner only with its black-box tests and provenance. Skill Composer dogfoods the contract with four functional scenarios spanning create, update, review, and package workflows plus twenty balanced trigger-boundary queries.
- **Why:** The user observed that evaluation guidance and case files alone do not ensure tests run after a skill changes, then asked for one reusable facility that can exercise Claude, Codex, and Grok without copying an independently drifting runner into every skill. A structural validator alone could turn a green schema check into a false behavior claim, while model self-grading or inferred activation could leak expected answers and manufacture passes. The split contract makes deterministic validation available after every edit and fresh target behavior repeatable; unavailable sandboxes, missing skills, malformed output, reused sessions, unobservable activation, and uncontrolled isolation remain `unknown`.

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
