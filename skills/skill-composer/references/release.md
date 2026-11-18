# Packaging and Releasing a Skill

Branch-only workflow, reached from [Choose the Workflow](../SKILL.md#choose-the-workflow). Read this file in full before Release Step 1.

### Release Step 1: Lock the Release Contract

Record the exact skill, the proposed version in version mode, target harnesses and
surfaces, invocation policies, distribution forms, and files that belong in the artifact.

**Done when:** one release ledger names the exact skill, any proposed version, target harnesses and surfaces, invocation policies, distribution forms, artifact files, and every claimed gate before the artifact is built.

### Release Step 2: Build the Exact Artifact

Build from the skill directory only. Include every linked script, reference, asset,
dependency, license or attribution notice, and required release record; exclude
temporary research bundles, caches, secrets, and unrelated repository files.

**Done when:** an explicit artifact inventory contains every required file and no source-tree-only or temporary residue.

### Release Step 3: Validate Schema and Behavior

Run the package check from [Step 7](../SKILL.md#step-7-validate-behavior-and-maintain-admitted-evals), the portable schema validator, every claimed target validator, and bundled tests. Then use the evaluation side-effect boundary from [Planning](../SKILL.md#planning-before-creating-or-updating) and run
fresh-context activation and functional scenarios on every claimed target, including
portable fallback, isolation, and coexistence where those claims apply. Record an
unavailable gate as `unknown`; do not convert it to a pass or silently narrow the
artifact after testing.

**Done when:** every locked gate has evidence or an explicit `unknown`, and no validator result is presented as behavior proof.

### Release Step 4: Prepare Release Records

Apply [references/changelog.md](changelog.md), including its Evidence gate, in the mode that
[Step 6](../SKILL.md#step-6-record-portable-release-history) selects. State any compatibility or
migration effect without inventing rationale. Build and validate a release candidate
without presenting it as the completed release.

- **Date mode:** record each change not yet in the changelog under the date of the change.
  A date-mode skill has no version metadata.
- **Version mode:** establish the published baseline, update the skill-local changelog
  under `Unreleased`, and prepare target-owned version metadata.

**Done when:** the changelog records every change in its mode, every migration corresponds to real downstream action, and candidate validation has a result for every locked pre-install gate; in version mode, the candidate also records each net change relative to that baseline, and all metadata is ready for one proposed version while the changelog remains `Unreleased`.

### Release Step 5: Verify and Promote the Exact Artifact

Install the candidate artifact in a clean instance of each claimed surface and rerun at
least one representative scenario per real workflow branch. Compare the installed
inventory with the artifact so repository-only files cannot mask a broken package.

In date mode the candidate is the final artifact, so publish only a candidate that
passes. In version mode, if the candidate passes, assign the version and date, build the
final artifact, and repeat the clean-install inventory and representative branch checks
on that exact final artifact; if promotion or the final checks fail, return the changelog
to `Unreleased` and do not publish.

**Done when:** the final artifact itself matches the clean-install inventory on every claimed surface and exercises every supported branch without source-tree residue; otherwise nothing is published, and in version mode the changelog is `Unreleased` and no versioned release state remains.

**Done when:** the exact artifact is self-contained, every claimed target has schema and
behavior evidence, every unavailable gate is visible, and a clean installation exercises
all supported branches without relying on source-tree residue.
