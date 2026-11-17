# Portable Changelog Format

Use a skill-local `CHANGELOG.md` when a skill has releases of its own or may be distributed without its source repository. Git history is not a sufficient release record: one commit may modify several skills, and an installed or copied skill may have no Git metadata.

Keep the changelog outside `SKILL.md` so historical narration does not consume runtime context. Package it with the skill, update it in the same change as the behavior it records, and record only changes that matter to a user, integrator, or downstream maintainer. Omit it for unpublished, single-use skills until there is a real release history to preserve.

### Changelog modes

[Step 7](../SKILL.md#step-7-record-portable-release-history) reads this section before writing. Choose the mode first. Date mode is the default: entries sit under the date of the change, with no version or release bookkeeping. Version mode keeps `Unreleased` and numbered releases.

1. An explicit request for a mode wins. Switching leaves earlier sections as written.
2. An existing changelog keeps its mode, decided by its newest section: a date means
   date mode; a numbered release, or `Unreleased` beside a numbered release or a version
   signal, means version mode.
3. Otherwise look for a version signal: a version this skill ships under, such as its own
   `VERSION` file, `metadata.version`, or plugin manifest, release tags that name it, or
   the version of the one package or repository that distributes it. A sibling package's
   version is not a signal. Without one, use date mode and do not ask. With one, name it
   and ask whether to use version mode; when no one can answer, use date mode and report
   the signal.

Then record each logical change once under the [Evidence gate](#evidence-gate):

- **Date mode:** put each entry under the date of the change. Fold revisions from one day
  into that day's net change; later days add their own entries and leave earlier sections
  as written.
- **Version mode:** establish the published baseline defined below. Describe changes
  relative to that baseline: fold revisions made inside one unreleased cycle into the
  resulting contract instead of recording them as separate changes or migrations.

The mode decides how entries are grouped and what release bookkeeping applies; the entry fields and the Evidence gate are the same in both.

| | Date mode (default) | Version mode |
|---|---|---|
| Section heading | `## 2026-11-02`, the date of the change, newest first | `## [Unreleased]`, then `## [2.0.0] - 2025-11-15` |
| Revisions | Fold one day's revisions into that day's net change; later days add their own entries | Fold one release cycle's revisions into the net delta from the published baseline |
| Version metadata | None | Target-owned metadata agrees with the numbered release |

When date mode takes over an `Unreleased` section, put each entry under the day its change landed, using version-control history or file timestamps. When nothing dates an entry, use the conversion date and say so.

### Published baseline

This section applies to version mode. Date mode needs no published baseline: a dated entry states when a change was made, not that users received it.

Before writing `Unreleased`, identify the last artifact actually published to the
changelog's audience. `Unreleased` is the net difference between that artifact and the
release candidate, not a diary of commits, drafts, or revisions within the current
release cycle. A working-tree state, commit, pull request, candidate artifact, or
existing `Unreleased` entry does not prove that users received it. Establish publication
from the published artifact, a release record that identifies it, or the user's explicit
confirmation.

When no prior artifact was published, record the resulting first-release contract and
its evidenced reason. Fold all pre-release edits into that resulting capability. A
behavior that existed only in an unpublished intermediate state creates no release
transition, compatibility change, or migration.

### Evidence gate

Evidence outranks the desire to fill every field. Write a changelog claim only when it is directly supported by at least one traceable source:

- the user's explicit explanation in the current conversation or a retrievable earlier conversation;
- a requirement or specification;
- observed diff or code;
- test or log output; or
- an existing release record, limited to what that record actually says.

These sources can establish the candidate behavior and its reason. A claim that behavior
changed for released users also requires evidence for the published baseline above; an
observed diff or implementation state alone does not establish audience-visible history.

A historical conversation can establish why the user chose a separate file, boundary, or workflow even when the current request only says to implement it. Preserve that explicit reason. Do not promote an agent's plausible interpretation of the conversation into the user's rationale, and do not use the changelog entry being written as evidence for itself.

De-identification is transformation, not invention. Rename sensitive details while preserving the evidenced actors, states, sequence, and consequence. Use a minimal code, config, payload, or diff excerpt when one was observed. A reconstruction may express an explicitly described code pattern, but it must not introduce behavior or causality that the source did not establish. When only the reason is known, use concrete prose instead of manufacturing code.

If the evidence does not establish a `Why`, preserve the supported facts, report what evidence is missing, and do not claim the new entry is complete. An `Example` is optional: omit it when it would not materially improve understanding or when the evidence cannot support it. When importing legacy entries that lack enough evidence, keep their recorded facts and identify them as legacy history rather than backfilling a plausible story.

Once the evidence gate passes, include for every complete new logical change inside a release or a dated section:

- **Changed** (required): the behavior, rule, contract, or compatibility surface that changed.
- **Why** (required): the failure mode, missing invariant, or distribution constraint that made the change necessary.
- **Example** (optional): include the causal pre-change pattern and its consequence only when it makes the decision materially easier to understand than `Changed` and `Why` alone. Prefer the smallest reconstructed code, config, payload, or diff snippet that makes the missing relationship obvious; use concrete prose when code would add no clarity. Show before and after only when the contrast helps explain the decision.
- **Migration** (optional): include only when a user or downstream integrator must act
  because a supported public invocation, input, output, installation, or configuration
  contract changed. An internal implementation replacement with unchanged public
  invocation, inputs, and outputs has no Migration entry. A caller's private wrapper
  around a removed implementation detail is not migration evidence unless the existing
  contract or direct evidence identifies that wrapper as public.

Use this inclusion test: remove the proposed `Example` and reread `Changed` plus `Why`. If the causal pattern, consequence, and reason for the decision remain equally clear, omit the example.

During review, run this test against every retained `Example`, including examples outside the current diff. Existing text is not grandfathered: remove any example that no longer adds material understanding.

When included, write the heading as `Example` and de-identify its contents. Replace project, customer, ticket, repository, path, symbol, route, event, and real payload names with neutral ones. Preserve structural roles such as caller, owner, gate, optimizer, or compatibility boundary because they carry the rationale. Reconstruct the smallest faithful example instead of copying proprietary code verbatim. If a changelog contains examples, state in its preamble that they are de-identified, evidence-backed reconstructions.

An example documents what caused the change; it is not a usage demo or a mandatory restatement of the new behavior.

````markdown
# Changelog

Examples, when included, are de-identified, evidence-backed reconstructions of the patterns that motivated each change.

## [2.0.0] - 2025-11-15

### Preserve decision-relevant facts

- **Changed:** Callers now pass every distinction the owning surface may need.
- **Why:** Selecting one value early made valid states indistinguishable and prevented the owner from deciding correctly.
- **Example:**

  ```ts
  declare const candidates: Candidate[] | undefined;
  const choice = candidates?.[0] ?? null;
  owner.decide(choice);
  ```

  This reduces one or many candidates to one value and collapses both an empty result and an unavailable result to `null`.
- **Migration:** Pass the complete candidate result to the owner.
````

In version mode, use semantic versioning: Major (breaking), Minor (features, backward compatible), Patch (bug fixes).
