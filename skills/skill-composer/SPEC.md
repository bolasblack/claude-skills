# Skill Composer Specification

## Cross-Harness by Default

A skill is cross-harness by default. Its required behavior must remain executable
without host-only enhancements. Every enhancement names its host, has a tested portable
fallback, and is not the sole owner of required state or input.

A skill may depend on host-only behavior when it explicitly declares that host as a
requirement and makes no broader compatibility claim.

**Why:** The user owns the cross-harness distribution promise. Without this invariant,
a convenient host enhancement can silently become the sole owner of required behavior
while the package still appears portable.

## Bounded Entry Point

Every `SKILL.md`, Skill Composer's own included, is at most 15,000 UTF-8 bytes with its
frontmatter. It holds every standing rule (one that applies across a whole run),
must-follow gates first. A reference is a whole file holding one branch's workflow or lookup material, named
with its read condition and read in full; a pointer never targets a section anchor. One skill points to another by asking the agent
to invoke it by name, not by linking its files. Discovery text gives each invocation
branch one discriminating trigger, and within the cap every passage still earns its
place. What a script can check is scripted and not restated in prose. The rest is stated
once as a terse requirement, with at most the core reason where knowing it changes what
the agent does; detailed explanation, evidence, and history sit in a reference or
`SPEC.md` behind a link.

**Why:** On 2026-11-17 the user replaced the earlier rule that size was "a behavioral
property rather than a universal line or token limit". Text past a host's cap is lost
without warning, and only the start of a skill survives:

- The [Agent Skills specification](https://agentskills.io/specification) recommends
  "Instructions (< 5000 tokens recommended)" and "Keep your main `SKILL.md` under 500
  lines."
- Claude Code's [skill content lifecycle](https://code.claude.com/docs/en/skills.md#skill-content-lifecycle)
  states: "Claude Code re-attaches the most recent invocation of each skill after the
  summary, keeping the first 5,000 tokens of each. Re-attached skills share a combined
  budget of 25,000 tokens." Its [compaction table](https://code.claude.com/docs/en/context-window.md#what-survives-compaction)
  re-reads only up to five recently read files and gives a file over 5,000 tokens back
  as a path only, so a standing rule kept in a reference can disappear. Claude Code
  records only Skill tool and slash-command invocations for re-attachment (verified in
  the 2.1.326 binary), so a skill reached by reading its `SKILL.md` as a file is not
  re-attached after compaction.
- In four scheduled cloud runs, agents reached a skill through a Markdown link to a
  section of its `SKILL.md` and read it with `head`, `sed`, or `grep` in place of
  invoking it. The 2026-11-17 run read only `/^## Step 1/,/^## Step 3/`, never saw the
  instruction written above Step 1, and marked a pull request ready without the check
  the skill requires before that step.

The user stated the scripting and terseness rule on 2026-11-18 after finding Skill
Composer's own `SKILL.md` wordy. Mechanical rules restated in prose cost context on
every invocation and were still not followed: the package check, on its first runs,
found about ten real violations across two repositories that the prose rules had not
prevented.

Both documents were read in full on 2026-11-17, with Claude Code 2.1.326 installed. The
cap is in bytes because no local tokenizer is available. English prose runs about 3.5 to
4.5 bytes per token, so 15,000 bytes stays under 5,000 tokens. Text that is mostly CJK
may use more tokens per byte, and its margin has not been measured.

## Environment-Native Automation

Repeated, deterministic work with a stable public boundary belongs in tested executable
helpers when that reduces agent reinterpretation; judgment remains in instructions and
executable changes follow TDD.

Language and dependency choices follow the supported environment and minimize total
installation, implementation, maintenance, and supply-chain cost. Portability is not
defined by one language or zero dependencies; this preserves deterministic behavior
without making environment-specific skills less compatible or more complex.

Skill Composer ships one mechanical package check, `scripts/check-skill.py`, and runs it
on every skill it creates, updates, reviews, or releases. A rule it sets that a script
can check is enforced there, from one copy inside Skill Composer, not as tests copied
into each skill and not as prose alone.

**Why:** Manual reinterpretation lets stable mechanics drift, while a universal Python
or zero-dependency rule can add more machinery than it removes. The user requires the
automation decision to follow the actual environment and public behavior seam. On
2026-11-18 the user asked for the rules Skill Composer sets to be verified automatically
on every skill it maintains, so a rule added later that a script can check belongs in
the check.

## Bundled Core Rules

Skill Composer carries its own core writing rules (`references/writing.md`) and
red-green loop (`references/package-layout.md`), so the quality of what it writes
does not depend on a sibling skill being installed or staying unchanged. When the
fuller sibling skill (`writing-for-agents`, `tdd`) is available, it replaces the bundled
rules instead of adding to them, so context is not spent twice. The bundled rules stay a
short core, not a copy of the sibling.

**Why:** On 2026-11-18 the user decided that a third-party skill must not carry Skill
Composer's writing quality: most installations lack `writing-for-agents`, the earlier
fallback was half a sentence, and third-party skill content is outside Skill Composer's
control.

## Package-Local Maintenance Context

Most skills have no `SPEC.md`. The file exists only when explicit, stable requirements
must constrain future rewrites but ordinary execution does not need them. It records
those current requirements and why each must survive. Runtime principles and workflows
remain in `SKILL.md`; this rare separation keeps maintainer-only context available
without loading it on ordinary invocations or duplicating the runtime contract.

A skill with releases of its own or independent distribution carries an evidence-backed
`CHANGELOG.md` recording what changed and why. It stays outside `SKILL.md` because
history is not a runtime instruction, and inside the package because repository history,
a multi-skill commit, or one platform's version identifier may not travel with the
skill. An unpublished, single-use skill carries neither an empty changelog nor a release
record it does not have.

Changelogs default to date mode: each entry sits under the date of its change, with no
version or release bookkeeping. Version mode is a choice: an existing changelog keeps its
mode, and a skill that ships under a version asks before choosing it.

**Why:** The user requires maintainer constraints and release rationale to survive when
a skill is rewritten or leaves its repository, without making ordinary invocations pay
for maintenance-only context or duplicating the runtime contract. The user finds version
numbers unnecessary in their way of working and expects the same for many others, so
dates are the default and versions are opted into.
